"use client";

import { useState, useEffect } from "react";

export default function ClientsPage() {
  const [clients, setClients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    total: 0,
    sent: 0,
    opened: 0,
    clicked: 0,
  });

  useEffect(() => {
    fetchClients();
  }, []);

  const fetchClients = async () => {
    try {
      const res = await fetch("/api/clients");
      const data = await res.json();
      setClients(data.clients || []);
      setStats(data.stats || stats);
    } catch (error) {
      console.error("Failed to fetch clients:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <header className="flex flex-col gap-2">
        <h2 className="text-2xl font-semibold text-white">Client Outreach</h2>
        <p className="text-sm text-slate-400">Track client engagement and email analytics</p>
      </header>

      {/* Stats Cards */}
      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <p className="text-xs uppercase tracking-wide text-slate-400">Total Clients</p>
          <p className="mt-3 text-2xl font-semibold text-white">{stats.total}</p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <p className="text-xs uppercase tracking-wide text-slate-400">Emails Sent</p>
          <p className="mt-3 text-2xl font-semibold text-indigo-400">{stats.sent}</p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <p className="text-xs uppercase tracking-wide text-slate-400">Opened</p>
          <p className="mt-3 text-2xl font-semibold text-emerald-400">{stats.opened}</p>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <p className="text-xs uppercase tracking-wide text-slate-400">Clicked</p>
          <p className="mt-3 text-2xl font-semibold text-blue-400">{stats.clicked}</p>
        </div>
      </section>

      {/* Clients List */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Clients ({clients.length})</h3>
        {loading ? (
          <div className="text-center py-8 text-slate-400">Loading...</div>
        ) : clients.length === 0 ? (
          <div className="text-center py-8 text-slate-400">No clients yet.</div>
        ) : (
          <div className="space-y-4">
            {clients.map((client) => (
              <div
                key={client.id}
                className="rounded-lg border border-slate-700 bg-slate-800/50 p-4 hover:bg-slate-800 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="text-lg font-semibold text-white">{client.email}</h4>
                      {client.name && (
                        <span className="text-sm text-slate-400">({client.name})</span>
                      )}
                      <span
                        className={`rounded-full px-3 py-1 text-xs font-medium ${
                          client.status === "converted"
                            ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                            : client.status === "clicked"
                              ? "bg-blue-500/20 text-blue-300 border border-blue-500/30"
                              : client.status === "opened"
                                ? "bg-indigo-500/20 text-indigo-300 border border-indigo-500/30"
                                : client.status === "sent"
                                  ? "bg-slate-500/20 text-slate-300 border border-slate-500/30"
                                  : "bg-slate-700/50 text-slate-300 border border-slate-600/30"
                        }`}
                      >
                        {client.status}
                      </span>
                    </div>
                    <p className="text-sm text-slate-400">
                      Business: {client.business?.name || "Unknown"}
                    </p>
                    {client.previewUrl && (
                      <a
                        href={client.previewUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-indigo-400 hover:text-indigo-300 text-sm"
                      >
                        🌐 Preview URL
                      </a>
                    )}
                    <div className="flex gap-4 mt-2 text-xs text-slate-500">
                      {client.emailSentAt && (
                        <span>Sent: {new Date(client.emailSentAt).toLocaleString()}</span>
                      )}
                      {client.emailOpenedAt && (
                        <span>Opened: {new Date(client.emailOpenedAt).toLocaleString()}</span>
                      )}
                      {client.lastClickedAt && (
                        <span>Clicked: {new Date(client.lastClickedAt).toLocaleString()}</span>
                      )}
                    </div>
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

