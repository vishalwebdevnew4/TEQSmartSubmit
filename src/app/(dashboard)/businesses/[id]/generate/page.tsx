"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";

export default function GenerateWebsitePage() {
  const params = useParams();
  const router = useRouter();
  const businessId = params.id as string;
  
  const [business, setBusiness] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [copyStyle, setCopyStyle] = useState<"formal" | "friendly" | "marketing" | "minimalist">("friendly");
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (businessId) {
      fetchBusiness();
    }
  }, [businessId]);

  const fetchBusiness = async () => {
    try {
      const res = await fetch(`/api/businesses`);
      const data = await res.json();
      const found = data.find((b: any) => b.id === parseInt(businessId));
      setBusiness(found);
    } catch (error) {
      console.error("Failed to fetch business:", error);
      setError("Failed to load business data");
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!business) return;
    
    setGenerating(true);
    setError(null);
    setResult(null);
    
    try {
      const res = await fetch("/api/businesses/generate-website", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          businessId: business.id,
          copyStyle,
        }),
      });
      
      const data = await res.json();
      
      if (data.success) {
        setResult(data);
        // Redirect to deployments or show success
        setTimeout(() => {
          router.push(`/deployments?templateId=${data.templateId}`);
        }, 2000);
      } else {
        setError(data.error || "Failed to generate website");
      }
    } catch (error: any) {
      setError(error.message || "Error generating website");
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto mb-4"></div>
          <p className="text-slate-400">Loading business data...</p>
        </div>
      </div>
    );
  }

  if (!business) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-400 mb-4">Business not found</p>
        <Link href="/businesses" className="text-indigo-400 hover:text-indigo-300">
          ← Back to Businesses
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <header className="flex items-center justify-between">
        <div>
          <Link href="/businesses" className="text-indigo-400 hover:text-indigo-300 text-sm mb-2 inline-block">
            ← Back to Businesses
          </Link>
          <h2 className="text-2xl font-semibold text-white">Generate Website</h2>
          <p className="text-sm text-slate-400 mt-1">Create a Next.js website for {business.name}</p>
        </div>
      </header>

      {/* Business Info */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Business Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-slate-400 mb-1">Name</p>
            <p className="text-white font-medium">{business.name}</p>
          </div>
          {business.address && (
            <div>
              <p className="text-sm text-slate-400 mb-1">Address</p>
              <p className="text-white">{business.address}</p>
            </div>
          )}
          {business.phone && (
            <div>
              <p className="text-sm text-slate-400 mb-1">Phone</p>
              <p className="text-white">{business.phone}</p>
            </div>
          )}
          {business.website && (
            <div>
              <p className="text-sm text-slate-400 mb-1">Website</p>
              <a href={business.website} target="_blank" rel="noopener noreferrer" className="text-indigo-400 hover:text-indigo-300">
                {business.website}
              </a>
            </div>
          )}
          {business.categories && (
            <div>
              <p className="text-sm text-slate-400 mb-1">Categories</p>
              <div className="flex flex-wrap gap-2">
                {(Array.isArray(business.categories) 
                  ? business.categories 
                  : JSON.parse(business.categories || "[]")
                ).slice(0, 5).map((cat: string, idx: number) => (
                  <span key={idx} className="px-2 py-1 rounded text-xs bg-slate-700 text-slate-300">
                    {cat}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Generation Options */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Generation Options</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Copy Style
            </label>
            <select
              value={copyStyle}
              onChange={(e) => setCopyStyle(e.target.value as any)}
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-white"
            >
              <option value="friendly">Friendly</option>
              <option value="formal">Formal</option>
              <option value="marketing">Marketing</option>
              <option value="minimalist">Minimalist</option>
            </select>
            <p className="text-xs text-slate-500 mt-1">
              {copyStyle === "friendly" && "Warm and approachable tone"}
              {copyStyle === "formal" && "Professional and business-like"}
              {copyStyle === "marketing" && "Engaging and persuasive"}
              {copyStyle === "minimalist" && "Clean and simple"}
            </p>
          </div>

          <div className="pt-4 border-t border-slate-700">
            <button
              onClick={handleGenerate}
              disabled={generating}
              className="w-full rounded-lg bg-indigo-600 px-6 py-3 font-medium text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {generating ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Generating Website...</span>
                </>
              ) : (
                "Generate Website"
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="rounded-2xl border border-red-800 bg-red-900/20 p-6">
          <p className="text-red-400">Error: {error}</p>
        </div>
      )}

      {/* Success Message */}
      {result && (
        <div className="rounded-2xl border border-emerald-800 bg-emerald-900/20 p-6">
          <p className="text-emerald-400 mb-2">✅ Website generated successfully!</p>
          <p className="text-sm text-slate-400 mb-4">
            Template ID: {result.templateId} | Version ID: {result.templateVersionId}
          </p>
          <div className="flex gap-3">
            <button
              onClick={() => router.push(`/templates/${result.templateId}/preview`)}
              className="px-4 py-2 rounded-lg bg-indigo-600 text-white font-medium hover:bg-indigo-700 transition-colors"
            >
              👁️ Preview Template
            </button>
            <button
              onClick={() => {
                setResult(null);
                setError(null);
              }}
              className="px-4 py-2 rounded-lg bg-slate-700 text-white font-medium hover:bg-slate-600 transition-colors"
            >
              🔄 Regenerate
            </button>
            <button
              onClick={() => router.push(`/deployments`)}
              className="px-4 py-2 rounded-lg bg-emerald-600 text-white font-medium hover:bg-emerald-700 transition-colors"
            >
              🚀 Go to Deployments
            </button>
          </div>
        </div>
      )}

      {/* Preview Info */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">What Will Be Generated</h3>
        <ul className="space-y-2 text-sm text-slate-300">
          <li className="flex items-start gap-2">
            <span className="text-indigo-400">✓</span>
            <span>Next.js + Tailwind CSS website template</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-indigo-400">✓</span>
            <span>AI-generated copy (Hero, About, Services, Contact sections)</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-indigo-400">✓</span>
            <span>Auto color palette based on business type</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-indigo-400">✓</span>
            <span>Responsive design (mobile-friendly)</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="text-indigo-400">✓</span>
            <span>Ready for Vercel deployment</span>
          </li>
        </ul>
      </div>
    </div>
  );
}

