/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'trendysa.blob.core.windows.net',
        pathname: '/photos/**',
      },
    ],
  },
};

module.exports = nextConfig;
