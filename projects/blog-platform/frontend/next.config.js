/** @type {import('next').NextConfig} */
const nextConfig = {
  // SECURITY (GHSA-2xp9-vwfh-vxw4): Next.js image optimization is disabled because
  // this app is on Next 14, which has no patch for the libheif/sharp AVIF RCE.
  // Re-enable after upgrading to Next >= 15.5.24.
  images: { unoptimized: true },
}

module.exports = nextConfig
