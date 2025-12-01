import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  // Skip static generation for pages that require database during build
  // Disable static optimization for dashboard routes
  generateBuildId: async () => {
    return 'build-' + Date.now();
  },
};

export default nextConfig;
