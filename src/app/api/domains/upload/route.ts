import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { detectContactPage } from "@/lib/contact-page-detector";

const DOMAIN_CHECK_TIMEOUT_MS = parseInt(process.env.CONTACT_CHECK_TIMEOUT_MS || "45000");

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const {
      urls,
      categories,
      category,
      messages,
      isActive,
      isActiveValues,
      contactPageUrls,
      contactCheckStatuses,
      contactCheckMessages,
      createdAtValues,
      templateNames,
    } = body;

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
      templateLinks: {
        linked: 0,
        missing: 0,
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
      
      // Get custom message for this URL (from array if provided)
      const customMessage = messages && Array.isArray(messages) && messages[i] ? String(messages[i]).trim() : null;
      const rowIsActive = Array.isArray(isActiveValues) && i < isActiveValues.length
        ? Boolean(isActiveValues[i])
        : (isActive !== undefined ? Boolean(isActive) : true);
      const rowContactPageUrl = Array.isArray(contactPageUrls) && contactPageUrls[i] ? String(contactPageUrls[i]).trim() : null;
      const rowContactCheckStatus = Array.isArray(contactCheckStatuses) && contactCheckStatuses[i]
        ? String(contactCheckStatuses[i]).trim()
        : null;
      const rowContactCheckMessage = Array.isArray(contactCheckMessages) && contactCheckMessages[i]
        ? String(contactCheckMessages[i]).trim()
        : null;
      const rowCreatedAt = Array.isArray(createdAtValues) && createdAtValues[i]
        ? new Date(createdAtValues[i])
        : null;
      const rowTemplateNames = Array.isArray(templateNames) && Array.isArray(templateNames[i])
        ? templateNames[i].map((name: unknown) => String(name).trim()).filter(Boolean)
        : [];
      const shouldPreserveImportedContactState = Boolean(rowContactPageUrl || rowContactCheckStatus || rowContactCheckMessage);

      try {
        const domain = await prisma.domain.create({
          data: {
            url: url.trim(),
            category: urlCategory || null,
            customMessage: customMessage,
            isActive: rowIsActive,
            contactPageUrl: rowContactPageUrl,
            contactCheckStatus: rowContactCheckStatus || "pending",
            createdAt: rowCreatedAt && !Number.isNaN(rowCreatedAt.getTime()) ? rowCreatedAt : undefined,
          },
        });
        results.created++;
        results.createdDomainIds.push(domain.id);

        if (rowTemplateNames.length > 0) {
          const existingTemplates = await prisma.template.findMany({
            where: {
              name: {
                in: rowTemplateNames,
              },
            },
            select: {
              id: true,
              name: true,
            },
          });

          if (existingTemplates.length > 0) {
            const matchedNames = existingTemplates.map((template) => template.name);
            const updateResult = await prisma.template.updateMany({
              where: {
                id: {
                  in: existingTemplates.map((template) => template.id),
                },
              },
              data: {
                domainId: domain.id,
              },
            });
            results.templateLinks.linked += updateResult.count;
            results.templateLinks.missing += rowTemplateNames.filter((name) => !matchedNames.includes(name)).length;
          } else {
            results.templateLinks.missing += rowTemplateNames.length;
          }
        }

        if (shouldPreserveImportedContactState) {
          results.contactCheckResults.checked++;
          if (rowContactCheckStatus === "found") results.contactCheckResults.found++;
          else if (rowContactCheckStatus === "not_found") results.contactCheckResults.notFound++;
          else if (rowContactCheckStatus === "no_form") results.contactCheckResults.noForm++;
          else if (rowContactCheckStatus === "error") results.contactCheckResults.errors++;

          if (rowContactCheckStatus) {
            await prisma.contactCheck.create({
              data: {
                domainId: domain.id,
                status: rowContactCheckStatus,
                contactUrl: rowContactPageUrl,
                message: rowContactCheckMessage,
                checkedAt: rowCreatedAt && !Number.isNaN(rowCreatedAt.getTime()) ? rowCreatedAt : new Date(),
              },
            });
          }
        } else {
          // Check contact page in background (don't wait for it)
          // Add a small delay to avoid rate limiting (stagger the requests)
          const delay = i * 500; // 500ms delay between each domain check
          setTimeout(() => {
            Promise.race([
              detectContactPage(domain.url),
              new Promise<never>((_, reject) =>
                setTimeout(() => reject(new Error(`Contact check timed out after ${DOMAIN_CHECK_TIMEOUT_MS}ms`)), DOMAIN_CHECK_TIMEOUT_MS)
              ),
            ])
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
        }
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
      message: `Processed ${urls.length} URLs. Created: ${results.created}, Skipped: ${results.skipped}. ` +
        (results.templateLinks.linked > 0 || results.templateLinks.missing > 0
          ? `Templates linked: ${results.templateLinks.linked}, missing template matches: ${results.templateLinks.missing}. `
          : "") +
        `Contact page checking is in progress for rows without imported contact data.`,
      ...results,
    });
  } catch (error) {
    return NextResponse.json(
      { detail: (error as Error).message ?? "Unable to upload domains." },
      { status: 500 }
    );
  }
}
