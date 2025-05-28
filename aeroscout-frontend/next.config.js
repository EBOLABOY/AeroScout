/** @type {import('next').NextConfig} */
const nextConfig = {
  // 根据部署方式选择输出模式
  output: process.env.DEPLOY_MODE === 'static' ? 'export' : 'standalone',

  // 静态导出配置
  trailingSlash: true,

  // 字符编码配置
  experimental: {
    // 确保正确处理UTF-8编码
    esmExternals: true,
  },

  // 编译器配置
  compiler: {
    // 移除console.log在生产环境
    removeConsole: process.env.NODE_ENV === 'production',
  },

  // ESLint 配置
  eslint: {
    // 在构建时忽略 ESLint 错误
    ignoreDuringBuilds: true,
  },

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

  // 添加API代理配置 - 仅在开发环境下使用
  async rewrites() {
    // 生产环境下不使用rewrites，由nginx处理代理
    if (process.env.NODE_ENV === 'production' || process.env.DEPLOY_MODE === 'static') {
      return [];
    }

    // 开发环境下才使用rewrites
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return [
      {
        source: '/api/:path*',
        destination: `${backendUrl}/:path*`,
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
