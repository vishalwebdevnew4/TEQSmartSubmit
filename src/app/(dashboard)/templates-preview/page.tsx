"use client";

import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";

export default function TemplatePreviewPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const category = searchParams.get("category");
  const name = searchParams.get("name");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>("");

  useEffect(() => {
    if (category && name) {
      const url = `/api/templates/preview?category=${encodeURIComponent(category)}&name=${encodeURIComponent(name)}`;
      setPreviewUrl(url);
      setLoading(false);
    }
  }, [category, name]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto mb-4"></div>
          <p className="text-slate-400">Loading template...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-900">
        <div className="text-center">
          <p className="text-red-400 mb-4">Error: {error}</p>
          <button
            onClick={() => router.back()}
            className="px-4 py-2 rounded-lg bg-slate-700 text-white hover:bg-slate-600"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  if (!previewUrl) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-slate-900">
        <div className="text-center">
          <p className="text-slate-400 mb-4">No template selected</p>
          <button
            onClick={() => router.back()}
            className="px-4 py-2 rounded-lg bg-slate-700 text-white hover:bg-slate-600"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-white">
      {/* Full Screen Preview - No Header */}
      <iframe
        src={previewUrl}
        className="w-full h-full border-0"
        title="Template Preview"
        sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-modals"
        style={{ 
          width: '100%', 
          height: '100%',
          border: 'none',
          display: 'block'
        }}
        onLoad={() => setLoading(false)}
      />

      {/* Loading Overlay */}
      {loading && (
        <div className="absolute inset-0 bg-white flex items-center justify-center z-50">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto mb-4"></div>
            <p className="text-slate-400">Loading template preview...</p>
          </div>
        </div>
      )}
    </div>
  );
}

