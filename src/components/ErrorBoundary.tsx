"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
    this.setState({
      error,
      errorInfo,
    });
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="flex items-center justify-center min-h-[400px] p-6">
          <div className="rounded-xl border border-rose-800/50 bg-gradient-to-br from-rose-900/20 to-slate-900/40 backdrop-blur-sm p-8 max-w-2xl w-full shadow-lg">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-lg bg-rose-500/20 border border-rose-500/30 flex items-center justify-center">
                <span className="text-2xl">⚠️</span>
              </div>
              <div>
                <h2 className="text-xl font-semibold text-white">Something went wrong</h2>
                <p className="text-sm text-slate-400 mt-0.5">An unexpected error occurred</p>
              </div>
            </div>

            {this.state.error && (
              <div className="mb-4 p-4 rounded-lg border border-slate-800/50 bg-slate-950/50">
                <p className="text-sm font-semibold text-rose-300 mb-2">Error Details:</p>
                <p className="text-xs text-slate-300 font-mono break-all">
                  {this.state.error.message || "Unknown error"}
                </p>
              </div>
            )}

            <div className="flex gap-3">
              <button
                onClick={this.handleReset}
                className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-indigo-500 to-indigo-600 px-4 py-2.5 text-sm font-medium text-white hover:from-indigo-400 hover:to-indigo-500 transition-all shadow-sm hover:shadow-md"
              >
                <span>🔄</span>
                Try Again
              </button>
              <button
                onClick={() => window.location.href = "/dashboard"}
                className="inline-flex items-center gap-2 rounded-lg border border-slate-700/50 bg-slate-800/50 px-4 py-2.5 text-sm font-medium text-slate-200 hover:bg-slate-700/50 transition-all"
              >
                <span>🏠</span>
                Go to Dashboard
              </button>
            </div>

            {process.env.NODE_ENV === "development" && this.state.errorInfo && (
              <details className="mt-4">
                <summary className="text-xs text-slate-400 cursor-pointer hover:text-slate-300">
                  Stack Trace (Development Only)
                </summary>
                <pre className="mt-2 p-4 rounded-lg border border-slate-800/50 bg-slate-950/50 text-xs text-slate-300 overflow-auto max-h-64">
                  {this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

