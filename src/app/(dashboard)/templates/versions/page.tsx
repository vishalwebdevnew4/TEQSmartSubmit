"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export default function TemplateVersionsPage() {
  const [templates, setTemplates] = useState<any[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<any>(null);
  const [versions, setVersions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    fetchTemplates();
  }, []);

  useEffect(() => {
    if (selectedTemplate) {
      fetchVersions(selectedTemplate.id);
    }
  }, [selectedTemplate]);

  const fetchTemplates = async () => {
    try {
      const res = await fetch("/api/templates");
      const data = await res.json();
      setTemplates(data);
      if (data.length > 0 && !selectedTemplate) {
        setSelectedTemplate(data[0]);
      }
    } catch (error) {
      console.error("Failed to fetch templates:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchVersions = async (templateId: number) => {
    try {
      const res = await fetch(`/api/templates/${templateId}/versions`);
      const data = await res.json();
      setVersions(data);
    } catch (error) {
      console.error("Failed to fetch versions:", error);
    }
  };

  const handleRollback = async (versionId: number) => {
    if (!confirm("Are you sure you want to rollback to this version?")) {
      return;
    }

    try {
      const res = await fetch(`/api/templates/versions/${versionId}/rollback`, {
        method: "POST",
      });
      const data = await res.json();
      
      if (data.success) {
        alert("Template rolled back successfully");
        fetchVersions(selectedTemplate.id);
      } else {
        alert(data.error || "Failed to rollback");
      }
    } catch (error) {
      alert("Error rolling back template");
    }
  };

  return (
    <div className="space-y-8">
      <header className="flex flex-col gap-2">
        <h2 className="text-2xl font-semibold text-white">Template Versions</h2>
        <p className="text-sm text-slate-400">Manage template versions and rollback</p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Template Selector */}
        <div className="lg:col-span-1">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Templates</h3>
            {loading ? (
              <div className="text-center py-4 text-slate-400">Loading...</div>
            ) : templates.length === 0 ? (
              <div className="text-center py-4 text-slate-400">No templates found</div>
            ) : (
              <div className="space-y-2">
                {templates.map((template) => (
                  <button
                    key={template.id}
                    onClick={() => setSelectedTemplate(template)}
                    className={`w-full text-left rounded-lg px-4 py-3 transition-colors ${
                      selectedTemplate?.id === template.id
                        ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/30"
                        : "bg-slate-800/50 text-slate-300 hover:bg-slate-800 border border-slate-700"
                    }`}
                  >
                    <div className="font-medium">{template.name}</div>
                    {template.business && (
                      <div className="text-xs text-slate-400 mt-1">
                        {template.business.name}
                      </div>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Versions List */}
        <div className="lg:col-span-2">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">
                Versions {selectedTemplate && `- ${selectedTemplate.name}`}
              </h3>
            </div>
            {!selectedTemplate ? (
              <div className="text-center py-8 text-slate-400">
                Select a template to view versions
              </div>
            ) : versions.length === 0 ? (
              <div className="text-center py-8 text-slate-400">No versions found</div>
            ) : (
              <div className="space-y-4">
                {versions.map((version) => (
                  <div
                    key={version.id}
                    className="rounded-lg border border-slate-700 bg-slate-800/50 p-4"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="text-lg font-semibold text-white">
                            Version {version.version}
                          </span>
                          {version.isActive && (
                            <span className="rounded-full px-3 py-1 text-xs font-medium bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                              Active
                            </span>
                          )}
                          {version.aiCopyStyle && (
                            <span className="text-xs text-slate-400">
                              Style: {version.aiCopyStyle}
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-slate-400">
                          Created: {new Date(version.createdAt).toLocaleString()}
                        </p>
                        {version.deployedAt && (
                          <p className="text-sm text-slate-400">
                            Deployed: {new Date(version.deployedAt).toLocaleString()}
                          </p>
                        )}
                        {version.screenshotUrl && (
                          <img
                            src={version.screenshotUrl}
                            alt="Version screenshot"
                            className="w-32 h-20 object-cover rounded-lg mt-2"
                          />
                        )}
                      </div>
                      <div className="flex gap-2 ml-4">
                        {!version.isActive && (
                          <button
                            onClick={() => handleRollback(version.id)}
                            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
                          >
                            Rollback
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

