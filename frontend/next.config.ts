/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  // ⭐ Force all preview URLs to redirect to production
  async redirects() {
    return [
      {
        source: '/:path*',
        has: [
          {
            type: 'host',
            value: '(?!sinbad-ai\\.vercel\\.app$).*\\.vercel\\.app',
          },
        ],
        destination: 'https://sinbad-ai.vercel.app/:path*',
        permanent: false,
      },
    ];
  },
}

module.exports = nextConfig




// /** @type {import('next').NextConfig} */
// const nextConfig = {
//   eslint: {
//     // Warning: This allows production builds to successfully complete even if
//     // your project has ESLint errors.
//     ignoreDuringBuilds: true,
//   },
//   typescript: {
//     // Warning: This allows production builds to successfully complete even if
//     // your project has type errors.
//     ignoreBuildErrors: true,
//   },
// }

// module.exports = nextConfig
