"use client";

import { useEffect, useState } from "react";

interface Template {
  id: number;
  name: string;
  description: string | null;
  fieldMappings: Record<string, string>;
  createdAt: Date;
  updatedAt: Date;
  domainId: number | null;
  domain?: {
    id: number;
    url: string;
  };
}

interface Domain {
  id: number;
  url: string;
}

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [filteredTemplates, setFilteredTemplates] = useState<Template[]>([]);
  const [domains, setDomains] = useState<Domain[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<Template | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState<"all" | "universal" | "domain">("all");
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    domainId: "",
    fieldMappings: "{}",
  });
  const [fieldMappingsList, setFieldMappingsList] = useState<Array<{ key: string; value: string }>>([]);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    fetchTemplates();
    fetchDomains();
  }, []);

  const fetchTemplates = async () => {
    try {
      const response = await fetch("/api/templates");
      if (response.ok) {
        const data = await response.json();
        setTemplates(data);
        setFilteredTemplates(data);
      }
    } catch (error) {
      console.error("Failed to fetch templates:", error);
    } finally {
      setLoading(false);
    }
  };

  // Filter templates based on search and type
  useEffect(() => {
    let filtered = templates;

    // Filter by type
    if (filterType === "universal") {
      filtered = filtered.filter(t => t.domainId === null);
    } else if (filterType === "domain") {
      filtered = filtered.filter(t => t.domainId !== null);
    }

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(t => 
        t.name.toLowerCase().includes(query) ||
        t.description?.toLowerCase().includes(query) ||
        Object.keys(t.fieldMappings).some(key => key.toLowerCase().includes(query))
      );
    }

    setFilteredTemplates(filtered);
  }, [templates, searchQuery, filterType]);

  const fetchDomains = async () => {
    try {
      const response = await fetch("/api/domains");
      if (response.ok) {
        const data = await response.json();
        setDomains(data);
      }
    } catch (error) {
      console.error("Failed to fetch domains:", error);
    }
  };

  const handleCreate = () => {
    setEditingTemplate(null);
    setFormData({
      name: "",
      description: "",
      domainId: "",
      fieldMappings: "{}",
    });
    setShowModal(true);
  };

  const handleEdit = (template: Template) => {
    setEditingTemplate(template);
    setFormData({
      name: template.name,
      description: template.description || "",
      domainId: template.domainId?.toString() || "",
      fieldMappings: JSON.stringify(template.fieldMappings, null, 2),
    });
    setShowModal(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this template?")) return;

    try {
      const response = await fetch(`/api/templates/${id}`, { method: "DELETE" });
      if (response.ok) {
        fetchTemplates();
      } else {
        const error = await response.json();
        alert(error.detail || "Failed to delete template");
      }
    } catch (error) {
      console.error("Failed to delete template:", error);
      alert("Failed to delete template");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setProcessing(true);
    try {
      let fieldMappings;
      try {
        fieldMappings = JSON.parse(formData.fieldMappings);
        // Validate that it's an object
        if (typeof fieldMappings !== "object" || Array.isArray(fieldMappings)) {
          alert("Field mappings must be a valid JSON object");
          return;
        }
      } catch {
        alert("Invalid JSON in field mappings");
        return;
      }

      const url = editingTemplate ? `/api/templates/${editingTemplate.id}` : "/api/templates";
      const method = editingTemplate ? "PUT" : "POST";

      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: formData.name,
          description: formData.description || null,
          fieldMappings: fieldMappings,
          domainId: formData.domainId || null,
        }),
      });

      if (response.ok) {
        setShowModal(false);
        setEditingTemplate(null);
        fetchTemplates();
      } else {
        const error = await response.json();
        alert(error.detail || "Failed to save template");
      }
    } catch (error) {
      console.error("Failed to save template:", error);
      alert("Failed to save template");
    } finally {
      setProcessing(false);
    }
  };

  const formatFieldMappings = (mappings: Record<string, string>): string => {
    if (!mappings || Object.keys(mappings).length === 0) {
      return "No field mappings defined";
    }
    return Object.entries(mappings)
      .map(([key, value]) => `${key} - ${value}`)
      .join(", ");
  };

  const getFieldKeys = (mappings: Record<string, string>): string[] => {
    if (!mappings || typeof mappings !== "object") {
      return [];
    }
    return Object.keys(mappings);
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <header>
          <h2 className="text-2xl font-semibold text-white">Form Templates</h2>
          <p className="text-sm text-slate-400">Create reusable mappings that the automation engine relies on.</p>
        </header>
        <div className="text-center text-slate-400">Loading templates...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <header>
        <h2 className="text-2xl font-semibold text-white">Form Templates</h2>
        <p className="text-sm text-slate-400">Create reusable mappings that the automation engine relies on.</p>
      </header>

      <div className="rounded-xl border border-slate-800/50 bg-gradient-to-br from-slate-900/80 to-slate-900/40 backdrop-blur-sm p-5 shadow-lg">
        <div className="flex flex-wrap gap-4 items-end">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-xs font-semibold text-slate-300 mb-2 tracking-wide">Search Templates</label>
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search templates..."
                className="w-full rounded-lg border border-slate-700/50 bg-slate-800/50 px-4 py-2.5 text-sm text-white placeholder-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 focus:bg-slate-800 transition-all"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery("")}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
                >
                  ✕
                </button>
              )}
            </div>
          </div>
          
          <div className="min-w-[150px]">
            <label className="block text-xs font-semibold text-slate-300 mb-2 tracking-wide">Filter Type</label>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value as "all" | "universal" | "domain")}
              className="w-full rounded-lg border border-slate-700/50 bg-slate-800/50 px-4 py-2.5 text-sm text-white focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 focus:bg-slate-800 transition-all cursor-pointer"
            >
              <option value="all">All Templates</option>
              <option value="universal">Universal Only</option>
              <option value="domain">Domain-Specific</option>
            </select>
          </div>

          <button
            onClick={handleCreate}
            className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-indigo-500 to-indigo-600 px-4 py-2.5 text-sm font-medium text-white hover:from-indigo-400 hover:to-indigo-500 transition-all shadow-sm hover:shadow-md"
          >
            <span>➕</span>
            New Template
          </button>
        </div>
      </div>

      {templates.length > 0 && (
        <div className="rounded-xl border border-slate-800/50 bg-gradient-to-br from-slate-900/80 to-slate-900/40 backdrop-blur-sm p-4 shadow-lg">
          <div className="flex items-center gap-4 text-sm text-slate-300 mb-4">
            <span className="font-semibold">Total: <span className="text-white font-bold">{templates.length}</span></span>
            <span>Universal: <span className="text-indigo-300 font-medium">{templates.filter(t => t.domainId === null).length}</span></span>
            <span>Domain-Specific: <span className="text-emerald-300 font-medium">{templates.filter(t => t.domainId !== null).length}</span></span>
            {searchQuery && (
              <span className="text-slate-500">
                Showing {filteredTemplates.length} of {templates.length}
              </span>
            )}
          </div>
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        {filteredTemplates.length === 0 ? (
          <div className="col-span-2 rounded-xl border border-slate-800/50 bg-gradient-to-br from-slate-900/80 to-slate-900/40 backdrop-blur-sm p-8 text-center shadow-lg">
            <p className="text-sm text-slate-300">
              {templates.length === 0 
                ? "No templates found. Create your first template to get started."
                : searchQuery || filterType !== "all"
                ? "No templates match your filters."
                : "No templates found."}
            </p>
          </div>
        ) : (
          filteredTemplates.map((template) => {
            const fields = getFieldKeys(template.fieldMappings);
            const preview = formatFieldMappings(template.fieldMappings);

            return (
              <div key={template.id} className="space-y-3 rounded-xl border border-slate-800/50 bg-gradient-to-br from-slate-900/80 to-slate-900/40 backdrop-blur-sm p-6 shadow-lg hover:border-slate-700 transition-all">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-white">{template.name}</h3>
                    <p className="text-xs text-slate-500">
                      Last updated {new Date(template.updatedAt).toLocaleDateString()}
                    </p>
                    {template.domain ? (
                      <p className="text-xs text-slate-500 mt-1">Domain: {template.domain.url}</p>
                    ) : (
                      <p className="text-xs text-indigo-400 mt-1">🌐 Universal Template (works with all domains)</p>
                    )}
              </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEdit(template)}
                      className="inline-flex items-center gap-1.5 rounded-lg border border-indigo-600/50 bg-indigo-500/10 px-3 py-1.5 text-xs font-medium text-indigo-300 hover:bg-indigo-500/20 transition-all"
                    >
                      <span>✏️</span>
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(template.id)}
                      className="inline-flex items-center gap-1.5 rounded-lg border border-rose-600/50 bg-rose-500/10 px-3 py-1.5 text-xs font-medium text-rose-300 hover:bg-rose-500/20 transition-all"
                    >
                      <span>🗑️</span>
                      Delete
                    </button>
                  </div>
            </div>
                {template.description && (
                  <p className="text-sm text-slate-300">{template.description}</p>
                )}
            <div className="rounded-lg border border-slate-800/50 bg-slate-950/50 p-4">
              <p className="text-xs font-semibold text-slate-300 uppercase tracking-wide mb-3">Mapped Fields</p>
              <div className="flex flex-wrap gap-2">
                    {fields.length > 0 ? (
                      fields.map((field) => (
                  <span key={field} className="inline-flex items-center gap-1 rounded-full bg-indigo-500/20 border border-indigo-500/30 px-3 py-1.5 text-xs font-medium text-indigo-300">
                    <span className="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
                    {field}
                  </span>
                      ))
                    ) : (
                      <span className="text-slate-500 text-xs">No fields mapped</span>
                    )}
              </div>
            </div>
            <div className="text-xs text-slate-400">
              <p>Preview:</p>
                  <p className="mt-1 line-clamp-2 text-slate-300 font-mono text-xs">{preview}</p>
                </div>
              </div>
            );
          })
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-2xl rounded-2xl border border-slate-800 bg-slate-900 p-6 max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-semibold text-white mb-4">
              {editingTemplate ? "Edit Template" : "New Template"}
            </h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white"
                  placeholder="Default Contact Form"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Description</label>
                <input
                  type="text"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white"
                  placeholder="Optional description"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">
                  Domain (optional)
                  <span className="ml-2 text-xs text-slate-500 font-normal">
                    Leave empty to create a universal template that works with all domains
                  </span>
                </label>
                <select
                  value={formData.domainId}
                  onChange={(e) => setFormData({ ...formData, domainId: e.target.value })}
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white"
                >
                  <option value="">🌐 Universal (all domains)</option>
                  {domains.map((domain) => (
                    <option key={domain.id} value={domain.id}>
                      {domain.url}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">
                  Field Mappings (JSON) *
                  <span className="ml-2 text-xs text-slate-500 font-normal">
                    Format: {`{"fieldName": "selector"}`}
                  </span>
                </label>
                <textarea
                  value={formData.fieldMappings}
                  onChange={(e) => setFormData({ ...formData, fieldMappings: e.target.value })}
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white font-mono text-sm h-48"
                  placeholder='{"name": "input[name=\\"fullname\\"]", "email": "input#email", "message": "textarea[name=\\"message\\"]"}'
                  required
                />
                <p className="mt-1 text-xs text-slate-500">
                  Example: {`{"name": "input[name='name']", "email": "input#email", "message": "textarea"}`}
              </p>
            </div>
              <div className="flex gap-3 justify-end">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    setEditingTemplate(null);
                  }}
                  className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={processing}
                  className="rounded-lg bg-indigo-500 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-400 disabled:opacity-50"
                >
                  {processing ? "Saving..." : editingTemplate ? "Update" : "Create"}
                </button>
              </div>
            </form>
          </div>
      </div>
      )}
    </div>
  );
}
