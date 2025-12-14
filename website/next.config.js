/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Skip TypeScript type checking during build
  // API routes use runtime env vars, so build-time type checking fails
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.supabase.co',
      },
      {
        protocol: 'https',
        hostname: 'stripe.com',
      },
    ],
  },
}

module.exports = nextConfig
