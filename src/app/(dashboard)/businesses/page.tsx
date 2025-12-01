"use client";

import { useState, useEffect } from "react";

export default function BusinessesPage() {
  const [businesses, setBusinesses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [inputValue, setInputValue] = useState("");
  const [inputType, setInputType] = useState<"name" | "phone" | "url">("name");
  const [processing, setProcessing] = useState(false);
  
  // Category & Location search
  const [category, setCategory] = useState("");
  const [location, setLocation] = useState("");
  const [searchMode, setSearchMode] = useState<"single" | "category">("single");
  
  // Location autocomplete
  const [locationSuggestions, setLocationSuggestions] = useState<any[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [locationInputFocused, setLocationInputFocused] = useState(false);
  
  // Filters
  const [filterCategory, setFilterCategory] = useState("");
  const [filterLocation, setFilterLocation] = useState("");

  useEffect(() => {
    fetchBusinesses();
  }, []);

  // Fetch location autocomplete suggestions
  useEffect(() => {
    if (location.trim().length >= 2 && locationInputFocused) {
      const timeoutId = setTimeout(() => {
        fetchLocationSuggestions(location);
      }, 300); // Debounce 300ms

      return () => clearTimeout(timeoutId);
    } else {
      setLocationSuggestions([]);
      setShowSuggestions(false);
    }
  }, [location, locationInputFocused]);

  const fetchLocationSuggestions = async (query: string) => {
    try {
      // Use OpenStreetMap API for real data (primary)
      const res = await fetch(`/api/places/autocomplete-free?input=${encodeURIComponent(query)}`);
      const data = await res.json();
      
      if (data.predictions && data.predictions.length > 0) {
        setLocationSuggestions(data.predictions);
        setShowSuggestions(true);
      } else if (data.error) {
        // If API error, try simple fallback
        console.warn('OpenStreetMap API error, using fallback:', data.error);
        const fallbackRes = await fetch(`/api/places/autocomplete-simple?input=${encodeURIComponent(query)}`);
        const fallbackData = await fallbackRes.json();
        
        if (fallbackData.predictions && fallbackData.predictions.length > 0) {
          setLocationSuggestions(fallbackData.predictions);
          setShowSuggestions(true);
        } else {
          setLocationSuggestions([]);
          setShowSuggestions(false);
        }
      } else {
        setLocationSuggestions([]);
        setShowSuggestions(false);
      }
    } catch (error) {
      console.error("Failed to fetch location suggestions:", error);
      // Try simple fallback on error
      try {
        const fallbackRes = await fetch(`/api/places/autocomplete-simple?input=${encodeURIComponent(query)}`);
        const fallbackData = await fallbackRes.json();
        if (fallbackData.predictions && fallbackData.predictions.length > 0) {
          setLocationSuggestions(fallbackData.predictions);
          setShowSuggestions(true);
        } else {
          setLocationSuggestions([]);
          setShowSuggestions(false);
        }
      } catch (fallbackError) {
        setLocationSuggestions([]);
        setShowSuggestions(false);
      }
    }
  };

  const handleLocationSelect = (suggestion: any) => {
    setLocation(suggestion.description);
    setShowSuggestions(false);
    setLocationInputFocused(false);
  };

  const fetchBusinesses = async () => {
    try {
      const res = await fetch("/api/businesses");
      const data = await res.json();
      setBusinesses(data);
    } catch (error) {
      console.error("Failed to fetch businesses:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleFetchBusiness = async () => {
    if (!inputValue.trim()) return;
    
    setProcessing(true);
    try {
      const res = await fetch("/api/businesses/fetch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          input: inputValue.trim(),
          inputType,
        }),
      });
      
      const data = await res.json();
      if (data.success) {
        setInputValue("");
        fetchBusinesses();
      } else {
        alert(data.error || "Failed to fetch business data");
      }
    } catch (error) {
      alert("Error fetching business data");
    } finally {
      setProcessing(false);
    }
  };

  const handleUploadCSV = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setProcessing(true);
    try {
      const res = await fetch("/api/businesses/upload-csv", {
        method: "POST",
        body: formData,
      });
      
      const data = await res.json();
      if (data.success) {
        fetchBusinesses();
      } else {
        alert(data.error || "Failed to upload CSV");
      }
    } catch (error) {
      alert("Error uploading CSV");
    } finally {
      setProcessing(false);
    }
  };

  const handleCategoryLocationSearch = async () => {
    if (!category.trim() || !location.trim()) {
      alert("Please enter both category and location");
      return;
    }
    
    setProcessing(true);
    try {
      const res = await fetch("/api/businesses/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          category: category.trim(),
          location: location.trim(),
          radius: 5000,
        }),
      });
      
      const data = await res.json();
      if (data.success) {
        setCategory("");
        setLocation("");
        fetchBusinesses();
        alert(`Found ${data.total} businesses!`);
      } else {
        alert(data.error || "Failed to search businesses");
      }
    } catch (error) {
      alert("Error searching businesses");
    } finally {
      setProcessing(false);
    }
  };

  // Filter businesses
  const filteredBusinesses = businesses.filter((business) => {
    if (filterCategory && business.categories) {
      const categories = Array.isArray(business.categories) 
        ? business.categories 
        : JSON.parse(business.categories || "[]");
      const categoryMatch = categories.some((cat: string) => 
        cat.toLowerCase().includes(filterCategory.toLowerCase())
      );
      if (!categoryMatch) return false;
    }
    
    if (filterLocation && business.address) {
      if (!business.address.toLowerCase().includes(filterLocation.toLowerCase())) {
        return false;
      }
    }
    
    return true;
  });

  return (
    <div className="space-y-8">
      <header className="flex flex-col gap-2">
        <h2 className="text-2xl font-semibold text-white">Businesses</h2>
        <p className="text-sm text-slate-400">Manage businesses from Google Places</p>
      </header>

      {/* Search Mode Toggle */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <div className="flex gap-2 mb-4">
          <button
            onClick={() => setSearchMode("single")}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              searchMode === "single"
                ? "bg-indigo-600 text-white"
                : "bg-slate-800 text-slate-300 hover:bg-slate-700"
            }`}
          >
            Single Business
          </button>
          <button
            onClick={() => setSearchMode("category")}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              searchMode === "category"
                ? "bg-indigo-600 text-white"
                : "bg-slate-800 text-slate-300 hover:bg-slate-700"
            }`}
          >
            Category & Location
          </button>
        </div>

        {/* Single Business Search */}
        {searchMode === "single" && (
          <>
            <h3 className="text-lg font-semibold text-white mb-4">Fetch Single Business</h3>
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <select
                  value={inputType}
                  onChange={(e) => setInputType(e.target.value as "name" | "phone" | "url")}
                  className="w-full sm:w-auto mb-2 sm:mb-0 rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-white"
                >
                  <option value="name">Business Name</option>
                  <option value="phone">Phone Number</option>
                  <option value="url">Google Places URL</option>
                </select>
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder={`Enter ${inputType === "name" ? "business name" : inputType === "phone" ? "phone number" : "Google Places URL"}`}
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-white placeholder-slate-500"
                  onKeyPress={(e) => e.key === "Enter" && handleFetchBusiness()}
                />
              </div>
              <button
                onClick={handleFetchBusiness}
                disabled={processing || !inputValue.trim()}
                className="rounded-lg bg-indigo-600 px-6 py-2 font-medium text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {processing ? "Fetching..." : "Fetch"}
              </button>
            </div>
            
            <div className="mt-4 pt-4 border-t border-slate-700">
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Or upload CSV file
              </label>
              <input
                type="file"
                accept=".csv"
                onChange={handleUploadCSV}
                disabled={processing}
                className="block w-full text-sm text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-700"
              />
            </div>
          </>
        )}

        {/* Category & Location Search */}
        {searchMode === "category" && (
          <>
            <h3 className="text-lg font-semibold text-white mb-4">Search by Category & Location</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Category (e.g., restaurant, hotel, gym, dentist, lawyer)
                </label>
                <input
                  type="text"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  placeholder="Enter business category"
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-white placeholder-slate-500"
                  onKeyPress={(e) => e.key === "Enter" && handleCategoryLocationSearch()}
                />
              </div>
              <div className="relative">
                <label className="block text-sm font-medium text-slate-300 mb-2">
                  Location (e.g., "New York, NY" or "London, UK")
                </label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  onFocus={() => setLocationInputFocused(true)}
                  onBlur={() => {
                    // Delay hiding suggestions to allow click
                    setTimeout(() => {
                      setLocationInputFocused(false);
                      setShowSuggestions(false);
                    }, 200);
                  }}
                  placeholder="Start typing a location..."
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  onKeyPress={(e) => e.key === "Enter" && handleCategoryLocationSearch()}
                />
                {showSuggestions && locationSuggestions.length > 0 && (
                  <div className="absolute z-10 w-full mt-1 bg-slate-800 border border-slate-700 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                    {locationSuggestions.map((suggestion, idx) => (
                      <button
                        key={idx}
                        type="button"
                        onClick={() => handleLocationSelect(suggestion)}
                        className="w-full text-left px-4 py-2 hover:bg-slate-700 text-white text-sm transition-colors"
                      >
                        <div className="font-medium">{suggestion.structuredFormatting?.main_text}</div>
                        {suggestion.structuredFormatting?.secondary_text && (
                          <div className="text-xs text-slate-400">{suggestion.structuredFormatting.secondary_text}</div>
                        )}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              <button
                onClick={handleCategoryLocationSearch}
                disabled={processing || !category.trim() || !location.trim()}
                className="w-full rounded-lg bg-indigo-600 px-6 py-2 font-medium text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {processing ? "Searching..." : "Search Businesses"}
              </button>
            </div>
          </>
        )}
      </div>

      {/* Filters */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Filters</h3>
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Filter by Category
            </label>
            <input
              type="text"
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              placeholder="e.g., restaurant, hotel, gym"
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-white placeholder-slate-500"
            />
          </div>
          <div className="flex-1 relative">
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Filter by Location
            </label>
            <input
              type="text"
              value={filterLocation}
              onChange={(e) => setFilterLocation(e.target.value)}
              placeholder="e.g., New York, London"
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-white placeholder-slate-500"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={() => {
                setFilterCategory("");
                setFilterLocation("");
              }}
              className="px-4 py-2 rounded-lg border border-slate-700 bg-slate-800 text-slate-300 hover:bg-slate-700"
            >
              Clear
            </button>
          </div>
        </div>
      </div>

      {/* Businesses List */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          Businesses ({filteredBusinesses.length} of {businesses.length})
        </h3>
        {loading ? (
          <div className="text-center py-8 text-slate-400">Loading...</div>
        ) : filteredBusinesses.length === 0 ? (
          <div className="text-center py-8 text-slate-400">
            {businesses.length === 0 
              ? "No businesses found. Fetch your first business above."
              : "No businesses match your filters. Try adjusting your search criteria."}
          </div>
        ) : (
          <div className="space-y-4">
            {filteredBusinesses.map((business) => (
              <div
                key={business.id}
                className="rounded-lg border border-slate-700 bg-slate-800/50 p-4 hover:bg-slate-800 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="text-lg font-semibold text-white">{business.name}</h4>
                    {business.address && (
                      <p className="text-sm text-slate-400 mt-1">{business.address}</p>
                    )}
                    <div className="flex flex-wrap gap-4 mt-3 text-sm">
                      {business.phone && (
                        <span className="text-slate-300">📞 {business.phone}</span>
                      )}
                      {business.website && (
                        <a
                          href={business.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-indigo-400 hover:text-indigo-300"
                        >
                          🌐 Website
                        </a>
                      )}
                      {business.rating && (
                        <span className="text-slate-300">⭐ {business.rating} ({business.reviewCount || 0} reviews)</span>
                      )}
                    </div>
                    {business.description && (
                      <p className="text-sm text-slate-400 mt-2 line-clamp-2">{business.description}</p>
                    )}
                    {business.categories && (
                      <div className="flex flex-wrap gap-2 mt-2">
                        {(Array.isArray(business.categories) 
                          ? business.categories 
                          : JSON.parse(business.categories || "[]")
                        ).slice(0, 5).map((cat: string, idx: number) => (
                          <span
                            key={idx}
                            className="px-2 py-1 rounded text-xs bg-slate-700 text-slate-300"
                          >
                            {cat}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2 ml-4">
                    <a
                      href={`/businesses/${business.id}/generate`}
                      className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
                    >
                      Generate Website
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

