/**
 * Script to re-check all domains with error status
 * This will use the improved contact page detector to re-check all error domains
 */

import { PrismaClient } from '@prisma/client';
import { detectContactPage } from '../src/lib/contact-page-detector';

const prisma = new PrismaClient();

async function recheckErrorDomains() {
  try {
    // Get all domains with error status
    const errorDomains = await prisma.domain.findMany({
      where: {
        contactCheckStatus: 'error',
      },
      select: {
        id: true,
        url: true,
      },
      orderBy: {
        id: 'asc',
      },
    });

    console.log(`Found ${errorDomains.length} domains with error status`);
    console.log('Starting re-check process...\n');

    let successCount = 0;
    let stillErrorCount = 0;
    let foundCount = 0;
    let notFoundCount = 0;
    let noFormCount = 0;

    // Process in batches to avoid overwhelming the system
    const batchSize = 10;
    const delayBetweenBatches = 5000; // 5 seconds between batches

    for (let i = 0; i < errorDomains.length; i += batchSize) {
      const batch = errorDomains.slice(i, i + batchSize);
      const batchNumber = Math.floor(i / batchSize) + 1;
      const totalBatches = Math.ceil(errorDomains.length / batchSize);

      console.log(`\nProcessing batch ${batchNumber}/${totalBatches} (${batch.length} domains)...`);

      const batchPromises = batch.map(async (domain) => {
        try {
          console.log(`  Checking: ${domain.url}`);
          const checkResult = await detectContactPage(domain.url);

          // Update domain in database
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

          // Update counters
          if (checkResult.status === 'found') {
            foundCount++;
            successCount++;
            console.log(`    ✅ Found: ${checkResult.contactUrl}`);
          } else if (checkResult.status === 'not_found') {
            notFoundCount++;
            console.log(`    ⚠️  Not found: ${checkResult.message}`);
          } else if (checkResult.status === 'no_form') {
            noFormCount++;
            console.log(`    ⚠️  No form: ${checkResult.message}`);
          } else if (checkResult.status === 'error') {
            stillErrorCount++;
            console.log(`    ❌ Still error: ${checkResult.message}`);
          }

          // Small delay between individual checks
          await new Promise(resolve => setTimeout(resolve, 1000));
        } catch (error: any) {
          stillErrorCount++;
          console.error(`    ❌ Error checking ${domain.url}: ${error.message}`);
          
          // Update domain with error status
          try {
            await prisma.domain.update({
              where: { id: domain.id },
              data: {
                contactCheckStatus: 'error',
                contactCheckedAt: new Date(),
              },
            });

            await prisma.contactCheck.create({
              data: {
                domainId: domain.id,
                status: 'error',
                contactUrl: null,
                message: error.message || 'Unknown error during contact page check',
              },
            });
          } catch (dbError) {
            console.error(`    Failed to update error status for domain ${domain.id}: ${dbError}`);
          }
        }
      });

      await Promise.all(batchPromises);

      // Delay between batches (except for the last batch)
      if (i + batchSize < errorDomains.length) {
        console.log(`\nWaiting ${delayBetweenBatches / 1000} seconds before next batch...`);
        await new Promise(resolve => setTimeout(resolve, delayBetweenBatches));
      }
    }

    // Print summary
    console.log('\n' + '='.repeat(60));
    console.log('RE-CHECK SUMMARY');
    console.log('='.repeat(60));
    console.log(`Total domains checked: ${errorDomains.length}`);
    console.log(`✅ Found (with form): ${foundCount}`);
    console.log(`⚠️  Not found: ${notFoundCount}`);
    console.log(`⚠️  No form: ${noFormCount}`);
    console.log(`❌ Still error: ${stillErrorCount}`);
    console.log(`✅ Success rate: ${((successCount / errorDomains.length) * 100).toFixed(1)}%`);
    console.log('='.repeat(60));

  } catch (error) {
    console.error('Fatal error:', error);
    process.exit(1);
  } finally {
    await prisma.$disconnect();
  }
}

// Run the script
recheckErrorDomains()
  .then(() => {
    console.log('\nRe-check process completed!');
    process.exit(0);
  })
  .catch((error) => {
    console.error('Script failed:', error);
    process.exit(1);
  });



