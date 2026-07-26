/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      { hostname: "i.ytimg.com" },
      { hostname: "img.youtube.com" },
      { hostname: "avatars.githubusercontent.com" },
    ],
    unoptimized: true,
  },
  // Disable barrel optimization for react-icons to fix import errors
  transpilePackages: ["react-icons"],
  experimental: {
    optimizePackageImports: [],
  },
};

module.exports = nextConfig;
