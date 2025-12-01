import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const input = searchParams.get("input");

    if (!input || input.trim().length < 2) {
      return NextResponse.json({ predictions: [] });
    }

    // Use OpenStreetMap Nominatim API (100% free, no API key needed!)
    // Using proper parameters for better results
    const query = encodeURIComponent(input.trim());
    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${query}&limit=10&addressdetails=1&extratags=1&namedetails=1`;
    
    // Make request with proper headers (server-side, so no CORS issues)
    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'User-Agent': 'TEQSmartSubmit/1.0', // Required by Nominatim
        'Accept': 'application/json',
        'Accept-Language': 'en',
      },
      // Add cache control to help with rate limits
      cache: 'no-store'
    });
    
    // Check response status
    if (!response.ok) {
      console.error('OpenStreetMap API error:', response.status, response.statusText);
      return NextResponse.json({ 
        predictions: [],
        error: `API returned status ${response.status}`
      });
    }
    
    // Get response text first to check if it's JSON
    const responseText = await response.text();
    
    // Check if response is HTML (error page)
    if (responseText.trim().startsWith('<')) {
      console.error('OpenStreetMap API returned HTML:', responseText.substring(0, 200));
      return NextResponse.json({ 
        predictions: [],
        error: 'API returned HTML instead of JSON. This might be a rate limit issue.'
      });
    }
    
    // Parse JSON
    let data;
    try {
      data = JSON.parse(responseText);
    } catch (parseError) {
      console.error('Failed to parse JSON:', parseError);
      return NextResponse.json({ 
        predictions: [],
        error: 'Invalid JSON response from API'
      });
    }

    // Format predictions to match Google Places format
    const predictions = (data || []).map((item: any) => {
      // Build location description
      const parts = [];
      if (item.name) parts.push(item.name);
      if (item.address) {
        if (item.address.city || item.address.town || item.address.village) {
          parts.push(item.address.city || item.address.town || item.address.village);
        }
        if (item.address.state) parts.push(item.address.state);
        if (item.address.country) parts.push(item.address.country);
      }
      
      const description = parts.length > 0 
        ? parts.join(', ') 
        : item.display_name || item.name || '';

      return {
        description,
        placeId: item.place_id?.toString() || item.osm_id?.toString() || '',
        structuredFormatting: {
          main_text: item.name || item.display_name?.split(',')[0] || '',
          secondary_text: item.display_name?.split(',').slice(1).join(',').trim() || ''
        },
        // Store full data for reference
        rawData: item
      };
    });

    return NextResponse.json({ predictions });
  } catch (error: any) {
    console.error("Error fetching free autocomplete:", error);
    return NextResponse.json(
      { error: error.message || "Failed to fetch autocomplete" },
      { status: 500 }
    );
  }
}

