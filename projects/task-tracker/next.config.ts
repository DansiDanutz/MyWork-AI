import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    serverActions: {
      bodySizeLimit: '5mb', // Increased for file uploads (small files via Server Actions)
    },
  },
  images: {
    remotePatterns: [], // Will add patterns if needed for thumbnails
  },
};

export default nextConfig;
