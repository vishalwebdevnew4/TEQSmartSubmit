"use client";

import { useEffect, useState } from "react";

interface Domain {
  id: number;
  url: string;
  category: string | null;
  isActive: boolean;
  contactPageUrl: string | null;
  contactCheckStatus: string | null;
  contactCheckedAt: Date | null;
  contactCheckMessage: string | null;
  createdAt: Date;
  templates: Array<{
    name: string;
  }>;
}

export default function DomainsPage() {
  const [allDomains, setAllDomains] = useState<Domain[]>([]);
  const [domains, setDomains] = useState<Domain[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showBulkEnableModal, setShowBulkEnableModal] = useState(false);
  const [showBulkDisableModal, setShowBulkDisableModal] = useState(false);
  const [showBulkDeleteModal, setShowBulkDeleteModal] = useState(false);
  const [showDeleteAllModal, setShowDeleteAllModal] = useState(false);
  const [selectedDomain, setSelectedDomain] = useState<Domain | null>(null);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [formData, setFormData] = useState({
    url: "",
    category: "",
    isActive: true,
  });
  const [csvContent, setCsvContent] = useState("");
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [uploadMode, setUploadMode] = useState<"paste" | "file">("paste");
  const [processing, setProcessing] = useState(false);
  
  // Filter states
  const [statusFilter, setStatusFilter] = useState<"all" | "active" | "disabled">("all");
  const [categoryFilter, setCategoryFilter] = useState<string>("all");
  const [contactStatusFilter, setContactStatusFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState<string>("");
  
  // Pagination states
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(25);
  const [filteredDomains, setFilteredDomains] = useState<Domain[]>([]);

  useEffect(() => {
    fetchDomains();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [allDomains, statusFilter, categoryFilter, contactStatusFilter, searchQuery]);

  useEffect(() => {
    // Reset to page 1 when filters change
    setCurrentPage(1);
  }, [statusFilter, categoryFilter, contactStatusFilter, searchQuery]);

  const fetchDomains = async () => {
    try {
      // Fetch all domains by setting a high limit
      const response = await fetch("/api/domains?limit=10000");
      if (response.ok) {
        const data = await response.json();
        setAllDomains(data);
        setDomains(data);
      }
    } catch (error) {
      console.error("Failed to fetch domains:", error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...allDomains];

    // Apply status filter
    if (statusFilter === "active") {
      filtered = filtered.filter((d) => d.isActive);
    } else if (statusFilter === "disabled") {
      filtered = filtered.filter((d) => !d.isActive);
    }

    // Apply category filter
    if (categoryFilter !== "all") {
      filtered = filtered.filter((d) => d.category === categoryFilter);
    }

    // Apply search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter((d) => d.url.toLowerCase().includes(query));
    }

    // Apply contact status filter
    if (contactStatusFilter !== "all") {
      filtered = filtered.filter((d) => d.contactCheckStatus === contactStatusFilter);
    }

    setFilteredDomains(filtered);
  };

  useEffect(() => {
    // Apply pagination whenever filteredDomains, currentPage, or itemsPerPage changes
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    setDomains(filteredDomains.slice(startIndex, endIndex));
  }, [currentPage, itemsPerPage, filteredDomains]);

  // Get unique categories for filter dropdown
  const uniqueCategories = Array.from(
    new Set(allDomains.map((d) => d.category).filter((c) => c !== null))
  ).sort() as string[];

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
        await fetchDomains();
      } else {
        const error = await response.json();
        alert(error.detail || "Failed to delete domain");
      }
    } catch (error) {
      console.error("Failed to delete domain:", error);
      alert("Failed to delete domain");
    } finally {
      setProcessing(false);
    }
  };

  const handleRecheckContact = async (domain: Domain) => {
    if (processing) return;
    
    setProcessing(true);
    try {
      // Show a message that this may take up to 2 minutes (Playwright waits for page loading)
      alert("Re-checking contact page... This may take up to 2 minutes. The system will use Playwright to verify the contact page link. Please wait.");
      
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 180000); // 3 minutes timeout (increased for Playwright waits)
      
      const response = await fetch("/api/domains/check-contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ domainIds: [domain.id] }),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        const data = await response.json();
        alert(`Re-check completed: ${data.message}`);
        await fetchDomains();
      } else {
        const error = await response.json();
        alert(error.detail || "Failed to re-check contact page");
      }
    } catch (error: any) {
      console.error("Failed to re-check contact page:", error);
      if (error.name === 'AbortError') {
        alert("Request timed out. The check is taking longer than expected. Please try again.");
      } else {
        alert("Failed to re-check contact page: " + (error.message || "Unknown error"));
      }
    } finally {
      setProcessing(false);
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
        await fetchDomains();
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

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setCsvFile(file);
    
    // Read file content
    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result as string;
      setCsvContent(content);
    };
    reader.readAsText(file);
  };

  const handleDownloadSample = () => {
    const sampleCSV = `url,category
https://example1.com,interior-design
https://example2.com,web-design
https://example3.com,marketing`;
    
    const blob = new Blob([sampleCSV], { type: "text/csv" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "domains-sample.csv";
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  };

  const handleUploadCSV = async () => {
    let content = csvContent.trim();
    
    if (uploadMode === "file" && csvFile) {
      // File content is already loaded in csvContent
      if (!content) {
        alert("Please select a CSV file");
        return;
      }
    } else {
      if (!content) {
        alert("Please paste CSV content or upload a file");
        return;
      }
    }

    setProcessing(true);
    try {
      const lines = content.split("\n").filter(line => line.trim());
      if (lines.length === 0) {
        alert("No data found in CSV");
        return;
      }

      const domains: Array<{ url: string; category: string | null }> = [];
      let hasHeaders = false;
      
      // Check if first line looks like headers
      const firstLine = lines[0].toLowerCase();
      if (firstLine.includes("url") || firstLine.includes("domain") || firstLine.includes("category")) {
        hasHeaders = true;
      }

      // Start from line 1 if headers exist
      const dataLines = hasHeaders ? lines.slice(1) : lines;

      for (const line of dataLines) {
        const trimmed = line.trim();
        if (!trimmed) continue;

        // Support both comma and tab separated
        const parts = trimmed.split(/[,\t]/).map((p) => p.trim());
        
        if (parts[0]) {
          const url = parts[0];
          const category = parts[1] || null;
          
          // Validate URL format
          try {
            new URL(url);
            domains.push({ url, category });
          } catch {
            // Skip invalid URLs
            console.warn(`Invalid URL skipped: ${url}`);
          }
        }
      }

      if (domains.length === 0) {
        alert("No valid URLs found in CSV");
        return;
      }

      // Group by category for batch upload
      const urls = domains.map(d => d.url);
      const categories = domains.map(d => d.category);

      const response = await fetch("/api/domains/upload", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          urls,
          categories,
          isActive: true,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        alert(result.message);
        setShowUploadModal(false);
        setCsvContent("");
        setCsvFile(null);
        await fetchDomains();
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
        await fetchDomains();
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

  const handleBulkDisable = async () => {
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
          isActive: false,
        }),
  });

      if (response.ok) {
        const result = await response.json();
        alert(`Updated ${result.count} domain(s)`);
        setShowBulkDisableModal(false);
        setSelectedIds([]);
        await fetchDomains();
      } else {
        const error = await response.json();
        alert(error.detail || "Failed to bulk disable domains");
      }
    } catch (error) {
      console.error("Failed to bulk disable:", error);
      alert("Failed to bulk disable domains");
    } finally {
      setProcessing(false);
    }
  };

  const handleBulkDelete = async () => {
    if (selectedIds.length === 0) {
      alert("Please select at least one domain");
      return;
    }

    setProcessing(true);
    try {
      const response = await fetch("/api/domains", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ids: selectedIds,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Successfully deleted ${result.count} domain(s)`);
        setShowBulkDeleteModal(false);
        setSelectedIds([]);
        await fetchDomains();
      } else {
        const error = await response.json();
        alert(error.detail || "Failed to bulk delete domains");
      }
    } catch (error) {
      console.error("Failed to bulk delete:", error);
      alert("Failed to bulk delete domains");
    } finally {
      setProcessing(false);
    }
  };

  const handleDeleteAll = async () => {
    // Get all domain IDs from filtered domains (respects current filters)
    const allFilteredIds = filteredDomains.map((d) => d.id);
    
    if (allFilteredIds.length === 0) {
      alert("No domains to delete");
      return;
    }

    setProcessing(true);
    try {
      const response = await fetch("/api/domains", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ids: allFilteredIds,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Successfully deleted ${result.count} domain(s)`);
        setShowDeleteAllModal(false);
        setSelectedIds([]);
        await fetchDomains();
      } else {
        const error = await response.json();
        alert(error.detail || "Failed to delete all domains");
      }
    } catch (error) {
      console.error("Failed to delete all:", error);
      alert("Failed to delete all domains");
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

  const handleDownloadFailedDomains = async () => {
    try {
      // Download all failed statuses
      const statuses = ["not_found", "no_form", "error"];
      for (const status of statuses) {
        const response = await fetch(`/api/domains/failed-export?status=${status}`);
        if (response.ok) {
          const blob = await response.blob();
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = `failed-domains-${status}-${new Date().toISOString().split("T")[0]}.csv`;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
        }
      }
    } catch (error) {
      console.error("Failed to download failed domains:", error);
      alert("Failed to download failed domains");
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

      {/* Filter Controls */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
        <div className="flex flex-wrap gap-4 items-end">
          {/* Search by URL */}
          <div className="flex-1 min-w-[200px]">
            <label className="block text-xs font-medium text-slate-400 mb-1">Search by URL</label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search domains..."
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white placeholder-slate-500 focus:border-indigo-500 focus:outline-none"
            />
          </div>

          {/* Status Filter */}
          <div className="min-w-[150px]">
            <label className="block text-xs font-medium text-slate-400 mb-1">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as "all" | "active" | "disabled")}
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white focus:border-indigo-500 focus:outline-none"
            >
              <option value="all">All</option>
              <option value="active">Active</option>
              <option value="disabled">Disabled</option>
            </select>
          </div>

          {/* Category Filter */}
          <div className="min-w-[150px]">
            <label className="block text-xs font-medium text-slate-400 mb-1">Category</label>
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white focus:border-indigo-500 focus:outline-none"
            >
              <option value="all">All Categories</option>
              {uniqueCategories.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>

          {/* Contact Status Filter */}
          <div className="min-w-[150px]">
            <label className="block text-xs font-medium text-slate-400 mb-1">Contact Status</label>
            <select
              value={contactStatusFilter}
              onChange={(e) => setContactStatusFilter(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white focus:border-indigo-500 focus:outline-none"
            >
              <option value="all">All</option>
              <option value="pending">Pending</option>
              <option value="found">Found</option>
              <option value="not_found">Not Found</option>
              <option value="no_form">No Contact Form</option>
              <option value="error">Error</option>
            </select>
          </div>

          {/* Clear Filters */}
          {(statusFilter !== "all" || categoryFilter !== "all" || contactStatusFilter !== "all" || searchQuery.trim()) && (
            <button
              onClick={() => {
                setStatusFilter("all");
                setCategoryFilter("all");
                setContactStatusFilter("all");
                setSearchQuery("");
              }}
              className="rounded-lg border border-slate-700 px-4 py-2 text-xs font-medium text-slate-300 hover:bg-slate-800 whitespace-nowrap"
            >
              Clear Filters
            </button>
          )}

          {/* Items Per Page */}
          <div className="min-w-[120px]">
            <label className="block text-xs font-medium text-slate-400 mb-1">Per Page</label>
            <select
              value={itemsPerPage}
              onChange={(e) => {
                setItemsPerPage(Number(e.target.value));
                setCurrentPage(1);
              }}
              className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white focus:border-indigo-500 focus:outline-none"
            >
              <option value="10">10</option>
              <option value="25">25</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </select>
          </div>

          {/* Results Count */}
          <div className="relative top-[-8px] text-xs text-slate-400 whitespace-nowrap">
            {filteredDomains.length > 0 ? (
              <>
                 {(currentPage - 1) * itemsPerPage + 1} - {Math.min(currentPage * itemsPerPage, filteredDomains.length)} of {filteredDomains.length}
                {filteredDomains.length !== allDomains.length && ` (${allDomains.length} total)`}
              </>
            ) : (
              <>No domains found</>
            )}
          </div>
        </div>
      </div>

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
        <button
          onClick={() => setShowBulkDisableModal(true)}
          className="rounded-lg border border-slate-700 px-4 py-2 text-xs font-medium text-slate-200 hover:bg-slate-800"
        >
          Bulk Disable
        </button>
        <button
          onClick={() => setShowBulkDeleteModal(true)}
          className="rounded-lg border border-rose-600 px-4 py-2 text-xs font-medium text-rose-400 hover:bg-rose-600/20"
          disabled={selectedIds.length === 0}
        >
          Bulk Delete
        </button>
        <button
          onClick={() => setShowDeleteAllModal(true)}
          className="rounded-lg border border-rose-700 px-4 py-2 text-xs font-medium text-rose-300 hover:bg-rose-700/20"
          disabled={filteredDomains.length === 0}
        >
          Delete All {filteredDomains.length !== allDomains.length ? `(${filteredDomains.length})` : ""}
        </button>
        <button
          onClick={handleDownloadFailedDomains}
          className="rounded-lg border border-rose-600 px-4 py-2 text-xs font-medium text-rose-400 hover:bg-rose-600/20"
        >
          Download Failed Domains
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
              <th className="px-6 py-4">Contact Page</th>
              <th className="px-6 py-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {domains.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center text-sm text-slate-400">
                  {filteredDomains.length === 0 && allDomains.length === 0
                    ? "No domains found yet. Seed the database or add a domain to get started."
                    : filteredDomains.length === 0
                    ? "No domains match your filters. Try adjusting your search criteria."
                    : "No domains on this page."}
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
                    <td className="px-6 py-4 text-xs">
                      {domain.contactCheckStatus === "pending" ? (
                        <span className="rounded-full px-3 py-1 font-semibold bg-yellow-500/10 text-yellow-300">
                          Checking...
                        </span>
                      ) : domain.contactCheckStatus === "found" ? (
                        <div>
                          <span className="rounded-full px-3 py-1 font-semibold bg-emerald-500/10 text-emerald-300">
                            Found
                          </span>
                          {domain.contactPageUrl && (
                            <a
                              href={domain.contactPageUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="block mt-1 text-xs text-indigo-400 hover:text-indigo-300 truncate max-w-[200px]"
                              title={domain.contactPageUrl}
                            >
                              {domain.contactPageUrl.length > 30
                                ? domain.contactPageUrl.substring(0, 30) + "..."
                                : domain.contactPageUrl}
                            </a>
                          )}
                        </div>
                      ) : domain.contactCheckStatus === "not_found" ? (
                        <span className="rounded-full px-3 py-1 font-semibold bg-rose-500/10 text-rose-300">
                          Not Found
                        </span>
                      ) : domain.contactCheckStatus === "no_form" ? (
                        <span className="rounded-full px-3 py-1 font-semibold bg-orange-500/10 text-orange-300" title="Contact page found but no contact form detected (may have search/newsletter forms only)">
                          No Contact Form
                        </span>
                      ) : domain.contactCheckStatus === "error" ? (
                        <span 
                          className="rounded-full px-3 py-1 font-semibold bg-slate-700/40 text-slate-300 cursor-help"
                          title={domain.contactCheckMessage || "Error checking contact page"}
                        >
                          {domain.contactCheckMessage 
                            ? (domain.contactCheckMessage.length > 30 
                                ? domain.contactCheckMessage.substring(0, 30) + "..." 
                                : domain.contactCheckMessage)
                            : "Error"}
                        </span>
                      ) : (
                        <span className="text-slate-500">—</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right text-xs text-slate-400">
                      <button
                        onClick={() => handleRecheckContact(domain)}
                        disabled={processing}
                        className="mr-3 hover:text-yellow-300 disabled:opacity-50"
                        title="Re-check contact page"
                      >
                        Re-check
                      </button>
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

      {/* Pagination Controls */}
      {filteredDomains.length > 0 && (
        <div className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-900/60 px-6 py-4">
          <div className="text-sm text-slate-400">
            Page {currentPage} of {Math.ceil(filteredDomains.length / itemsPerPage)}
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentPage(1)}
              disabled={currentPage === 1}
              className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              First
            </button>
            <button
              onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
              className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            
            {/* Page Numbers */}
            <div className="flex items-center gap-1">
              {Array.from({ length: Math.min(5, Math.ceil(filteredDomains.length / itemsPerPage)) }, (_, i) => {
                const totalPages = Math.ceil(filteredDomains.length / itemsPerPage);
                let pageNum: number;
                
                if (totalPages <= 5) {
                  pageNum = i + 1;
                } else if (currentPage <= 3) {
                  pageNum = i + 1;
                } else if (currentPage >= totalPages - 2) {
                  pageNum = totalPages - 4 + i;
                } else {
                  pageNum = currentPage - 2 + i;
                }
                
                return (
                  <button
                    key={pageNum}
                    onClick={() => setCurrentPage(pageNum)}
                    className={`min-w-[32px] rounded-lg border px-2 py-1.5 text-xs font-medium transition-colors ${
                      currentPage === pageNum
                        ? "border-indigo-500 bg-indigo-500/20 text-indigo-300"
                        : "border-slate-700 text-slate-300 hover:bg-slate-800"
                    }`}
                  >
                    {pageNum}
                  </button>
                );
              })}
            </div>
            
            <button
              onClick={() => setCurrentPage((prev) => Math.min(Math.ceil(filteredDomains.length / itemsPerPage), prev + 1))}
              disabled={currentPage >= Math.ceil(filteredDomains.length / itemsPerPage)}
              className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
            <button
              onClick={() => setCurrentPage(Math.ceil(filteredDomains.length / itemsPerPage))}
              disabled={currentPage >= Math.ceil(filteredDomains.length / itemsPerPage)}
              className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-300 hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Last
            </button>
          </div>
        </div>
      )}

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
          <div className="w-full max-w-2xl rounded-2xl border border-slate-800 bg-slate-900 p-6 max-h-[90vh] overflow-y-auto">
            <h3 className="text-xl font-semibold text-white mb-4">Upload CSV</h3>
            
            {/* Download Sample Button */}
            <div className="mb-4 flex items-center justify-between">
              <p className="text-sm text-slate-400">
                Upload a CSV file or paste content. Format: <code className="text-xs bg-slate-800 px-1 rounded">url,category</code>
              </p>
              <button
                onClick={handleDownloadSample}
                className="rounded-lg border border-indigo-600 px-3 py-1.5 text-xs font-medium text-indigo-400 hover:bg-indigo-600/20 transition-colors"
              >
                📥 Download Sample
              </button>
            </div>

            {/* Upload Mode Toggle */}
            <div className="mb-4 flex gap-2">
              <button
                onClick={() => {
                  setUploadMode("paste");
                  setCsvFile(null);
                }}
                className={`flex-1 rounded-lg border px-3 py-2 text-sm font-medium transition-colors ${
                  uploadMode === "paste"
                    ? "border-indigo-500 bg-indigo-500/20 text-indigo-300"
                    : "border-slate-700 text-slate-300 hover:bg-slate-800"
                }`}
              >
                Paste Content
              </button>
              <button
                onClick={() => {
                  setUploadMode("file");
                  setCsvContent("");
                }}
                className={`flex-1 rounded-lg border px-3 py-2 text-sm font-medium transition-colors ${
                  uploadMode === "file"
                    ? "border-indigo-500 bg-indigo-500/20 text-indigo-300"
                    : "border-slate-700 text-slate-300 hover:bg-slate-800"
                }`}
              >
                Upload File
              </button>
            </div>

            {/* File Upload Input */}
            {uploadMode === "file" && (
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-300 mb-2">Select CSV File</label>
                <input
                  type="file"
                  accept=".csv,.txt"
                  onChange={handleFileSelect}
                  className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-white file:mr-4 file:rounded-lg file:border-0 file:bg-indigo-500 file:px-4 file:py-2 file:text-sm file:font-medium file:text-white hover:file:bg-indigo-400"
                />
                {csvFile && (
                  <p className="mt-2 text-xs text-slate-400">
                    Selected: {csvFile.name} ({(csvFile.size / 1024).toFixed(2)} KB)
                  </p>
                )}
              </div>
            )}

            {/* CSV Content Textarea */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-slate-300 mb-2">
                {uploadMode === "file" ? "CSV Content Preview" : "CSV Content"}
              </label>
              <textarea
                value={csvContent}
                onChange={(e) => setCsvContent(e.target.value)}
                readOnly={uploadMode === "file" && csvFile !== null}
                className="w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-white font-mono text-sm h-64 resize-y"
                placeholder={uploadMode === "file" 
                  ? "Select a CSV file to preview content..."
                  : "url,category\nhttps://example1.com,interior-design\nhttps://example2.com,web-design\nhttps://example3.com,marketing"}
              />
              {uploadMode === "paste" && (
                <p className="mt-2 text-xs text-slate-500">
                  💡 Tip: Copy the sample CSV, paste your data under the headers, and upload
                </p>
              )}
            </div>

            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowUploadModal(false);
                  setCsvContent("");
                  setCsvFile(null);
                  setUploadMode("paste");
                }}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-slate-800"
              >
                Cancel
              </button>
              <button
                onClick={handleUploadCSV}
                disabled={processing || (!csvContent.trim() && !csvFile)}
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

      {/* Bulk Disable Modal */}
      {showBulkDisableModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Bulk Disable</h3>
            <p className="text-sm text-slate-400 mb-4">
              {selectedIds.length > 0
                ? `Disable ${selectedIds.length} selected domain(s)?`
                : "Select domains from the table using checkboxes, then click this button to disable them all."}
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowBulkDisableModal(false);
                  setSelectedIds([]);
                }}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-slate-800"
              >
                Cancel
              </button>
              <button
                onClick={handleBulkDisable}
                disabled={processing || selectedIds.length === 0}
                className="rounded-lg bg-rose-500 px-4 py-2 text-sm font-medium text-white hover:bg-rose-400 disabled:opacity-50"
              >
                {processing ? "Disabling..." : "Disable Selected"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Bulk Delete Modal */}
      {showBulkDeleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <h3 className="text-xl font-semibold text-white mb-4">Bulk Delete</h3>
            <p className="text-sm text-slate-400 mb-4">
              {selectedIds.length > 0
                ? `⚠️ Are you sure you want to permanently delete ${selectedIds.length} selected domain(s)? This action cannot be undone.`
                : "Select domains from the table using checkboxes, then click this button to delete them all."}
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowBulkDeleteModal(false);
                }}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-slate-800"
              >
                Cancel
              </button>
              <button
                onClick={handleBulkDelete}
                disabled={processing || selectedIds.length === 0}
                className="rounded-lg bg-rose-600 px-4 py-2 text-sm font-medium text-white hover:bg-rose-500 disabled:opacity-50"
              >
                {processing ? "Deleting..." : "Delete Selected"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete All Modal */}
      {showDeleteAllModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-md rounded-2xl border border-rose-800 bg-slate-900 p-6">
            <h3 className="text-xl font-semibold text-rose-400 mb-4">⚠️ Delete All Domains</h3>
            <div className="mb-4 space-y-2">
              <p className="text-sm text-slate-300">
                {filteredDomains.length === allDomains.length
                  ? `You are about to permanently delete ALL ${filteredDomains.length} domain(s) in the database.`
                  : `You are about to permanently delete ${filteredDomains.length} domain(s) matching your current filters (out of ${allDomains.length} total).`}
              </p>
              <p className="text-sm font-semibold text-rose-400">
                ⚠️ This action CANNOT be undone!
              </p>
              <p className="text-xs text-slate-500 mt-2">
                All associated data (templates, submission logs, contact checks) will also be deleted.
              </p>
            </div>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => {
                  setShowDeleteAllModal(false);
                }}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-slate-800"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteAll}
                disabled={processing || filteredDomains.length === 0}
                className="rounded-lg bg-rose-700 px-4 py-2 text-sm font-medium text-white hover:bg-rose-600 disabled:opacity-50"
              >
                {processing ? "Deleting..." : `Delete All ${filteredDomains.length}`}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
