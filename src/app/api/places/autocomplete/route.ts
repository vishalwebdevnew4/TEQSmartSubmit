import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const input = searchParams.get("input");

    if (!input || input.trim().length < 2) {
      return NextResponse.json({ predictions: [] });
    }

    const apiKey = process.env.GOOGLE_PLACES_API_KEY;
    if (!apiKey) {
      return NextResponse.json(
        { error: "Google Places API key not configured" },
        { status: 500 }
      );
    }

    // Call Google Places Autocomplete API
    // Use components parameter to restrict to countries if needed, but don't restrict types
    // This allows cities, addresses, establishments, and regions
    const url = `https://maps.googleapis.com/maps/api/place/autocomplete/json?input=${encodeURIComponent(input)}&key=${apiKey}&language=en`;
    
    const response = await fetch(url);
    const data = await response.json();

    // Log for debugging
    console.log("Google Places Autocomplete response:", {
      status: data.status,
      predictionsCount: data.predictions?.length || 0,
      error: data.error_message
    });

    if (data.status !== "OK" && data.status !== "ZERO_RESULTS") {
      console.error("Google Places Autocomplete error:", data.status, data.error_message || "");
      return NextResponse.json({ 
        predictions: [],
        error: data.error_message || data.status,
        status: data.status
      });
    }

    // Format predictions
    const predictions = (data.predictions || []).map((pred: any) => ({
      description: pred.description,
      placeId: pred.place_id,
      structuredFormatting: pred.structured_formatting,
    }));

    return NextResponse.json({ predictions });
  } catch (error: any) {
    console.error("Error fetching autocomplete:", error);
    return NextResponse.json(
      { error: error.message || "Failed to fetch autocomplete" },
      { status: 500 }
    );
  }
}

