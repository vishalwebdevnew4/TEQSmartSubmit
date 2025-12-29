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
  experimental: {
    // Ensure dynamic routes are not statically generated
    missingSuspenseWithCSRBailout: false,
  },
  // Disable static optimization for dashboard routes
  generateBuildId: async () => {
    return 'build-' + Date.now();
  },
  // Enable compression
  compress: true,
  // Optimize images
  images: {
    formats: ['image/avif', 'image/webp'],
  },
};

export default nextConfig;
