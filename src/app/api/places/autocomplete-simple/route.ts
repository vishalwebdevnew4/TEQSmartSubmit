import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const input = searchParams.get("input");

    if (!input || input.trim().length < 2) {
      return NextResponse.json({ predictions: [] });
    }

    // Simple location suggestions based on common patterns
    // This is a fallback that works without any external API
    const commonLocations: { [key: string]: string[] } = {
      'mohali': ['Mohali, Punjab, India', 'Mohali, India', 'Mohali, Chandigarh, India'],
      'new york': ['New York, NY, USA', 'New York City, NY, USA', 'New York, United States'],
      'london': ['London, UK', 'London, England, UK', 'London, United Kingdom'],
      'delhi': ['Delhi, India', 'New Delhi, India', 'Delhi, NCR, India'],
      'mumbai': ['Mumbai, Maharashtra, India', 'Mumbai, India', 'Bombay, India'],
      'bangalore': ['Bangalore, Karnataka, India', 'Bengaluru, Karnataka, India', 'Bangalore, India'],
      'chennai': ['Chennai, Tamil Nadu, India', 'Chennai, India', 'Madras, India'],
      'kolkata': ['Kolkata, West Bengal, India', 'Kolkata, India', 'Calcutta, India'],
      'hyderabad': ['Hyderabad, Telangana, India', 'Hyderabad, India'],
      'pune': ['Pune, Maharashtra, India', 'Pune, India'],
      'chandigarh': ['Chandigarh, India', 'Chandigarh, Punjab, India'],
      'los angeles': ['Los Angeles, CA, USA', 'Los Angeles, California, USA'],
      'chicago': ['Chicago, IL, USA', 'Chicago, Illinois, USA'],
      'san francisco': ['San Francisco, CA, USA', 'San Francisco, California, USA'],
      'toronto': ['Toronto, ON, Canada', 'Toronto, Ontario, Canada'],
      'sydney': ['Sydney, NSW, Australia', 'Sydney, Australia'],
      'melbourne': ['Melbourne, VIC, Australia', 'Melbourne, Australia'],
      'paris': ['Paris, France', 'Paris, Île-de-France, France'],
      'tokyo': ['Tokyo, Japan', 'Tokyo, Kanto, Japan'],
      'dubai': ['Dubai, UAE', 'Dubai, United Arab Emirates'],
    };

    // Find matching locations
    const query = input.toLowerCase().trim();
    const matches: string[] = [];
    
    // Exact match
    if (commonLocations[query]) {
      matches.push(...commonLocations[query]);
    } else {
      // Partial match
      for (const [key, locations] of Object.entries(commonLocations)) {
        if (key.includes(query) || query.includes(key)) {
          matches.push(...locations);
        }
      }
      
      // Also add the input as-is with common suffixes
      if (matches.length === 0) {
        matches.push(
          `${input}, India`,
          `${input}, USA`,
          `${input}, UK`,
          `${input}, Canada`
        );
      }
    }

    // Format as predictions
    const predictions = matches.slice(0, 10).map((location, index) => ({
      description: location,
      placeId: `simple_${index}_${Date.now()}`,
      structuredFormatting: {
        main_text: location.split(',')[0],
        secondary_text: location.split(',').slice(1).join(',').trim()
      }
    }));

    return NextResponse.json({ predictions });
  } catch (error: any) {
    console.error("Error in simple autocomplete:", error);
    return NextResponse.json(
      { error: error.message || "Failed to fetch autocomplete" },
      { status: 500 }
    );
  }
}

