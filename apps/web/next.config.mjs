/** @type {import('next').NextConfig} */
const nextConfig = {
  // Next.js 16 configuration
  // App Router enabled by default
  
  // Output directory (default: .next)
  output: 'standalone',
  
  // Enable TypeScript strict mode through next.config
  typescript: {
    // This will be handled by tsconfig.json
    ignoreBuildErrors: false,
  },
  
  // Environment variables
  env: {
    // Will be loaded from .env files
  },
  
  // Image optimization (disabled for now, will be configured later if needed)
  images: {
    unoptimized: true,
  },
  
  // Experimental features
  experimental: {
    // App Router is enabled by default in Next.js 16
  },
};

export default nextConfig;
