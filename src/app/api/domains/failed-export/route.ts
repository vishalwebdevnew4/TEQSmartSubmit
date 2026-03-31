import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function GET(req: NextRequest) {
  try {
    const { searchParams } = new URL(req.url);
    const status = searchParams.get("status") || "not_found"; // "not_found" or "no_form" or "error"

    // Get failed domains
    const domains = await prisma.domain.findMany({
      where: {
        contactCheckStatus: status,
      },
      select: {
        url: true,
        category: true,
        contactPageUrl: true,
        contactCheckStatus: true,
        contactCheckedAt: true,
      },
      orderBy: {
        createdAt: "desc",
      },
    });

    // Generate CSV
    const headers = ["URL", "Category", "Contact Page URL", "Status", "Checked At"];
    const rows = domains.map((domain) => [
      domain.url,
      domain.category || "",
      domain.contactPageUrl || "",
      domain.contactCheckStatus || "",
      domain.contactCheckedAt?.toISOString() || "",
    ]);

    const csvContent = [
      headers.join(","),
      ...rows.map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(",")),
    ].join("\n");

    return new NextResponse(csvContent, {
      headers: {
        "Content-Type": "text/csv",
        "Content-Disposition": `attachment; filename="failed-domains-${status}-${new Date().toISOString().split("T")[0]}.csv"`,
      },
    });
  } catch (error) {
    return NextResponse.json(
      { detail: (error as Error).message ?? "Unable to export failed domains." },
      { status: 500 }
    );
  }
}

