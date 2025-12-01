#!/usr/bin/env python3
"""
Google Places API service - Fetches business data from Google Places.
Can be called from Next.js API routes or directly from Python.
"""

import json
import sys
import os
import argparse
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import googlemaps
except ImportError:
    print(json.dumps({"error": "googlemaps package not installed. Run: pip install googlemaps"}))
    sys.exit(1)


def search_businesses_by_category_location(
    category: str,
    location: str,
    radius: int = 5000,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Search for businesses by category and location.
    
    Args:
        category: Business category/type (e.g., "restaurant", "hotel", "gym")
        location: Location string (e.g., "New York, NY" or "latitude,longitude")
        radius: Search radius in meters (default: 5000m = 5km)
        api_key: Google Places API key (or from GOOGLE_PLACES_API_KEY env var)
    
    Returns:
        Dictionary with list of businesses
    """
    api_key = api_key or os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_PLACES_API_KEY environment variable not set")
    
    gmaps = googlemaps.Client(key=api_key)
    
    # Build query with category and location
    query = f"{category} in {location}"
    
    # Perform text search
    results = gmaps.places(query=query)
    
    businesses = []
    for place in results.get("results", [])[:20]:  # Limit to 20 results
        place_id = place.get("place_id")
        if place_id:
            # Get detailed information
            place_details = gmaps.place(place_id=place_id)
            result = place_details.get("result", {})
            
            business_data = {
                "name": result.get("name", ""),
                "phone": result.get("formatted_phone_number") or result.get("international_phone_number", ""),
                "address": result.get("formatted_address", ""),
                "website": result.get("website", ""),
                "googlePlacesUrl": f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                "googlePlacesId": place_id,
                "description": None,
                "categories": [cat for cat in result.get("types", []) if isinstance(cat, str) and "establishment" not in cat.lower()],
                "reviews": [
                    {
                        "author": r.get("author_name", ""),
                        "rating": r.get("rating"),
                        "text": r.get("text", ""),
                        "time": r.get("time"),
                    }
                    for r in result.get("reviews", [])[:5]
                ],
                "images": [
                    photo.get("photo_reference")
                    for photo in result.get("photos", [])[:5]
                ],
                "rating": result.get("rating"),
                "reviewCount": result.get("user_ratings_total", 0),
                "rawData": result,
            }
            businesses.append(business_data)
    
    return {
        "businesses": businesses,
        "total": len(businesses),
        "category": category,
        "location": location,
    }


def fetch_business_data(input_value: str, input_type: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch business data from Google Places API.
    
    Args:
        input_value: Business name, phone number, or Google Places URL
        input_type: "name", "phone", or "url"
        api_key: Google Places API key (or from GOOGLE_PLACES_API_KEY env var)
    
    Returns:
        Dictionary with business data
    """
    api_key = api_key or os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_PLACES_API_KEY environment variable not set")
    
    gmaps = googlemaps.Client(key=api_key)
    
    # Extract place_id from URL if input_type is "url"
    if input_type == "url":
        # Extract place_id from Google Places URL
        # Format: https://www.google.com/maps/place/?q=place_id:ChIJ...
        place_id = None
        if "place_id:" in input_value:
            place_id = input_value.split("place_id:")[-1].split("&")[0]
        elif "/place/" in input_value:
            # Try to extract from URL path
            parts = input_value.split("/place/")
            if len(parts) > 1:
                place_id = parts[1].split("/")[0].split("?")[0]
        
        if place_id:
            place_details = gmaps.place(place_id=place_id)
        else:
            raise ValueError("Could not extract place_id from URL")
    elif input_type == "phone":
        # Search by phone number
        results = gmaps.places(query=input_value)
        if not results.get("results"):
            raise ValueError("No business found with that phone number")
        place_id = results["results"][0]["place_id"]
        place_details = gmaps.place(place_id=place_id)
    else:  # input_type == "name"
        # Search by business name
        results = gmaps.places(query=input_value)
        if not results.get("results"):
            raise ValueError("No business found with that name")
        place_id = results["results"][0]["place_id"]
        place_details = gmaps.place(place_id=place_id)
    
    result = place_details.get("result", {})
    
    # Extract data
    business_data = {
        "name": result.get("name", ""),
        "phone": result.get("formatted_phone_number") or result.get("international_phone_number", ""),
        "address": result.get("formatted_address", ""),
        "website": result.get("website", ""),
        "googlePlacesUrl": f"https://www.google.com/maps/place/?q=place_id:{place_id}",
        "googlePlacesId": place_id,
        "description": None,  # Not directly available, could use reviews summary
        "categories": [cat for cat in result.get("types", []) if isinstance(cat, str) and "establishment" not in cat.lower()],
        "reviews": [
            {
                "author": r.get("author_name", ""),
                "rating": r.get("rating"),
                "text": r.get("text", ""),
                "time": r.get("time"),
            }
            for r in result.get("reviews", [])[:5]  # Top 5 reviews
        ],
        "images": [
            photo.get("photo_reference")
            for photo in result.get("photos", [])[:5]  # Top 5 photos
        ],
        "rating": result.get("rating"),
        "reviewCount": result.get("user_ratings_total", 0),
        "rawData": result,  # Store full response
    }
    
    return business_data


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Fetch business data from Google Places API")
    parser.add_argument("--input", help="Business name, phone, or Google Places URL")
    parser.add_argument("--type", choices=["name", "phone", "url"], default="name", help="Input type")
    parser.add_argument("--category", help="Business category (e.g., restaurant, hotel, gym)")
    parser.add_argument("--location", help="Location (e.g., 'New York, NY' or '40.7128,-74.0060')")
    parser.add_argument("--radius", type=int, default=5000, help="Search radius in meters (default: 5000)")
    parser.add_argument("--api-key", help="Google Places API key (or use GOOGLE_PLACES_API_KEY env var)")
    
    args = parser.parse_args()
    
    try:
        if args.category and args.location:
            # Category and location search
            data = search_businesses_by_category_location(
                args.category,
                args.location,
                args.radius,
                args.api_key
            )
        elif args.input:
            # Single business search
            data = fetch_business_data(args.input, args.type, args.api_key)
        else:
            raise ValueError("Either --input or both --category and --location must be provided")
        
        print(json.dumps(data, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

