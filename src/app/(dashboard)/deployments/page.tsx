"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

export default function DeploymentsPage() {
  const [deployments, setDeployments] = useState<any[]>([]);
  const [templates, setTemplates] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [deploying, setDeploying] = useState<number | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [deploymentsRes, templatesRes] = await Promise.all([
        fetch("/api/deployments"),
        fetch("/api/templates?withVersions=true"),
      ]);
      const deploymentsData = await deploymentsRes.json();
      const templatesData = await templatesRes.json();
      setDeployments(deploymentsData);
      // Filter templates that have active versions but no deployments
      const templatesWithVersions = templatesData.filter((t: any) => 
        t.versions && t.versions.some((v: any) => v.isActive)
      );
      setTemplates(templatesWithVersions);
    } catch (error) {
      console.error("Failed to fetch data:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleDeploy = async (templateId: number, businessId: number) => {
    setDeploying(templateId);
    try {
      // Get the active template version
      const template = templates.find(t => t.id === templateId);
      const activeVersion = template?.versions?.find((v: any) => v.isActive);
      
      if (!activeVersion) {
        alert("No active version found for this template");
        setDeploying(null);
        return;
      }

      const res = await fetch("/api/businesses/deploy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          businessId,
          templateVersionId: activeVersion.id,
        }),
      });
      const data = await res.json();
      if (data.success) {
        // Refresh data
        await fetchData();
        alert("Deployment started! Check back in a few moments.");
      } else {
        alert(`Deployment failed: ${data.error || "Unknown error"}`);
      }
    } catch (error: any) {
      alert(`Error: ${error.message}`);
    } finally {
      setDeploying(null);
    }
  };

  return (
    <div className="space-y-8">
      <header className="flex flex-col gap-2">
        <h2 className="text-2xl font-semibold text-white">Deployments</h2>
        <p className="text-sm text-slate-400">Track Vercel deployments and website status</p>
      </header>

      {/* Templates Ready to Deploy */}
      {templates.length > 0 && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Templates Ready to Deploy</h3>
          <div className="space-y-4">
            {templates.map((template) => {
              const activeVersion = template.versions?.find((v: any) => v.isActive);
              return (
                <div
                  key={template.id}
                  className="rounded-lg border border-indigo-700/50 bg-indigo-900/10 p-4"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h4 className="text-lg font-semibold text-white">
                          {template.name}
                        </h4>
                        <span className="rounded-full px-3 py-1 text-xs font-medium bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                          Ready
                        </span>
                      </div>
                      {template.business && (
                        <p className="text-sm text-slate-400 mb-2">
                          Business: {template.business.name}
                        </p>
                      )}
                      {activeVersion && (
                        <div className="flex items-center gap-2 mt-1">
                          <p className="text-xs text-slate-500">
                            Version {activeVersion.version} • Style: {activeVersion.aiCopyStyle || "friendly"}
                          </p>
                          {(() => {
                            const content = typeof activeVersion.content === 'string' 
                              ? JSON.parse(activeVersion.content || '{}') 
                              : activeVersion.content || {};
                            const isGpt = content._metadata?.isGptGenerated;
                            return isGpt ? (
                              <span className="px-2 py-0.5 rounded text-xs font-medium bg-gradient-to-r from-purple-600 to-indigo-600 text-white flex items-center gap-1">
                                <span>✨</span>
                                <span>GPT</span>
                              </span>
                            ) : (
                              <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-700 text-slate-300 flex items-center gap-1">
                                <span>⚙️</span>
                                <span>Fallback</span>
                              </span>
                            );
                          })()}
                        </div>
                      )}
                    </div>
                    <div className="ml-4 flex gap-2">
                      <Link
                        href={`/templates/${template.id}/preview`}
                        className="rounded-lg bg-slate-700 px-4 py-2 text-sm font-medium text-white hover:bg-slate-600 transition-colors flex items-center gap-2"
                      >
                        👁️ Preview
                      </Link>
                      <button
                        onClick={() => handleDeploy(template.id, template.businessId)}
                        disabled={deploying === template.id}
                        className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                      >
                        {deploying === template.id ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                            <span>Deploying...</span>
                          </>
                        ) : (
                          "🚀 Deploy to Vercel"
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Active Deployments */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Active Deployments</h3>
        {loading ? (
          <div className="text-center py-8 text-slate-400">Loading...</div>
        ) : deployments.length === 0 ? (
          <div className="text-center py-8 text-slate-400">
            No deployments yet. Generate a website template and deploy it!
          </div>
        ) : (
          <div className="space-y-4">
            {deployments.map((deployment) => (
              <div
                key={deployment.id}
                className="rounded-lg border border-slate-700 bg-slate-800/50 p-4 hover:bg-slate-800 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="text-lg font-semibold text-white">
                        {deployment.business?.name || "Unknown Business"}
                      </h4>
                      <span
                        className={`rounded-full px-3 py-1 text-xs font-medium ${
                          deployment.status === "success"
                            ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                            : deployment.status === "deploying"
                              ? "bg-blue-500/20 text-blue-300 border border-blue-500/30"
                              : deployment.status === "failed"
                                ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                                : "bg-slate-700/50 text-slate-300 border border-slate-600/30"
                        }`}
                      >
                        {deployment.status}
                      </span>
                    </div>
                    {deployment.vercelUrl && (
                      <a
                        href={deployment.vercelUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-indigo-400 hover:text-indigo-300 text-sm block"
                      >
                        🌐 {deployment.vercelUrl}
                      </a>
                    )}
                    {deployment.githubRepoUrl && (
                      <p className="text-sm text-slate-400 mt-1">
                        📦 {deployment.githubRepoUrl}
                      </p>
                    )}
                    <p className="text-xs text-slate-500 mt-2">
                      Deployed: {deployment.deployedAt ? new Date(deployment.deployedAt).toLocaleString() : "Pending"}
                    </p>
                    {deployment.errorMessage && (
                      <p className="text-xs text-rose-400 mt-2">
                        ⚠️ {deployment.errorMessage}
                      </p>
                    )}
                  </div>
                  {deployment.screenshotUrl && (
                    <img
                      src={deployment.screenshotUrl}
                      alt="Website screenshot"
                      className="w-32 h-20 object-cover rounded-lg ml-4"
                    />
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

