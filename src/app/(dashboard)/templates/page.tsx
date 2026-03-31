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
  const [fieldMappingsList, setFieldMappingsList] = useState<Array<{ key: string; value: string; type?: 'text' | 'number' | 'boolean' | 'object' }>>([]);
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
    setFieldMappingsList([]);
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
    // Convert field mappings object to array for easier editing
    const mappingsArray = Object.entries(template.fieldMappings || {}).map(([key, value]: [string, any]) => {
      let type: 'text' | 'number' | 'boolean' | 'object' = 'text';
      let stringValue = '';
      
      if (typeof value === 'boolean') {
        type = 'boolean';
        stringValue = String(value);
      } else if (typeof value === 'number') {
        type = 'number';
        stringValue = String(value);
      } else if (typeof value === 'object' && value !== null) {
        type = 'object';
        stringValue = JSON.stringify(value, null, 2);
      } else {
        stringValue = String(value);
      }
      
      return { key, value: stringValue, type };
    });
    setFieldMappingsList(mappingsArray.length > 0 ? mappingsArray : []);
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
      // Convert field mappings list to object
      const fieldMappings: Record<string, any> = {};
      for (const mapping of fieldMappingsList) {
        if (mapping.key.trim() && mapping.value.trim()) {
          // Try to parse value as JSON if it looks like JSON, otherwise use as string
          let parsedValue: any = mapping.value.trim();
          try {
            // Check if it's a JSON object/array/boolean/number
            if (mapping.value.trim().startsWith('{') || mapping.value.trim().startsWith('[') || 
                mapping.value.trim() === 'true' || mapping.value.trim() === 'false' ||
                (!isNaN(Number(mapping.value.trim())) && mapping.value.trim() !== '')) {
              parsedValue = JSON.parse(mapping.value.trim());
            }
          } catch {
            // If parsing fails, use as string
            parsedValue = mapping.value.trim();
          }
          fieldMappings[mapping.key.trim()] = parsedValue;
        }
      }
      
      if (Object.keys(fieldMappings).length === 0) {
        alert("Please add at least one field mapping");
        setProcessing(false);
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
        setFieldMappingsList([]);
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
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="w-full max-w-3xl rounded-xl border border-slate-800/50 bg-gradient-to-br from-slate-900/95 to-slate-900/80 backdrop-blur-sm p-6 max-h-[90vh] overflow-y-auto shadow-2xl">
            <div className="flex items-center gap-3 mb-6 pb-4 border-b border-slate-800/50">
              <div className="w-10 h-10 rounded-lg bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center">
                <span className="text-lg">{editingTemplate ? "✏️" : "➕"}</span>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-white">
                  {editingTemplate ? "Edit Template" : "New Template"}
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  {editingTemplate ? "Update template configuration" : "Create a new form template"}
                </p>
              </div>
            </div>
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-sm font-semibold text-slate-300 mb-2">Template Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full rounded-lg border border-slate-700/50 bg-slate-800/50 px-4 py-2.5 text-white placeholder-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 focus:bg-slate-800 transition-all"
                  placeholder="e.g., Default Contact Form"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-300 mb-2">Description</label>
                <input
                  type="text"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full rounded-lg border border-slate-700/50 bg-slate-800/50 px-4 py-2.5 text-white placeholder-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 focus:bg-slate-800 transition-all"
                  placeholder="Optional description for this template"
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-300 mb-2">
                  Domain (optional)
                </label>
                <p className="text-xs text-slate-400 mb-2">
                  Leave empty to create a universal template that works with all domains
                </p>
                <select
                  value={formData.domainId}
                  onChange={(e) => setFormData({ ...formData, domainId: e.target.value })}
                  className="w-full rounded-lg border border-slate-700/50 bg-slate-800/50 px-4 py-2.5 text-white focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 focus:bg-slate-800 transition-all cursor-pointer"
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
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-semibold text-slate-300">
                    Field Mappings *
                  </label>
                  <button
                    type="button"
                    onClick={() => setFieldMappingsList([...fieldMappingsList, { key: "", value: "", type: 'text' }])}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-indigo-600/50 bg-indigo-500/10 px-3 py-1.5 text-xs font-medium text-indigo-300 hover:bg-indigo-500/20 transition-all"
                  >
                    <span>➕</span>
                    Add Field
                  </button>
                </div>
                <p className="text-xs text-slate-400 mb-3">
                  Configure field mappings and settings. Values can be text, numbers, booleans, or JSON objects.
                </p>
                
                {fieldMappingsList.length === 0 ? (
                  <div className="rounded-lg border-2 border-dashed border-slate-700/50 bg-slate-800/30 p-8 text-center">
                    <p className="text-sm text-slate-400 mb-3">No field mappings added yet</p>
                    <button
                      type="button"
                      onClick={() => setFieldMappingsList([{ key: "", value: "", type: 'text' }])}
                      className="inline-flex items-center gap-2 rounded-lg bg-indigo-500/10 border border-indigo-600/50 px-4 py-2 text-sm font-medium text-indigo-300 hover:bg-indigo-500/20 transition-all"
                    >
                      <span>➕</span>
                      Add Your First Field Mapping
                    </button>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {fieldMappingsList.map((mapping, index) => {
                      const detectedType = mapping.type || (() => {
                        const val = mapping.value.trim();
                        if (val === 'true' || val === 'false') return 'boolean';
                        if (!isNaN(Number(val)) && val !== '') return 'number';
                        if (val.startsWith('{') || val.startsWith('[')) return 'object';
                        return 'text';
                      })();
                      
                      return (
                        <div key={index} className="rounded-lg border border-slate-700/50 bg-slate-800/50 p-4">
                          <div className="grid grid-cols-[1.2fr_1fr_0.8fr_auto] gap-3 items-start">
                            <div>
                              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                                Field Name
                              </label>
                              <input
                                type="text"
                                value={mapping.key}
                                onChange={(e) => {
                                  const newList = [...fieldMappingsList];
                                  newList[index].key = e.target.value;
                                  setFieldMappingsList(newList);
                                }}
                                className="w-full rounded-lg border border-slate-700/50 bg-slate-900/50 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 focus:bg-slate-900 transition-all"
                                placeholder="e.g., name, email, captcha"
                              />
                            </div>
                            <div>
                              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                                Value Type
                              </label>
                              <select
                                value={detectedType}
                                onChange={(e) => {
                                  const newList = [...fieldMappingsList];
                                  newList[index].type = e.target.value as any;
                                  // Reset value if switching types
                                  if (e.target.value === 'boolean') {
                                    newList[index].value = 'true';
                                  } else if (e.target.value === 'number') {
                                    newList[index].value = '0';
                                  } else if (e.target.value === 'object') {
                                    newList[index].value = '{}';
                                  } else {
                                    newList[index].value = '';
                                  }
                                  setFieldMappingsList(newList);
                                }}
                                className="w-full rounded-lg border border-slate-700/50 bg-slate-900/50 px-3 py-2 text-xs text-white focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 focus:bg-slate-900 transition-all cursor-pointer"
                              >
                                <option value="text">Text / CSS Selector</option>
                                <option value="number">Number</option>
                                <option value="boolean">Boolean (true/false)</option>
                                <option value="object">JSON Object/Array</option>
                              </select>
                            </div>
                            <div>
                              <label className="block text-xs font-semibold text-slate-300 mb-1.5">
                                {detectedType === 'boolean' ? 'Boolean Value' : 
                                 detectedType === 'number' ? 'Number Value' :
                                 detectedType === 'object' ? 'JSON Value' :
                                 'Value / CSS Selector'}
                              </label>
                              {detectedType === 'boolean' ? (
                                <select
                                  value={mapping.value}
                                  onChange={(e) => {
                                    const newList = [...fieldMappingsList];
                                    newList[index].value = e.target.value;
                                    setFieldMappingsList(newList);
                                  }}
                                  className="w-full rounded-lg border border-slate-700/50 bg-slate-900/50 px-3 py-2 text-sm text-white focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 focus:bg-slate-900 transition-all cursor-pointer"
                                >
                                  <option value="true">true</option>
                                  <option value="false">false</option>
                                </select>
                              ) : detectedType === 'number' ? (
                                <input
                                  type="number"
                                  value={mapping.value}
                                  onChange={(e) => {
                                    const newList = [...fieldMappingsList];
                                    newList[index].value = e.target.value;
                                    setFieldMappingsList(newList);
                                  }}
                                  className="w-full rounded-lg border border-slate-700/50 bg-slate-900/50 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 focus:bg-slate-900 transition-all"
                                  placeholder="e.g., 600000"
                                />
                              ) : detectedType === 'object' ? (
                                <textarea
                                  value={mapping.value}
                                  onChange={(e) => {
                                    const newList = [...fieldMappingsList];
                                    newList[index].value = e.target.value;
                                    setFieldMappingsList(newList);
                                  }}
                                  className="w-full rounded-lg border border-slate-700/50 bg-slate-900/50 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 focus:bg-slate-900 transition-all font-mono h-20 resize-y"
                                  placeholder='{"key": "value"} or [...]'
                                />
                              ) : (
                                <input
                                  type="text"
                                  value={mapping.value}
                                  onChange={(e) => {
                                    const newList = [...fieldMappingsList];
                                    newList[index].value = e.target.value;
                                    setFieldMappingsList(newList);
                                  }}
                                  className="w-full rounded-lg border border-slate-700/50 bg-slate-900/50 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 focus:bg-slate-900 transition-all font-mono"
                                  placeholder='e.g., input[name="name"], #email, or any text'
                                />
                              )}
                            </div>
                            <div className="pt-6">
                              <button
                                type="button"
                                onClick={() => {
                                  const newList = fieldMappingsList.filter((_, i) => i !== index);
                                  setFieldMappingsList(newList);
                                }}
                                className="rounded-lg border border-rose-600/50 bg-rose-500/10 px-3 py-2 text-xs font-medium text-rose-300 hover:bg-rose-500/20 transition-all"
                                title="Remove this field mapping"
                              >
                                🗑️
                              </button>
                            </div>
                          </div>
                          {mapping.key && mapping.value && (
                            <div className="mt-3 flex items-center gap-2 text-xs">
                              <span className="text-slate-400">Preview:</span>
                              <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-950/50 border border-slate-800/50">
                                <span className="font-semibold text-indigo-300">{mapping.key}</span>
                                <span className="text-slate-600">→</span>
                                {detectedType === 'object' ? (
                                  <span className="text-emerald-300 font-mono text-[10px]">
                                    {(() => {
                                      try {
                                        const parsed = JSON.parse(mapping.value);
                                        if (typeof parsed === 'object' && parsed !== null) {
                                          const keys = Object.keys(parsed);
                                          return keys.length > 0 
                                            ? `{${keys.length} ${keys.length === 1 ? 'key' : 'keys'}}`
                                            : '{}';
                                        }
                                      } catch {}
                                      return 'JSON';
                                    })()}
                                  </span>
                                ) : detectedType === 'boolean' ? (
                                  <span className={`font-semibold ${mapping.value === 'true' ? 'text-emerald-400' : 'text-rose-400'}`}>
                                    {mapping.value}
                                  </span>
                                ) : detectedType === 'number' ? (
                                  <span className="text-blue-300 font-mono">
                                    {mapping.value}
                                  </span>
                                ) : (
                                  <span className="text-emerald-300 font-mono text-[10px] max-w-[200px] truncate" title={mapping.value}>
                                    {mapping.value.length > 30 ? mapping.value.substring(0, 30) + '...' : mapping.value}
                                  </span>
                                )}
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
                
                <div className="mt-4 rounded-lg border border-slate-800/50 bg-gradient-to-br from-indigo-950/30 to-slate-950/50 p-4">
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-lg">💡</span>
                    <p className="text-xs font-semibold text-slate-300">Common CSS Selectors:</p>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-xs">
                    <div className="flex items-start gap-2">
                      <span className="text-indigo-400 mt-0.5">•</span>
                      <div>
                        <code className="text-indigo-300 font-mono">input[name="name"]</code>
                        <span className="text-slate-500 ml-2">By name attribute</span>
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="text-indigo-400 mt-0.5">•</span>
                      <div>
                        <code className="text-indigo-300 font-mono">#email</code>
                        <span className="text-slate-500 ml-2">By ID</span>
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="text-indigo-400 mt-0.5">•</span>
                      <div>
                        <code className="text-indigo-300 font-mono">input[type="email"]</code>
                        <span className="text-slate-500 ml-2">By type</span>
                      </div>
                    </div>
                    <div className="flex items-start gap-2">
                      <span className="text-indigo-400 mt-0.5">•</span>
                      <div>
                        <code className="text-indigo-300 font-mono">textarea</code>
                        <span className="text-slate-500 ml-2">By tag name</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="flex gap-3 justify-end pt-4 border-t border-slate-800/50">
                <button
                  type="button"
                  onClick={() => {
                    setShowModal(false);
                    setEditingTemplate(null);
                    setFieldMappingsList([]);
                  }}
                  className="inline-flex items-center gap-2 rounded-lg border border-slate-700/50 bg-slate-800/50 px-4 py-2.5 text-sm font-medium text-slate-200 hover:bg-slate-700/50 transition-all"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={processing}
                  className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-indigo-500 to-indigo-600 px-4 py-2.5 text-sm font-medium text-white hover:from-indigo-400 hover:to-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md"
                >
                  {processing ? (
                    <>
                      <span className="animate-spin">⏳</span>
                      Saving...
                    </>
                  ) : editingTemplate ? (
                    <>
                      <span>💾</span>
                      Update Template
                    </>
                  ) : (
                    <>
                      <span>✨</span>
                      Create Template
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
      </div>
      )}
    </div>
  );
}
