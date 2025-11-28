"use client";

import { useState, useEffect } from "react";

interface Setting {
  key: string;
  value: string;
  description?: string;
}

export default function SettingsPage() {
  const [settings, setSettings] = useState<Setting[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingKey, setEditingKey] = useState<string | null>(null);
  const [editValue, setEditValue] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await fetch("/api/settings");
      if (response.ok) {
        const data = await response.json();
        setSettings(data);
      }
    } catch (error) {
      console.error("Failed to fetch settings:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (key: string) => {
    setSaving(true);
    try {
      const response = await fetch("/api/settings", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ key, value: editValue }),
      });

      if (response.ok) {
        await fetchSettings();
        setEditingKey(null);
        setEditValue("");
      } else {
        const error = await response.json();
        alert(error.detail || "Failed to save setting");
      }
    } catch (error) {
      console.error("Failed to save setting:", error);
      alert("Failed to save setting");
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (key: string, currentValue: string) => {
    setEditingKey(key);
    setEditValue(currentValue);
  };

  const getDefaultSettings = () => [
    {
      key: "submission_delay",
      value: "5",
      description: "Delay in seconds between domain submissions",
    },
    {
      key: "retry_attempts",
      value: "2",
      description: "Number of retry attempts for failed submissions",
    },
    {
      key: "batch_size",
      value: "10",
      description: "Default batch size for bulk operations",
    },
    {
      key: "headless_mode",
      value: "false",
      description: "Run browser in headless mode (true/false)",
    },
    {
      key: "captcha_solver",
      value: "local",
      description: "CAPTCHA solver type: local, hybrid, or external",
    },
  ];

  const displaySettings = settings.length > 0 ? settings : getDefaultSettings();

  if (loading) {
    return (
      <div className="space-y-6">
        <header>
          <h2 className="text-2xl font-semibold text-white">System Settings</h2>
          <p className="text-sm text-slate-400">Loading settings...</p>
        </header>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <header>
        <h2 className="text-2xl font-semibold text-white">System Settings</h2>
        <p className="text-sm text-slate-400">
          Configure automation parameters, preferences, and system behavior.
        </p>
      </header>

      <div className="grid gap-4 lg:grid-cols-2">
        <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Automation Settings</h3>
          <ul className="space-y-3">
            {displaySettings
              .filter(s => ["submission_delay", "retry_attempts", "batch_size"].includes(s.key))
              .map((setting) => (
                <li key={setting.key} className="rounded-xl border border-slate-800 bg-slate-950/40 p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <span className="text-sm font-medium text-slate-200 capitalize">
                        {setting.key.replace(/_/g, " ")}
                      </span>
                      {setting.description && (
                        <p className="text-xs text-slate-500 mt-1">{setting.description}</p>
                      )}
                    </div>
                    {editingKey === setting.key ? (
                      <div className="flex gap-2 items-center">
                        <input
                          type="text"
                          value={editValue}
                          onChange={(e) => setEditValue(e.target.value)}
                          className="rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm text-white w-24"
                          autoFocus
                        />
                        <button
                          onClick={() => handleSave(setting.key)}
                          disabled={saving}
                          className="rounded px-2 py-1 text-xs bg-indigo-500 text-white hover:bg-indigo-400 disabled:opacity-50"
                        >
                          Save
                        </button>
                        <button
                          onClick={() => {
                            setEditingKey(null);
                            setEditValue("");
                          }}
                          className="rounded px-2 py-1 text-xs border border-slate-700 text-slate-300 hover:bg-slate-800"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-slate-400">{setting.value}</span>
                        <button
                          onClick={() => handleEdit(setting.key, setting.value)}
                          className="rounded px-2 py-1 text-xs border border-slate-700 text-slate-300 hover:bg-slate-800"
                        >
                          Edit
                        </button>
                      </div>
                    )}
                  </div>
                </li>
              ))}
          </ul>
        </section>

        <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Browser Settings</h3>
          <ul className="space-y-3">
            {displaySettings
              .filter(s => ["headless_mode", "captcha_solver"].includes(s.key))
              .map((setting) => (
                <li key={setting.key} className="rounded-xl border border-slate-800 bg-slate-950/40 p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <span className="text-sm font-medium text-slate-200 capitalize">
                        {setting.key.replace(/_/g, " ")}
                      </span>
                      {setting.description && (
                        <p className="text-xs text-slate-500 mt-1">{setting.description}</p>
                      )}
                    </div>
                    {editingKey === setting.key ? (
                      <div className="flex gap-2 items-center">
                        {setting.key === "headless_mode" ? (
                          <select
                            value={editValue}
                            onChange={(e) => setEditValue(e.target.value)}
                            className="rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm text-white"
                          >
                            <option value="true">True</option>
                            <option value="false">False</option>
                          </select>
                        ) : (
                          <select
                            value={editValue}
                            onChange={(e) => setEditValue(e.target.value)}
                            className="rounded-lg border border-slate-700 bg-slate-800 px-2 py-1 text-sm text-white"
                          >
                            <option value="local">Local</option>
                            <option value="hybrid">Hybrid</option>
                            <option value="external">External</option>
                          </select>
                        )}
                        <button
                          onClick={() => handleSave(setting.key)}
                          disabled={saving}
                          className="rounded px-2 py-1 text-xs bg-indigo-500 text-white hover:bg-indigo-400 disabled:opacity-50"
                        >
                          Save
                        </button>
                        <button
                          onClick={() => {
                            setEditingKey(null);
                            setEditValue("");
                          }}
                          className="rounded px-2 py-1 text-xs border border-slate-700 text-slate-300 hover:bg-slate-800"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-slate-400">{setting.value}</span>
                        <button
                          onClick={() => handleEdit(setting.key, setting.value)}
                          className="rounded px-2 py-1 text-xs border border-slate-700 text-slate-300 hover:bg-slate-800"
                        >
                          Edit
                        </button>
                      </div>
                    )}
                  </div>
                </li>
              ))}
          </ul>
        </section>
      </div>

      <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">System Information</h3>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="rounded-xl border border-slate-800 bg-slate-950/40 p-4">
            <p className="text-xs text-slate-400 mb-1">Environment</p>
            <p className="text-sm font-medium text-slate-200">Production</p>
          </div>
          <div className="rounded-xl border border-slate-800 bg-slate-950/40 p-4">
            <p className="text-xs text-slate-400 mb-1">Version</p>
            <p className="text-sm font-medium text-slate-200">1.0.0</p>
          </div>
        </div>
      </section>
    </div>
  );
}
