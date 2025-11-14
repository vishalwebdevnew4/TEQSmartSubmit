"use client";

import { useEffect, useState } from "react";

interface Domain {
  id: number;
  url: string;
  category: string | null;
  isActive: boolean;
  createdAt: Date;
  templates: Array<{
    name: string;
  }>;
}

export default function DomainsPage() {
  const [domains, setDomains] = useState<Domain[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showBulkEnableModal, setShowBulkEnableModal] = useState(false);
  const [selectedDomain, setSelectedDomain] = useState<Domain | null>(null);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [formData, setFormData] = useState({
    url: "",
    category: "",
    isActive: true,
  });
  const [csvContent, setCsvContent] = useState("");
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    fetchDomains();
  }, []);

  const fetchDomains = async () => {
    try {
      const response = await fetch("/api/domains");
      if (response.ok) {
        const data = await response.json();
        setDomains(data);
      }
    } catch (error) {
      console.error("Failed to fetch domains:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = () => {
    setFormData({ url: "", category: "", isActive: true });
    setShowAddModal(true);
  };

  const handleEdit = (domain: Domain) => {
    setSelectedDomain(domain);
    setFormData({
      url: domain.url,
      category: domain.category || "",
      isActive: domain.isActive,
    });
    setShowEditModal(true);
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this domain?")) return;

    try {
      const response = await fetch(`/api/domains/${id}`, { method: "DELETE" });
      if (response.ok) {
        fetchDomains();
      } else {
        const error = await response.json();
        alert(error.detail || "Failed to delete domain");
      }
    } catch (error) {
      console.error("Failed to delete domain:", error);
      alert("Failed to delete domain");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setProcessing(true);
    try {
      const url = selectedDomain ? `/api/domains/${selectedDomain.id}` : "/api/domains";
      const method = selectedDomain ? "PUT" : "POST";

      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          url: formData.url,
          category: formData.category || null,
          isActive: formData.isActive,
        }),
      });

      if (response.ok) {
        setShowAddModal(false);
        setShowEditModal(false);
        setSelectedDomain(null);
        fetchDomains();
      } else {
        const error = await response.json();
        alert(error.detail || "Failed to save domain");
      }
    } catch (error) {
      console.error("Failed to save domain:", error);
      alert("Failed to save domain");
    } finally {
      setProcessing(false);
    }
  };

  const handleUploadCSV = async () => {
    if (!csvContent.trim()) {
      alert("Please paste CSV content");
      return;
    }

    setProcessing(true);
    try {
      const lines = csvContent.trim().split("\n");
      const urls: string[] = [];

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed) {
          // Support both comma and tab separated
          const parts = trimmed.split(/[,\t]/).map((p) => p.trim());
          // First column is usually the URL
          if (parts[0]) {
            urls.push(parts[0]);
          }
        }
      }

      if (urls.length === 0) {
        alert("No valid URLs found in CSV");
        return;
      }

      const response = await fetch("/api/domains/upload", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          urls,
          isActive: true,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        alert(result.message);
        setShowUploadModal(false);
        setCsvContent("");
        fetchDomains();
      } else {
        const error = await response.json();
        alert(error.detail || "Failed to upload domains");
      }
    } catch (error) {
      console.error("Failed to upload CSV:", error);
      alert("Failed to upload CSV");
    } finally {
      setProcessing(false);
    }
  };

  const handleBulkEnable = async () => {
    if (selectedIds.length === 0) {
      alert("Please select at least one domain");
      return;
    }

    setProcessing(true);
    try {
      const response = await fetch("/api/domains", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ids: selectedIds,
          isActive: true,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Updated ${result.count} domain(s)`);
        setShowBulkEnableModal(false);
        setSelectedIds([]);
        fetchDomains();
      } else {
        const error = await response.json();
        alert(error.detail || "Failed to bulk enable domains");
      }
    } catch (error) {
      console.error("Failed to bulk enable:", error);
      alert("Failed to bulk enable domains");
    } finally {
      setProcessing(false);
    }
  };

  const toggleSelect = (id: number) => {
    setSelectedIds((prev) => (prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]));
  };

  const toggleSelectAll = () => {
    if (selectedIds.length === domains.length) {
      setSelectedIds([]);
    } else {
      setSelectedIds(domains.map((d) => d.id));
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <header>
          <h2 className="text-2xl font-semibold text-white">Domain Manager</h2>
          <p className="text-sm text-slate-400">Manage the queue of domains for automated submissions.</p>
        </header>
        <div className="text-center text-slate-400">Loading domains...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <header>
        <h2 className="text-2xl font-semibold text-white">Domain Manager</h2>
        <p className="text-sm text-slate-400">Manage the queue of domains for automated submissions.</p>
      </header>

      <div className="flex flex-wrap gap-3">
        <button
          onClick={handleAdd}
          className="rounded-lg bg-indigo-500 px-4 py-2 text-xs font-medium text-white hover:bg-indigo-400"
        >
          Add Domain
        </button>
        <button
          onClick={() => setShowUploadModal(true)}
          className="rounded-lg border border-slate-700 px-4 py-2 text-xs font-medium text-slate-200 hover:bg-slate-800"
        >
          Upload CSV
        </button>
        <button
          onClick={() => setShowBulkEnableModal(true)}
          className="rounded-lg border border-slate-700 px-4 py-2 text-xs font-medium text-slate-200 hover:bg-slate-800"
        >
          Bulk Enable
        </button>
      </div>

      <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/60">
        <table className="min-w-full border-collapse text-left text-sm">
          <thead className="bg-slate-900/80 text-xs uppercase tracking-wide text-slate-400">
            <tr>
              <th className="px-6 py-4">
                <input
                  type="checkbox"
                  checked={selectedIds.length === domains.length && domains.length > 0}
                  onChange={toggleSelectAll}
                  className="rounded border-slate-600 bg-slate-800"
                />
              </th>
              <th className="px-6 py-4">Domain URL</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4">Category</th>
              <th className="px-6 py-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {domains.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-sm text-slate-400">
                  No domains found yet. Seed the database or add a domain to get started.
                </td>
              </tr>
            ) : (
              domains.map((domain) => {
                const templatePreview =
                  domain.templates.length > 0
                    ? domain.templates.map((template) => template.name).join(", ")
                    : null;

                return (
                  <tr key={domain.id} className="hover:bg-slate-900/80">
                    <td className="px-6 py-4">
                      <input
                        type="checkbox"
                        checked={selectedIds.includes(domain.id)}
                        onChange={() => toggleSelect(domain.id)}
                        className="rounded border-slate-600 bg-slate-800"
                      />
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-100">
                      <div>{domain.url}</div>
                      {templatePreview && (
                        <div className="mt-1 text-xs text-slate-400">
                          Templates: {templatePreview}
                          {domain.templates.length === 3 && "…"}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 text-xs">
                      <span
                        className={`rounded-full px-3 py-1 font-semibold ${
                          domain.isActive
                            ? "bg-emerald-500/10 text-emerald-300"
                            : "bg-slate-700/40 text-slate-300"
                        }`}
                      >
                        {domain.isActive ? "Active" : "Disabled"}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-300">{domain.category ?? "—"}</td>
                    <td className="px-6 py-4 text-right text-xs text-slate-400">
                      <button
                        onClick={() => handleEdit(domain)}
                        className="mr-3 hover:text-indigo-300"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(domain.id)}
                        className="hover:text-rose-300"
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Add Domain Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Add Domain</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Domain URL *</label>
                <input
                  type="url"
                  value={formData.url}
                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white"
                  placeholder="https://example.com"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Category</label>
                <input
                  type="text"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white"
                  placeholder="interior-design"
                />
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.isActive}
                  onChange={(e) => setFormData({ ...formData, isActive: e.target.checked })}
                  className="rounded border-slate-600 bg-slate-800"
                  id="isActive"
                />
                <label htmlFor="isActive" className="text-sm text-slate-300">
                  Active
                </label>
              </div>
              <div className="flex gap-3 justify-end">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={processing}
                  className="rounded-lg bg-indigo-500 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-400 disabled:opacity-50"
                >
                  {processing ? "Adding..." : "Add Domain"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Domain Modal */}
      {showEditModal && selectedDomain && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Edit Domain</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Domain URL *</label>
                <input
                  type="url"
                  value={formData.url}
                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">Category</label>
                <input
                  type="text"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white"
                />
              </div>
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.isActive}
                  onChange={(e) => setFormData({ ...formData, isActive: e.target.checked })}
                  className="rounded border-slate-600 bg-slate-800"
                  id="editIsActive"
                />
                <label htmlFor="editIsActive" className="text-sm text-slate-300">
                  Active
                </label>
              </div>
              <div className="flex gap-3 justify-end">
                <button
                  type="button"
                  onClick={() => {
                    setShowEditModal(false);
                    setSelectedDomain(null);
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
                  {processing ? "Saving..." : "Save Changes"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Upload CSV Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-2xl rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Upload CSV</h3>
            <p className="text-sm text-slate-400 mb-4">
              Paste CSV content with one URL per line. Each line can be comma or tab separated.
            </p>
            <textarea
              value={csvContent}
              onChange={(e) => setCsvContent(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white font-mono text-sm h-64"
              placeholder="https://example1.com&#10;https://example2.com&#10;https://example3.com"
            />
            <div className="flex gap-3 justify-end mt-4">
              <button
                onClick={() => {
                  setShowUploadModal(false);
                  setCsvContent("");
                }}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-slate-800"
              >
                Cancel
              </button>
              <button
                onClick={handleUploadCSV}
                disabled={processing || !csvContent.trim()}
                className="rounded-lg bg-indigo-500 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-400 disabled:opacity-50"
              >
                {processing ? "Uploading..." : "Upload"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Bulk Enable Modal */}
      {showBulkEnableModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Bulk Enable</h3>
            <p className="text-sm text-slate-400 mb-4">
              {selectedIds.length > 0
                ? `Enable ${selectedIds.length} selected domain(s)?`
                : "Select domains from the table using checkboxes, then click this button to enable them all."}
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowBulkEnableModal(false);
                  setSelectedIds([]);
                }}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-slate-800"
              >
                Cancel
              </button>
              <button
                onClick={handleBulkEnable}
                disabled={processing || selectedIds.length === 0}
                className="rounded-lg bg-indigo-500 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-400 disabled:opacity-50"
              >
                {processing ? "Enabling..." : "Enable Selected"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
