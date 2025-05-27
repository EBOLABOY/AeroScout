'use client';

import React from 'react';
import Link from 'next/link';

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#007AFF] via-[#5856D6] to-[#AF52DE]">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-white/5 rounded-full blur-3xl animate-float"></div>
        <div className="absolute top-3/4 right-1/4 w-80 h-80 bg-purple-300/5 rounded-full blur-3xl animate-float-delayed"></div>
      </div>

      {/* 顶部导航 */}
      <nav className="relative z-10 bg-white/8 backdrop-blur-3xl border-b border-white/15">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <Link href="/search" className="flex items-center space-x-2 text-white hover:text-white/80 transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            <span className="font-medium">返回首页</span>
          </Link>
          <h1 className="text-xl font-bold text-white">关于我们</h1>
          <div className="w-20"></div>
        </div>
      </nav>

      {/* 主内容 */}
      <main className="relative z-10 max-w-4xl mx-auto px-6 py-16">
        <div className="bg-white/95 backdrop-blur-3xl rounded-3xl shadow-2xl border border-white/20 p-8 sm:p-12">
          {/* 标题区域 */}
          <div className="text-center mb-12">
            <h1 className="text-[36px] sm:text-[42px] font-bold tracking-tight leading-none mb-4">
              <span className="bg-gradient-to-r from-cyan-300 via-blue-400 to-purple-500 bg-clip-text text-transparent">
                AeroScout
              </span>
            </h1>
            <p className="text-[18px] text-gray-600 font-light">
              智能航班搜索，让旅行更简单
            </p>
          </div>

          {/* 内容区域 */}
          <div className="space-y-8 text-gray-700">
            {/* 公司介绍 */}
            <section>
              <h2 className="text-[24px] font-semibold text-gray-900 mb-4">我们的使命</h2>
              <p className="text-[16px] leading-relaxed">
                AeroScout 致力于为全球旅行者提供最智能、最便捷的航班搜索服务。我们相信，每一次旅行都应该从一个完美的开始，而找到理想的航班就是这个开始的关键。
              </p>
            </section>

            {/* 核心价值 */}
            <section>
              <h2 className="text-[24px] font-semibold text-gray-900 mb-6">核心价值</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center p-6 bg-blue-50 rounded-2xl">
                  <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <h3 className="text-[18px] font-semibold text-gray-900 mb-2">快速高效</h3>
                  <p className="text-[14px] text-gray-600">
                    秒级搜索全球航班，为您节省宝贵时间
                  </p>
                </div>
                <div className="text-center p-6 bg-purple-50 rounded-2xl">
                  <div className="w-12 h-12 bg-purple-500 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h3 className="text-[18px] font-semibold text-gray-900 mb-2">准确可靠</h3>
                  <p className="text-[14px] text-gray-600">
                    实时更新的航班信息，确保数据准确性
                  </p>
                </div>
                <div className="text-center p-6 bg-green-50 rounded-2xl">
                  <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                  </div>
                  <h3 className="text-[18px] font-semibold text-gray-900 mb-2">用户至上</h3>
                  <p className="text-[14px] text-gray-600">
                    以用户体验为中心，持续优化产品
                  </p>
                </div>
              </div>
            </section>

            {/* 技术优势 */}
            <section>
              <h2 className="text-[24px] font-semibold text-gray-900 mb-4">技术优势</h2>
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-[16px] font-semibold text-gray-900">智能算法</h3>
                    <p className="text-[14px] text-gray-600">采用先进的机器学习算法，为您推荐最优航班组合</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-[16px] font-semibold text-gray-900">全球覆盖</h3>
                    <p className="text-[14px] text-gray-600">整合全球1000+家航空公司数据，覆盖世界各大航线</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-[16px] font-semibold text-gray-900">实时更新</h3>
                    <p className="text-[14px] text-gray-600">24/7实时监控航班价格变化，确保信息准确及时</p>
                  </div>
                </div>
              </div>
            </section>

            {/* 联系信息 */}
            <section>
              <h2 className="text-[24px] font-semibold text-gray-900 mb-4">联系我们</h2>
              <div className="bg-gray-50 rounded-2xl p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-[16px] font-semibold text-gray-900 mb-2">客服支持</h3>
                    <p className="text-[14px] text-gray-600 mb-1">邮箱: 1242772513@izlx.de</p>
                    <p className="text-[14px] text-gray-600 mb-1">微信: Xinx--1996</p>
                    <p className="text-[14px] text-gray-600">工作时间: 周一至周日 9:00-21:00</p>
                  </div>
                  <div>
                    <h3 className="text-[16px] font-semibold text-gray-900 mb-2">商务合作</h3>
                    <p className="text-[14px] text-gray-600 mb-1">邮箱: 1242772513@izlx.de</p>
                    <p className="text-[14px] text-gray-600 mb-1">微信: Xinx--1996</p>
                    <p className="text-[14px] text-gray-600">我们期待与您的合作</p>
                  </div>
                </div>
              </div>
            </section>
          </div>

          {/* 底部导航 */}
          <div className="mt-12 pt-8 border-t border-gray-200">
            <div className="flex flex-wrap justify-center gap-6 text-[14px]">
              <Link href="/privacy" className="text-blue-600 hover:text-blue-700 transition-colors">
                隐私政策
              </Link>
              <Link href="/terms" className="text-blue-600 hover:text-blue-700 transition-colors">
                服务条款
              </Link>
              <Link href="/search" className="text-blue-600 hover:text-blue-700 transition-colors">
                返回搜索
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
