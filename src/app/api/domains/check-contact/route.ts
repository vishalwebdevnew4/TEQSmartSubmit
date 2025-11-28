import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { detectContactPage } from "@/lib/contact-page-detector";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { domainIds, urls } = body;

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
    };

    // Check each domain
    for (const domain of domainsToCheck) {
      try {
        const checkResult = await detectContactPage(domain.url);

        results.checked++;

        if (checkResult.status === "found") {
          results.found++;
        } else if (checkResult.status === "not_found") {
          results.notFound++;
        } else if (checkResult.status === "no_form") {
          results.noForm++;
        } else {
          results.errors++;
        }

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

        results.details.push({
          domainId: domain.id,
          url: domain.url,
          status: checkResult.status,
          contactUrl: checkResult.contactUrl,
          message: checkResult.message,
        });
      } catch (error: any) {
        results.errors++;
        results.details.push({
          domainId: domain.id,
          url: domain.url,
          status: "error",
          contactUrl: null,
          message: error.message || "Unknown error",
        });
      }
    }

    return NextResponse.json({
      message: `Checked ${results.checked} domains. Found: ${results.found}, Not Found: ${results.notFound}, No Form: ${results.noForm}, Errors: ${results.errors}`,
      ...results,
    });
  } catch (error) {
    return NextResponse.json(
      { detail: (error as Error).message ?? "Unable to check contact pages." },
      { status: 500 }
    );
  }
}

