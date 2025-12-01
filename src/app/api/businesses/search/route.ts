import { NextResponse } from "next/server";
import { spawn } from "child_process";
import path from "path";
import { prisma } from "@/lib/prisma";

export const dynamic = "force-dynamic";

export async function POST(request: Request) {
  try {
    const { category, location, radius } = await request.json();

    if (!category || !location) {
      return NextResponse.json(
        { success: false, error: "Category and location are required" },
        { status: 400 }
      );
    }

    // Use Overpass API (free OpenStreetMap query API) for business search
    // This doesn't require billing and works with OpenStreetMap data
    let businesses = [];
    
    try {
      // Extract location coordinates using Nominatim (free geocoding)
      const geocodeUrl = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(location)}&limit=1`;
      const geoResponse = await fetch(geocodeUrl, {
        headers: {
          'User-Agent': 'TEQSmartSubmit/1.0',
          'Accept': 'application/json'
        }
      });
      
      const geoData = await geoResponse.json();
      
      if (!geoData || geoData.length === 0) {
        return NextResponse.json(
          { success: false, error: "Location not found. Please try a more specific location." },
          { status: 400 }
        );
      }
      
      const lat = parseFloat(geoData[0].lat);
      const lon = parseFloat(geoData[0].lon);
      const radiusMeters = radius || 5000;
      
      // Use Overpass API to find businesses by category near location
      // Map category to OSM tags
      const categoryMap: { [key: string]: string } = {
        'restaurant': 'amenity=restaurant',
        'hotel': 'tourism=hotel',
        'gym': 'leisure=fitness_centre',
        'dentist': 'amenity=dentist',
        'lawyer': 'office=lawyer',
        'doctor': 'amenity=doctors',
        'pharmacy': 'amenity=pharmacy',
        'cafe': 'amenity=cafe',
        'bank': 'amenity=bank',
        'gas': 'amenity=fuel',
        'parking': 'amenity=parking',
      };
      
      const osmTag = categoryMap[category.toLowerCase()];
      
      if (!osmTag) {
        // If category not in map, use a generic search
        return NextResponse.json(
          { success: false, error: `Category "${category}" not supported. Supported: ${Object.keys(categoryMap).join(', ')}` },
          { status: 400 }
        );
      }
      
      // Parse OSM tag (e.g., "amenity=restaurant")
      const [key, value] = osmTag.split('=');
      
      // Overpass API query - search for businesses by tag near location
      const overpassQuery = `[out:json][timeout:25];
(
  node["${key}"="${value}"](around:${radiusMeters},${lat},${lon});
  way["${key}"="${value}"](around:${radiusMeters},${lat},${lon});
  relation["${key}"="${value}"](around:${radiusMeters},${lat},${lon});
);
out center meta;`;
      
      const overpassUrl = `https://overpass-api.de/api/interpreter?data=${encodeURIComponent(overpassQuery)}`;
      const overpassResponse = await fetch(overpassUrl, {
        headers: {
          'User-Agent': 'TEQSmartSubmit/1.0',
          'Accept': 'application/json'
        }
      });
      
      const overpassData = await overpassResponse.json();
      
      // Process results
      const elements = overpassData.elements || [];
      
      for (const element of elements.slice(0, 20)) { // Limit to 20 results
        const elementLat = element.lat || element.center?.lat;
        const elementLon = element.lon || element.center?.lon;
        
        if (!elementLat || !elementLon) continue;
        
        // Get place details using Nominatim reverse geocoding
        try {
          const reverseUrl = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${elementLat}&lon=${elementLon}&addressdetails=1`;
          const reverseResponse = await fetch(reverseUrl, {
            headers: {
              'User-Agent': 'TEQSmartSubmit/1.0',
              'Accept': 'application/json'
            }
          });
          
          const reverseData = await reverseResponse.json();
          
          if (reverseData) {
            const address = reverseData.address || {};
            const businessData = {
              name: element.tags?.name || reverseData.display_name?.split(',')[0] || 'Unknown Business',
              phone: element.tags?.['phone'] || element.tags?.['contact:phone'] || null,
              address: reverseData.display_name || `${address.road || ''} ${address.city || address.town || ''}`.trim(),
              website: element.tags?.['website'] || element.tags?.['contact:website'] || null,
              googlePlacesUrl: `https://www.openstreetmap.org/${element.type}/${element.id}`,
              googlePlacesId: `osm_${element.type}_${element.id}`,
              description: element.tags?.['description'] || null,
              categories: [category, ...Object.keys(element.tags || {}).filter(k => k.startsWith('amenity:') || k.startsWith('shop:'))],
              reviews: [],
              images: [],
              rating: null,
              reviewCount: null,
              rawData: { ...element, reverseGeocode: reverseData }
            };
            
            businesses.push(businessData);
          }
        } catch (reverseError) {
          // Skip if reverse geocoding fails
          console.warn('Reverse geocoding failed for element:', element.id);
        }
      }
    } catch (error: any) {
      console.error('Error searching businesses:', error);
      return NextResponse.json(
        { success: false, error: error.message || "Failed to search businesses. Please try again." },
        { status: 500 }
      );
    }

    // Save all businesses to database
    const savedBusinesses = [];
    for (const businessData of businesses) {
      try {
        // Check if business already exists
        const existing = await prisma.business.findFirst({
          where: {
            OR: [
              { googlePlacesId: businessData.googlePlacesId },
              { name: businessData.name, address: businessData.address },
            ],
          },
        });

        if (existing) {
          savedBusinesses.push(existing);
          continue;
        }

        // Create new business
        const business = await prisma.business.create({
          data: {
            name: businessData.name,
            phone: businessData.phone,
            address: businessData.address,
            website: businessData.website,
            googlePlacesUrl: businessData.googlePlacesUrl,
            googlePlacesId: businessData.googlePlacesId,
            description: businessData.description,
            categories: businessData.categories,
            reviews: businessData.reviews,
            images: businessData.images,
            rating: businessData.rating,
            reviewCount: businessData.reviewCount,
            rawData: businessData.rawData,
          },
        });

        savedBusinesses.push(business);
      } catch (error: any) {
        console.error(`Error saving business ${businessData.name}:`, error);
        // Continue with other businesses
      }
    }

    return NextResponse.json({
      success: true,
      businesses: savedBusinesses,
      total: savedBusinesses.length,
      category,
      location,
    });
  } catch (error: any) {
    console.error("Error searching businesses:", error);
    return NextResponse.json(
      { success: false, error: error.message || "Failed to search businesses" },
      { status: 500 }
    );
  }
}

