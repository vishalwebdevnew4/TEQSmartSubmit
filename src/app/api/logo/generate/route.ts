import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

/**
 * Generate logo for business
 * TODO: Integrate with actual logo generation API (DALL-E, Midjourney, LogoMaker API, etc.)
 */
export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const name = searchParams.get("name") || "Business";
    const category = searchParams.get("category") || "business";

    // For now, return a placeholder SVG logo
    // In production, integrate with:
    // - DALL-E API for logo generation
    // - Midjourney API
    // - LogoMaker API
    // - Or use a logo generation service

    const logo = generatePlaceholderLogo(name, category);

    return new NextResponse(logo, {
      headers: {
        "Content-Type": "image/svg+xml",
        "Cache-Control": "public, max-age=31536000",
      },
    });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message || "Failed to generate logo" },
      { status: 500 }
    );
  }
}

/**
 * Generate placeholder SVG logo
 * TODO: Replace with actual AI-generated logo
 */
function generatePlaceholderLogo(name: string, category: string): string {
  const initials = name
    .split(" ")
    .map((word) => word[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  const colors: Record<string, string> = {
    restaurant: "#FF6B6B",
    cafe: "#4ECDC4",
    hotel: "#45B7D1",
    bakery: "#FFA07A",
    business: "#6C5CE7",
  };

  const color = colors[category.toLowerCase()] || colors.business;

  return `<?xml version="1.0" encoding="UTF-8"?>
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:${color};stop-opacity:1" />
      <stop offset="100%" style="stop-color:${color}dd;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="200" height="200" rx="20" fill="url(#grad)"/>
  <text x="100" y="120" font-family="Arial, sans-serif" font-size="60" font-weight="bold" 
        fill="white" text-anchor="middle" dominant-baseline="middle">${initials}</text>
</svg>`;
}

