// In-memory cache implementation
// Can be upgraded to Redis later

interface CacheEntry<T> {
  value: T;
  expiresAt: number;
}

class MemoryCache {
  private cache: Map<string, CacheEntry<any>> = new Map();
  private defaultTTL: number = 60; // seconds

  get<T>(key: string): T | null {
    const entry = this.cache.get(key);
    
    if (!entry) {
      return null;
    }

    // Check if expired
    if (Date.now() > entry.expiresAt) {
      this.cache.delete(key);
      return null;
    }

    return entry.value as T;
  }

  set<T>(key: string, value: T, ttl: number = this.defaultTTL): void {
    const expiresAt = Date.now() + ttl * 1000;
    this.cache.set(key, { value, expiresAt });
  }

  delete(key: string): void {
    this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }

  invalidate(pattern: string): void {
    const regex = new RegExp(pattern.replace(/\*/g, ".*"));
    for (const key of this.cache.keys()) {
      if (regex.test(key)) {
        this.cache.delete(key);
      }
    }
  }

  // Clean up expired entries periodically
  cleanup(): void {
    const now = Date.now();
    for (const [key, entry] of this.cache.entries()) {
      if (now > entry.expiresAt) {
        this.cache.delete(key);
      }
    }
  }
}

// Singleton instance
const memoryCache = new MemoryCache();

// Cleanup expired entries every 5 minutes
if (typeof setInterval !== "undefined") {
  setInterval(() => {
    memoryCache.cleanup();
  }, 5 * 60 * 1000);
}

// Cache key generators
export const cacheKeys = {
  dashboardStats: () => "dashboard:stats",
  dashboardDomains: () => "dashboard:domains",
  dashboardTemplates: () => "dashboard:templates",
  logs: (params?: string) => `logs:${params || "default"}`,
  domain: (id: number) => `domain:${id}`,
  template: (id: number) => `template:${id}`,
  contactCheck: (url: string) => `contact:${url}`,
};

export const cache = {
  get: <T>(key: string): T | null => memoryCache.get<T>(key),
  set: <T>(key: string, value: T, ttl?: number): void => memoryCache.set(key, value, ttl),
  delete: (key: string): void => memoryCache.delete(key),
  clear: (): void => memoryCache.clear(),
  invalidate: (pattern: string): void => memoryCache.invalidate(pattern),
};

// Helper function to cache async operations
export async function cached<T>(
  key: string,
  fn: () => Promise<T>,
  ttl: number = 60
): Promise<T> {
  const cached = memoryCache.get<T>(key);
  if (cached !== null) {
    return cached;
  }

  const value = await fn();
  memoryCache.set(key, value, ttl);
  return value;
}

