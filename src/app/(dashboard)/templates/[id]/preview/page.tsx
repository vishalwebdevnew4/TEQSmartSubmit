"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";

export default function TemplatePreviewPage() {
  const params = useParams();
  const router = useRouter();
  const templateId = params.id as string;
  
  const [template, setTemplate] = useState<any>(null);
  const [version, setVersion] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [previewMode, setPreviewMode] = useState<"code" | "rendered">("rendered");

  useEffect(() => {
    if (templateId) {
      fetchTemplate();
    }
  }, [templateId]);

  const fetchTemplate = async () => {
    try {
      const res = await fetch(`/api/templates/${templateId}`);
      const data = await res.json();
      setTemplate(data);
      
      // Get active version
      if (data.versions && data.versions.length > 0) {
        const activeVersion = data.versions.find((v: any) => v.isActive) || data.versions[0];
        setVersion(activeVersion);
      }
    } catch (error) {
      console.error("Failed to fetch template:", error);
      setError("Failed to load template");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto mb-4"></div>
          <p className="text-slate-400">Loading template preview...</p>
        </div>
      </div>
    );
  }

  if (error || !template || !version) {
    return (
      <div className="text-center py-12">
        <p className="text-slate-400 mb-4">{error || "Template not found"}</p>
        <Link href="/deployments" className="text-indigo-400 hover:text-indigo-300">
          ← Back to Deployments
        </Link>
      </div>
    );
  }

  // Handle content - it might be stored as JSON string or object
  let contentObj = version.content;
  if (typeof contentObj === "string") {
    try {
      contentObj = JSON.parse(contentObj);
    } catch (e) {
      console.error("Failed to parse content as JSON:", e);
      contentObj = {};
    }
  }
  
  const pageContent = contentObj?.["app/page.tsx"] || contentObj?.["page.tsx"] || contentObj?.["app\\page.tsx"] || "";

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <Link href="/deployments" className="text-indigo-400 hover:text-indigo-300 text-sm mb-2 inline-block">
            ← Back to Deployments
          </Link>
          <h2 className="text-2xl font-semibold text-white">Template Preview</h2>
          <div className="flex items-center gap-3 mt-1">
            <p className="text-sm text-slate-400">
              {template.name} • Version {version.version}
            </p>
            {contentObj?._metadata?.isGptGenerated ? (
              <span className="px-2 py-1 rounded text-xs font-medium bg-gradient-to-r from-purple-600 to-indigo-600 text-white flex items-center gap-1">
                <span>✨</span>
                <span>GPT Generated</span>
              </span>
            ) : (
              <span className="px-2 py-1 rounded text-xs font-medium bg-slate-700 text-slate-300 flex items-center gap-1">
                <span>⚙️</span>
                <span>Template Fallback</span>
              </span>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setPreviewMode("rendered")}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              previewMode === "rendered"
                ? "bg-indigo-600 text-white"
                : "bg-slate-800 text-slate-300 hover:bg-slate-700"
            }`}
          >
            Preview
          </button>
          <button
            onClick={() => setPreviewMode("code")}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              previewMode === "code"
                ? "bg-indigo-600 text-white"
                : "bg-slate-800 text-slate-300 hover:bg-slate-700"
            }`}
          >
            Code
          </button>
          {template.businessId && (
            <button
              onClick={async () => {
                if (confirm("Regenerate this template? This will create a new version.")) {
                  try {
                    const res = await fetch("/api/businesses/generate-website", {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({
                        businessId: template.businessId,
                        copyStyle: version.aiCopyStyle || "friendly",
                      }),
                    });
                    const data = await res.json();
                    if (data.success) {
                      router.push(`/templates/${data.templateId}/preview`);
                    } else {
                      alert(`Error: ${data.error || "Failed to regenerate"}`);
                    }
                  } catch (error: any) {
                    alert(`Error: ${error.message}`);
                  }
                }
              }}
              className="px-4 py-2 rounded-lg text-sm font-medium bg-emerald-600 text-white hover:bg-emerald-700 transition-colors"
            >
              🔄 Regenerate
            </button>
          )}
        </div>
      </header>

      {previewMode === "code" ? (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-white mb-2">Generated Code</h3>
            <p className="text-sm text-slate-400">app/page.tsx</p>
          </div>
          <pre className="bg-slate-950 rounded-lg p-4 overflow-x-auto">
            <code className="text-sm text-slate-300 font-mono">{pageContent}</code>
          </pre>
          
          {contentObj?.["package.json"] && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold text-white mb-2">package.json</h3>
              <pre className="bg-slate-950 rounded-lg p-4 overflow-x-auto">
                <code className="text-sm text-slate-300 font-mono">
                  {typeof contentObj["package.json"] === "string"
                    ? contentObj["package.json"]
                    : JSON.stringify(contentObj["package.json"], null, 2)}
                </code>
              </pre>
            </div>
          )}

          {contentObj?.["tailwind.config.js"] && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold text-white mb-2">tailwind.config.js</h3>
              <pre className="bg-slate-950 rounded-lg p-4 overflow-x-auto">
                <code className="text-sm text-slate-300 font-mono">
                  {contentObj["tailwind.config.js"]}
                </code>
              </pre>
            </div>
          )}
          
          {!pageContent && Object.keys(contentObj).length === 0 && (
            <div className="mt-6 p-4 bg-rose-900/20 border border-rose-800 rounded-lg">
              <p className="text-rose-400 text-sm">
                ⚠️ No content found in template version. The template may not have been generated correctly.
              </p>
              <p className="text-slate-400 text-xs mt-2">
                Content keys: {Object.keys(contentObj).join(", ") || "none"}
              </p>
            </div>
          )}
        </div>
      ) : (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <div className="mb-4">
            <h3 className="text-lg font-semibold text-white mb-2">Rendered Preview</h3>
            <p className="text-sm text-slate-400">
              This is a preview of how the website will look. Note: Some features may not work in preview mode.
            </p>
          </div>
          <div className="bg-white rounded-lg p-8 overflow-auto" style={{ minHeight: "600px" }}>
            {pageContent ? (
              <iframe
                srcDoc={(() => {
                  // Extract JSX content and convert to HTML
                  let htmlContent = pageContent;
                  
                  // Remove imports and exports
                  htmlContent = htmlContent.replace(/import.*?from.*?;/g, "");
                  htmlContent = htmlContent.replace(/export const metadata.*?};/gs, "");
                  
                  // Extract content between return ( and closing );
                  const returnStart = htmlContent.indexOf("return (");
                  const returnEnd = htmlContent.lastIndexOf(");");
                  if (returnStart !== -1 && returnEnd !== -1) {
                    htmlContent = htmlContent.substring(returnStart + 8, returnEnd).trim();
                  }
                  
                  // Remove function declaration if still present
                  htmlContent = htmlContent.replace(/export default function Home\(\)\s*\{[\s\S]*?return\s*\(/g, "");
                  
                  // Convert JSX className to class
                  htmlContent = htmlContent.replace(/className=/g, "class=");
                  
                  // Remove JSX comments
                  htmlContent = htmlContent.replace(/\{\{\/\*[\s\S]*?\*\/\}\}/g, "");
                  htmlContent = htmlContent.replace(/\{\/\*[\s\S]*?\*\/\}/g, "");
                  
                  // Get business info for replacements
                  const businessName = template.business?.name || template.name.split(" - ")[0] || "Business";
                  const businessDesc = template.business?.description || "";
                  
                  // Replace escaped variables (from Python f-strings)
                  htmlContent = htmlContent.replace(/\{hero_title_escaped\}/g, businessName);
                  htmlContent = htmlContent.replace(/\{hero_subtitle_escaped\}/g, 
                    version.aiCopyStyle === "minimalist" ? "Quality. Simplicity. Excellence." :
                    version.aiCopyStyle === "formal" ? "Delivering exceptional quality and service" :
                    version.aiCopyStyle === "marketing" ? "Discover the difference that sets us apart" :
                    businessDesc || "Your trusted partner"
                  );
                  htmlContent = htmlContent.replace(/\{about_text_escaped\}/g, 
                    `${businessName} is committed to providing exceptional service and quality. ${businessDesc || "We specialize in excellence."}`
                  );
                  htmlContent = htmlContent.replace(/\{services_text_escaped\}/g, 
                    `At ${businessName}, we offer a comprehensive range of services designed to meet your needs.`
                  );
                  htmlContent = htmlContent.replace(/\{contact_text_escaped\}/g, 
                    `Get in touch with ${businessName} today. We're here to help!`
                  );
                  htmlContent = htmlContent.replace(/\{name_escaped\}/g, businessName);
                  htmlContent = htmlContent.replace(/\{address_escaped\}/g, template.business?.address || "");
                  htmlContent = htmlContent.replace(/\{phone_escaped\}/g, template.business?.phone || "");
                  htmlContent = htmlContent.replace(/\{website_escaped\}/g, template.business?.website || "");
                  
                  // Replace style expressions with actual colors
                  const primaryColor = version.colorPalette?.primary || "#6366f1";
                  const secondaryColor = version.colorPalette?.secondary || "#8b5cf6";
                  htmlContent = htmlContent.replace(/\{\{\{\{ backgroundColor: "\{primary_color\}" \}\}\}\}/g, `style="background-color: ${primaryColor}"`);
                  htmlContent = htmlContent.replace(/\{\{\{\{ color: "\{primary_color\}" \}\}\}\}/g, `style="color: ${primaryColor}"`);
                  htmlContent = htmlContent.replace(/\{primary_color\}/g, primaryColor);
                  htmlContent = htmlContent.replace(/\{secondary_color\}/g, secondaryColor);
                  
                  // Remove remaining JSX-style expressions
                  htmlContent = htmlContent.replace(/\{\{([^}]+)\}\}/g, "$1");
                  htmlContent = htmlContent.replace(/\{([^}]+)\}/g, "");
                  
                  // Clean up extra whitespace
                  htmlContent = htmlContent.replace(/\s+/g, " ").trim();
                  
                  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${businessName} - Preview</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body { margin: 0; padding: 0; }
    :root {
      --primary: ${primaryColor};
      --secondary: ${secondaryColor};
    }
  </style>
</head>
<body>
  ${htmlContent}
</body>
</html>`;
                })()}
                className="w-full h-full border-0"
                style={{ minHeight: "600px", width: "100%" }}
                title="Template Preview"
                sandbox="allow-same-origin allow-scripts"
              />
            ) : (
              <div className="flex items-center justify-center h-[600px] text-slate-400">
                <div className="text-center">
                  <p className="text-lg mb-2">No preview available</p>
                  <p className="text-sm">Switch to Code view to see the generated template</p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Template Info */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Template Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-slate-400 mb-1">Template Name</p>
            <p className="text-white font-medium">{template.name}</p>
          </div>
          <div>
            <p className="text-sm text-slate-400 mb-1">Version</p>
            <p className="text-white">Version {version.version}</p>
          </div>
          <div>
            <p className="text-sm text-slate-400 mb-1">Copy Style</p>
            <p className="text-white capitalize">{version.aiCopyStyle || "friendly"}</p>
          </div>
          {version.colorPalette && (
            <div>
              <p className="text-sm text-slate-400 mb-1">Color Palette</p>
              <div className="flex gap-2">
                {Object.entries(version.colorPalette).map(([key, value]: [string, any]) => (
                  <div key={key} className="flex items-center gap-2">
                    <div
                      className="w-6 h-6 rounded border border-slate-700"
                      style={{ backgroundColor: value }}
                    ></div>
                    <span className="text-xs text-slate-300">{key}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          {template.business && (
            <div>
              <p className="text-sm text-slate-400 mb-1">Business</p>
              <p className="text-white">{template.business.name}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

