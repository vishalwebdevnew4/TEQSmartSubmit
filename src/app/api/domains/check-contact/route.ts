import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { detectContactPage } from "@/lib/contact-page-detector";

// Allow longer execution time for contact checks (5 minutes)
export const maxDuration = 300;
export const runtime = "nodejs";

// Configuration for load balancing
const BATCH_SIZE = parseInt(process.env.CONTACT_CHECK_BATCH_SIZE || "10"); // Process 10 domains per batch
const DELAY_BETWEEN_BATCHES_MS = parseInt(process.env.CONTACT_CHECK_BATCH_DELAY || "2000"); // 2 seconds between batches
const CONCURRENT_CHECKS = parseInt(process.env.CONTACT_CHECK_CONCURRENT || "3"); // Max 3 concurrent checks per batch
const DELAY_BETWEEN_CHECKS_MS = parseInt(process.env.CONTACT_CHECK_DELAY || "500"); // 500ms between individual checks

// Helper function to sleep/delay
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Helper function to process a single domain check
async function processDomainCheck(domain: { id?: number; url: string }) {
  try {
    const checkResult = await detectContactPage(domain.url);

    // Update domain in database if we have an ID
    if (domain.id) {
      await prisma.domain.update({
        where: { id: domain.id },
        data: {
          contactPageUrl: checkResult.contactUrl,
          contactCheckStatus: checkResult.status,
          contactCheckedAt: new Date(),
        },
      });

      // Log the check
      await prisma.contactCheck.create({
        data: {
          domainId: domain.id,
          status: checkResult.status,
          contactUrl: checkResult.contactUrl,
          message: checkResult.message,
        },
      });
    }

    return {
      domainId: domain.id,
      url: domain.url,
      status: checkResult.status,
      contactUrl: checkResult.contactUrl,
      message: checkResult.message,
      success: true,
    };
  } catch (error: any) {
    return {
      domainId: domain.id,
      url: domain.url,
      status: "error",
      contactUrl: null,
      message: error.message || "Unknown error",
      success: false,
    };
  }
}

// Process a batch of domains with concurrency control
async function processBatch(
  batch: Array<{ id?: number; url: string }>,
  batchIndex: number,
  totalBatches: number,
  maxConcurrent: number
): Promise<Array<{ domainId?: number; url: string; status: string; contactUrl: string | null; message: string; success: boolean }>> {
  console.log(`[ContactCheck] Processing batch ${batchIndex + 1}/${totalBatches} (${batch.length} domains)`);
  
  const results: Array<{ domainId?: number; url: string; status: string; contactUrl: string | null; message: string; success: boolean }> = [];
  
  // Process domains in chunks with concurrency limit
  for (let i = 0; i < batch.length; i += maxConcurrent) {
    const chunk = batch.slice(i, i + maxConcurrent);
    
    // Process chunk concurrently
    const chunkPromises = chunk.map(async (domain, chunkIndex) => {
      // Add small delay between checks to avoid overwhelming the server
      if (i + chunkIndex > 0) {
        await sleep(DELAY_BETWEEN_CHECKS_MS);
      }
      
      return await processDomainCheck(domain);
    });
    
    const chunkResults = await Promise.all(chunkPromises);
    results.push(...chunkResults);
    
    // Small delay between chunks within the batch
    if (i + maxConcurrent < batch.length) {
      await sleep(DELAY_BETWEEN_CHECKS_MS);
    }
  }
  
  return results;
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { domainIds, urls, batchSize, batchDelay, concurrent } = body;

    // Support both domain IDs and URLs
    let domainsToCheck: Array<{ id?: number; url: string }> = [];

    if (domainIds && Array.isArray(domainIds)) {
      const domains = await prisma.domain.findMany({
        where: { id: { in: domainIds.map((id: any) => parseInt(id)) } },
        select: { id: true, url: true },
      });
      domainsToCheck = domains.map((d) => ({ id: d.id, url: d.url }));
    } else if (urls && Array.isArray(urls)) {
      domainsToCheck = urls.map((url: string) => ({ url }));
    } else {
      return NextResponse.json({ detail: "domainIds or urls array is required." }, { status: 400 });
    }

    // For single domain checks, process synchronously and return results
    // For multiple domains, process in background to prevent timeout
    if (domainsToCheck.length === 1) {
      console.log(`[ContactCheck] Processing single domain synchronously: ${domainsToCheck[0].url}`);
      const result = await processDomainCheck(domainsToCheck[0]);
      
      return NextResponse.json({
        status: result.status,
        message: result.success 
          ? `Contact check completed: ${result.message}` 
          : `Contact check failed: ${result.message}`,
        domainId: result.domainId,
        url: result.url,
        contactUrl: result.contactUrl,
        contactCheckStatus: result.status,
        success: result.success,
      });
    } else {
      // For multiple domains, process in background
      console.log(`[ContactCheck] Processing ${domainsToCheck.length} domains in background`);
      
      // Return immediately and process in background to prevent timeout
      (async () => {
        try {
          await processContactChecksInBackground(
            domainsToCheck,
            batchSize,
            batchDelay,
            concurrent
          );
        } catch (error) {
          console.error("[ContactCheck] Background processing error:", error);
        }
      })();

      // Return immediately with 202 Accepted
      return NextResponse.json({
        status: "processing",
        message: `Contact check started for ${domainsToCheck.length} domain(s). Processing in background...`,
        totalDomains: domainsToCheck.length,
      }, { status: 202 }); // 202 Accepted - request accepted but processing asynchronously
    }
  } catch (error) {
    console.error("[ContactCheck] Error:", error);
    return NextResponse.json(
      { detail: (error as Error).message ?? "Unable to start contact page checks." },
      { status: 500 }
    );
  }
}

