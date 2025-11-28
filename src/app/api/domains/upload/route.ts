import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { detectContactPage } from "@/lib/contact-page-detector";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { urls, categories, category, isActive } = body;

    if (!Array.isArray(urls) || urls.length === 0) {
      return NextResponse.json({ detail: "URLs array is required." }, { status: 400 });
    }

    const results = {
      created: 0,
      skipped: 0,
      errors: [] as string[],
      contactCheckResults: {
        checked: 0,
        found: 0,
        notFound: 0,
        noForm: 0,
        errors: 0,
      },
      createdDomainIds: [] as number[],
    };

    // Support both single category and array of categories
    const categoryArray = categories && Array.isArray(categories) ? categories : null;
    const defaultCategory = category || null;

    for (let i = 0; i < urls.length; i++) {
      const url = urls[i];
      if (!url || typeof url !== "string") {
        results.skipped++;
        results.errors.push(`Invalid URL: ${url}`);
        continue;
      }

      // Validate URL format
      try {
        new URL(url);
      } catch {
        results.skipped++;
        results.errors.push(`Invalid URL format: ${url}`);
        continue;
      }

      // Get category for this URL (from array if provided, otherwise use default)
      const urlCategory = categoryArray && categoryArray[i] ? categoryArray[i] : defaultCategory;

      try {
        const domain = await prisma.domain.create({
          data: {
            url: url.trim(),
            category: urlCategory || null,
            isActive: isActive !== undefined ? isActive : true,
            contactCheckStatus: "pending",
          },
        });
        results.created++;
        results.createdDomainIds.push(domain.id);

        // Check contact page in background (don't wait for it)
        // Add a small delay to avoid rate limiting (stagger the requests)
        const delay = i * 500; // 500ms delay between each domain check
        setTimeout(() => {
          detectContactPage(domain.url)
          .then(async (checkResult) => {
            try {
              await prisma.domain.update({
                where: { id: domain.id },
                data: {
                  contactPageUrl: checkResult.contactUrl,
                  contactCheckStatus: checkResult.status,
                  contactCheckedAt: new Date(),
                },
              });

              await prisma.contactCheck.create({
                data: {
                  domainId: domain.id,
                  status: checkResult.status,
                  contactUrl: checkResult.contactUrl,
                  message: checkResult.message,
                },
              });
            } catch (dbError) {
              console.error(`Database error updating domain ${domain.id}:`, dbError);
            }
          })
          .catch(async (error) => {
            console.error(`Error checking contact page for ${domain.url}:`, error.message || error);
            // Update domain with error status
            try {
              await prisma.domain.update({
                where: { id: domain.id },
                data: {
                  contactCheckStatus: "error",
                  contactCheckedAt: new Date(),
                },
              });

              await prisma.contactCheck.create({
                data: {
                  domainId: domain.id,
                  status: "error",
                  contactUrl: null,
                  message: error.message || "Unknown error during contact page check",
                },
              });
            } catch (dbError) {
              console.error(`Failed to update error status for domain ${domain.id}:`, dbError);
            }
          });
        }, delay);
      } catch (error: any) {
        if (error.code === "P2002") {
          results.skipped++;
          results.errors.push(`Domain already exists: ${url}`);
        } else {
          results.skipped++;
          results.errors.push(`Error creating domain ${url}: ${(error as Error).message}`);
        }
      }
    }

    return NextResponse.json({
      message: `Processed ${urls.length} URLs. Created: ${results.created}, Skipped: ${results.skipped}. Contact page checking is in progress.`,
      ...results,
    });
  } catch (error) {
    return NextResponse.json(
      { detail: (error as Error).message ?? "Unable to upload domains." },
      { status: 500 }
    );
  }
}

