/** @type {import('next').NextConfig} */
const nextConfig = {
  // 根据部署方式选择输出模式
  output: process.env.DEPLOY_MODE === 'static' ? 'export' : 'standalone',

  // 静态导出配置
  trailingSlash: true,

  images: {
    // 允许从任何域加载图像
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
      {
        protocol: 'http',
        hostname: '**',
      },
    ],
    // 静态导出时禁用图像优化
    unoptimized: process.env.DEPLOY_MODE === 'static' || process.env.NODE_ENV === 'development',
  },

  // 添加API代理配置 - 仅在开发环境和standalone模式下使用
  async rewrites() {
    if (process.env.DEPLOY_MODE === 'static') {
      return [];
    }

    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },

  // 添加重定向配置
  async redirects() {
    return [
      {
        source: '/',
        destination: '/search',
        permanent: false,
        basePath: false,
      },
    ];
  },
};

module.exports = nextConfig;