// Background processing function
async function processContactChecksInBackground(
  domainsToCheck: Array<{ id?: number; url: string }>,
  batchSize?: number,
  batchDelay?: number,
  concurrent?: number
) {
  try {

    // Use custom batch size if provided, otherwise use default
    const effectiveBatchSize = batchSize && batchSize > 0 ? Math.min(batchSize, 50) : BATCH_SIZE;
    const effectiveBatchDelay = batchDelay && batchDelay >= 0 ? batchDelay : DELAY_BETWEEN_BATCHES_MS;
    const effectiveConcurrent = concurrent && concurrent > 0 ? Math.min(concurrent, 10) : CONCURRENT_CHECKS;

    // Auto-split large requests into chunks to prevent timeout
    const MAX_DOMAINS_PER_CHUNK = 1000;
    const totalDomains = domainsToCheck.length;
    const needsAutoSplit = totalDomains > MAX_DOMAINS_PER_CHUNK;
    
    console.log(`[ContactCheck] Background processing started for ${totalDomains} domains`);
    if (needsAutoSplit) {
      console.log(`[ContactCheck] Auto-splitting ${totalDomains} domains into chunks of ${MAX_DOMAINS_PER_CHUNK}`);
    }
    console.log(`[ContactCheck] Batch size: ${effectiveBatchSize}, Delay: ${effectiveBatchDelay}ms, Concurrent: ${effectiveConcurrent}`);

    const results = {
      checked: 0,
      found: 0,
      notFound: 0,
      noForm: 0,
      errors: 0,
      details: [] as Array<{
        domainId?: number;
        url: string;
        status: string;
        contactUrl: string | null;
        message: string;
      }>,
      batchesProcessed: 0,
      totalBatches: 0,
      chunksProcessed: 0,
      totalChunks: needsAutoSplit ? Math.ceil(totalDomains / MAX_DOMAINS_PER_CHUNK) : 1,
    };

    // Auto-split into chunks if needed
    const chunks: Array<Array<{ id?: number; url: string }>> = [];
    if (needsAutoSplit) {
      for (let i = 0; i < domainsToCheck.length; i += MAX_DOMAINS_PER_CHUNK) {
        chunks.push(domainsToCheck.slice(i, i + MAX_DOMAINS_PER_CHUNK));
      }
    } else {
      chunks.push(domainsToCheck);
    }

    console.log(`[ContactCheck] Processing ${chunks.length} chunk(s) of domains`);

    // Process each chunk
    for (let chunkIndex = 0; chunkIndex < chunks.length; chunkIndex++) {
      const chunk = chunks[chunkIndex];
      console.log(`[ContactCheck] Processing chunk ${chunkIndex + 1}/${chunks.length} (${chunk.length} domains)`);

      // Split chunk into processing batches
      const batches: Array<Array<{ id?: number; url: string }>> = [];
      for (let i = 0; i < chunk.length; i += effectiveBatchSize) {
        batches.push(chunk.slice(i, i + effectiveBatchSize));
      }

      results.totalBatches += batches.length;
      console.log(`[ContactCheck] Chunk ${chunkIndex + 1} split into ${batches.length} batches`);

      // Process each batch within the chunk
      for (let batchIndex = 0; batchIndex < batches.length; batchIndex++) {
        const batch = batches[batchIndex];
        const globalBatchIndex = results.batchesProcessed;
        
        // Process the batch
        const batchResults = await processBatch(batch, globalBatchIndex, results.totalBatches, effectiveConcurrent);
        
        // Update results
        for (const result of batchResults) {
          results.checked++;
          
          if (result.status === "found") {
            results.found++;
          } else if (result.status === "not_found") {
            results.notFound++;
          } else if (result.status === "no_form") {
            results.noForm++;
          } else {
            results.errors++;
          }

          results.details.push({
            domainId: result.domainId,
            url: result.url,
            status: result.status,
            contactUrl: result.contactUrl,
            message: result.message,
          });
        }
        
        results.batchesProcessed++;
        
        // Add delay between batches (except for the last batch in chunk)
        if (batchIndex < batches.length - 1) {
          console.log(`[ContactCheck] Batch ${globalBatchIndex + 1}/${results.totalBatches} completed. Waiting ${effectiveBatchDelay}ms before next batch...`);
          await sleep(effectiveBatchDelay);
        }
      }
      
      results.chunksProcessed = chunkIndex + 1;
      
      // Add longer delay between chunks (except for the last chunk)
      if (chunkIndex < chunks.length - 1) {
        const chunkDelay = effectiveBatchDelay * 3; // 3x delay between chunks
        console.log(`[ContactCheck] Chunk ${chunkIndex + 1}/${chunks.length} completed. Waiting ${chunkDelay}ms before next chunk...`);
        await sleep(chunkDelay);
      }
    }

    console.log(`[ContactCheck] Background processing completed: ${results.checked} domains checked`);
    console.log(`[ContactCheck] Results - Found: ${results.found}, Not Found: ${results.notFound}, No Form: ${results.noForm}, Errors: ${results.errors}`);
    
  } catch (error) {
    console.error("[ContactCheck] Background processing error:", error);
  }
}

