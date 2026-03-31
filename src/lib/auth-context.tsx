"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

type AuthUser = {
  username: string;
};

type AuthState = {
  isAuthenticated: boolean;
  token: string | null;
  user: AuthUser | null;
};

type LoginResult =
  | { success: true }
  | {
      success: false;
      message: string;
    };

type RegisterResult =
  | { success: true }
  | {
      success: false;
      message: string;
    };

type AuthContextValue = AuthState & {
  isHydrated: boolean;
  apiBaseUrl: string;
  login: (username: string, password: string) => Promise<LoginResult>;
  logout: () => void;
  registerAdmin: (payload: { username: string; password: string }, adminToken: string) => Promise<RegisterResult>;
};

function resolveApiBaseUrl() {
  const raw = (process.env.NEXT_PUBLIC_API_BASE_URL || "/api").trim() || "/api";
  if (typeof window !== "undefined") {
    try {
      const url = new URL(raw, window.location.origin);
      return url.toString().replace(/\/$/, "");
    } catch {
      return raw.replace(/\/$/, "");
    }
  }
  return raw.replace(/\/$/, "");
}
const STORAGE_KEY = "teqsmartsubmit_auth";
const INITIAL_STATE: AuthState = { isAuthenticated: false, token: null, user: null };

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function loadPersistedState(): AuthState {
  if (typeof window === "undefined") {
    return INITIAL_STATE;
  }
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return INITIAL_STATE;
    }
    const parsed = JSON.parse(raw) as Partial<AuthState>;
    return {
      isAuthenticated: Boolean(parsed.isAuthenticated),
      token: parsed.token ?? null,
      user: parsed.user ?? null,
    };
  } catch {
    return INITIAL_STATE;
  }
}

function persistState(state: AuthState) {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // ignore persistence errors for now
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>(INITIAL_STATE);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setState(loadPersistedState());
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (hydrated && typeof window !== "undefined") {
      persistState(state);
    }
  }, [state, hydrated]);

  const [apiBaseUrl, setApiBaseUrl] = useState<string>(() => resolveApiBaseUrl());

  useEffect(() => {
    setApiBaseUrl(resolveApiBaseUrl());
  }, []);

  const login = useCallback(async (username: string, password: string): Promise<LoginResult> => {
    if (!username || !password) {
      return { success: false, message: "Username and password are required." };
    }
    try {
      const baseUrl = resolveApiBaseUrl();
      const response = await fetch(`${baseUrl}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (!response.ok) {
        const error = await response.json().catch(() => null);
        return {
          success: false,
          message: error?.detail ?? "Invalid credentials.",
        };
      }
      const data = await response.json();
      const nextState: AuthState = {
        isAuthenticated: true,
        token: data.access_token,
        user: data.user ?? { username },
      };
      setState(nextState);
      return { success: true };
    } catch {
      return { success: false, message: "Unable to reach authentication service." };
    }
  }, []);

  const logout = useCallback(() => {
    setState(INITIAL_STATE);
  }, []);

  const registerAdmin = useCallback(
    async (payload: { username: string; password: string }, adminToken: string): Promise<RegisterResult> => {
      try {
        const headers: Record<string, string> = {
          "Content-Type": "application/json",
          "X-Admin-Token": adminToken,
        };
        if (state.token) {
          headers.Authorization = `Bearer ${state.token}`;
        }

        const baseUrl = resolveApiBaseUrl();
        const response = await fetch(`${baseUrl}/auth/register`, {
          method: "POST",
          headers,
          body: JSON.stringify(payload),
        });

        if (!response.ok) {
          const error = await response.json().catch(() => null);
          return {
            success: false,
            message: error?.detail ?? "Unable to register admin user.",
          };
        }

        return { success: true };
      } catch {
        return { success: false, message: "Unable to reach registration service." };
      }
    },
    [state.token],
  );

  const value = useMemo<AuthContextValue>(
    () => ({
      ...state,
      isHydrated: hydrated,
      apiBaseUrl,
      login,
      logout,
      registerAdmin,
    }),
    [state, hydrated, apiBaseUrl, login, logout, registerAdmin],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}

