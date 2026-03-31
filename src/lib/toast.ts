"use client";

export type ToastType = "success" | "error" | "warning" | "info";

export interface Toast {
  id: string;
  message: string;
  type: ToastType;
  duration?: number;
}

class ToastManager {
  private toasts: Toast[] = [];
  private listeners: Set<(toasts: Toast[]) => void> = new Set();
  private idCounter = 0;

  subscribe(listener: (toasts: Toast[]) => void) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private notify() {
    this.listeners.forEach((listener) => listener([...this.toasts]));
  }

  show(message: string, type: ToastType = "info", duration: number = 5000) {
    const id = `toast-${++this.idCounter}`;
    const toast: Toast = { id, message, type, duration };

    this.toasts.push(toast);
    this.notify();

    if (duration > 0) {
      setTimeout(() => {
        this.remove(id);
      }, duration);
    }

    return id;
  }

  success(message: string, duration?: number) {
    return this.show(message, "success", duration);
  }

  error(message: string, duration?: number) {
    return this.show(message, "error", duration || 7000);
  }

  warning(message: string, duration?: number) {
    return this.show(message, "warning", duration);
  }

  info(message: string, duration?: number) {
    return this.show(message, "info", duration);
  }

  remove(id: string) {
    this.toasts = this.toasts.filter((toast) => toast.id !== id);
    this.notify();
  }

  clear() {
    this.toasts = [];
    this.notify();
  }
}

export const toastManager = new ToastManager();

// Convenience functions
export const toast = {
  success: (message: string, duration?: number) => toastManager.success(message, duration),
  error: (message: string, duration?: number) => toastManager.error(message, duration),
  warning: (message: string, duration?: number) => toastManager.warning(message, duration),
  info: (message: string, duration?: number) => toastManager.info(message, duration),
  show: (message: string, type: ToastType = "info", duration?: number) =>
    toastManager.show(message, type, duration),
};

