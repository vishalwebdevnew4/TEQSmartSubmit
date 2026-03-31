import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  try {
    // Generate sample CSV content with message column
    const sampleData = [
      ["url", "category", "isActive", "message"],
      ["https://example.com", "Technology", "true", "I am interested in your technology services"],
      ["https://example-agency.com", "Marketing", "true", "Can you help with marketing strategy?"],
      ["https://example-design.com", "Design", "true", "We need professional design services"],
      ["https://example-consulting.com", "Consulting", "false", "Consulting inquiry for our company"],
      ["https://example-ecommerce.com", "E-commerce", "true", "Looking for e-commerce solutions"],
      ["https://example-saas.com", "SaaS", "true", "Interested in your SaaS platform"],
      ["https://example-blog.com", "Media", "true", "Media partnership inquiry"],
      ["https://example-service.com", "Services", "true", "Request for service information"],
    ];

    // Convert to CSV format
    const csvContent = sampleData.map(row => 
      row.map(cell => {
        // Escape quotes and wrap in quotes if needed
        if (typeof cell === "string" && (cell.includes(",") || cell.includes('"') || cell.includes("\n"))) {
          return `"${cell.replace(/"/g, '""')}"`;
        }
        return cell;
      }).join(",")
    ).join("\n");

    // Return as CSV file
    return new NextResponse(csvContent, {
      status: 200,
      headers: {
        "Content-Type": "text/csv; charset=utf-8",
        "Content-Disposition": 'attachment; filename="domains_sample.csv"',
      },
    });
  } catch (error) {
    console.error("Failed to generate sample CSV:", error);
    return NextResponse.json(
      { error: "Failed to generate sample CSV" },
      { status: 500 }
    );
  }
}
