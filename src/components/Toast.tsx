"use client";

import { useEffect, useState } from "react";
import { toastManager, Toast } from "@/lib/toast";

export function ToastContainer() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => {
    return toastManager.subscribe(setToasts);
  }, []);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-md">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} />
      ))}
    </div>
  );
}

function ToastItem({ toast }: { toast: Toast }) {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Trigger animation
    setTimeout(() => setIsVisible(true), 10);
  }, []);

  const getIcon = () => {
    switch (toast.type) {
      case "success":
        return "✅";
      case "error":
        return "❌";
      case "warning":
        return "⚠️";
      case "info":
        return "ℹ️";
      default:
        return "ℹ️";
    }
  };

  const getStyles = () => {
    switch (toast.type) {
      case "success":
        return "border-emerald-500/50 bg-emerald-500/10 text-emerald-300";
      case "error":
        return "border-rose-500/50 bg-rose-500/10 text-rose-300";
      case "warning":
        return "border-amber-500/50 bg-amber-500/10 text-amber-300";
      case "info":
        return "border-blue-500/50 bg-blue-500/10 text-blue-300";
      default:
        return "border-slate-500/50 bg-slate-500/10 text-slate-300";
    }
  };

  return (
    <div
      className={`
        rounded-lg border backdrop-blur-sm p-4 shadow-lg
        transition-all duration-300 ease-in-out
        ${isVisible ? "opacity-100 translate-x-0" : "opacity-0 translate-x-full"}
        ${getStyles()}
      `}
    >
      <div className="flex items-start gap-3">
        <span className="text-lg flex-shrink-0">{getIcon()}</span>
        <p className="text-sm font-medium flex-1">{toast.message}</p>
        <button
          onClick={() => toastManager.remove(toast.id)}
          className="flex-shrink-0 text-current opacity-70 hover:opacity-100 transition-opacity"
          aria-label="Close"
        >
          ✕
        </button>
      </div>
    </div>
  );
}

