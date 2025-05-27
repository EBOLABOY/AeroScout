'use client';

import React from 'react';
import Link from 'next/link';

export default function Home() {
  return (
    <div className="min-h-screen bg-white">
      {/* 顶部导航 - 苹果官网风格 */}
      <nav className="bg-white/90 backdrop-blur-md sticky top-0 z-50 border-b border-[#E5E5EA]">
        <div className="max-w-[980px] mx-auto px-5 py-3 flex justify-between items-center">
          <div>
            <Link href="/" className="text-[21px] font-medium text-[#1D1D1F] bg-gradient-to-r from-[#0066CC] to-[#5AC8FA] bg-clip-text text-transparent transition-apple hover:opacity-80">
              AeroScout
            </Link>
          </div>
          <div className="hidden md:flex items-center space-x-4">
            <Link
              href="/search"
              className="text-[14px] font-medium text-white bg-[#0071E3] hover:bg-[#0077ED] px-4 py-1.5 rounded-full shadow-apple-sm transition-apple"
            >
              开始搜索
            </Link>
          </div>
        </div>
      </nav>

      {/* 主标题区 */}
      <section className="bg-white pt-16 pb-16 mb-8">
        <div className="max-w-[980px] mx-auto px-5 text-center">
          <h1 className="text-[56px] font-bold text-[#1D1D1F] tracking-tight leading-tight mb-6">
            发现您的
            <br />
            <span className="text-[#FF9500]">下一站</span>精彩
          </h1>
          <p className="text-[21px] text-[#86868B] max-w-2xl mx-auto mb-12">
            智能搜索全球航班，为您找到最优惠的价格和最佳的旅行组合
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/search"
              className="inline-flex items-center justify-center px-8 py-3 text-[17px] font-medium text-white bg-[#0071E3] hover:bg-[#0077ED] rounded-full shadow-lg transition-apple"
            >
              开始搜索航班
            </Link>
            <Link
              href="/about"
              className="inline-flex items-center justify-center px-8 py-3 text-[17px] font-medium text-[#0071E3] hover:text-[#0077ED] transition-apple"
            >
              了解更多
            </Link>
          </div>
        </div>
      </section>

      {/* 特性介绍 */}
      <section className="max-w-[980px] mx-auto px-5 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="w-16 h-16 bg-gradient-to-r from-[#0066CC] to-[#5AC8FA] rounded-full flex items-center justify-center mb-6 mx-auto">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="white" className="w-8 h-8">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-[21px] font-semibold text-[#1D1D1F] mb-3">多航司组合</h3>
            <p className="text-[15px] text-[#86868B]">
              智能组合不同航空公司的航班，发现隐藏的价格优势。
            </p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 bg-gradient-to-r from-[#34C759] to-[#30D158] rounded-full flex items-center justify-center mb-6 mx-auto">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="white" className="w-8 h-8">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h3 className="text-[21px] font-semibold text-[#1D1D1F] mb-3">价格保障</h3>
            <p className="text-[15px] text-[#86868B]">
              透明定价，显示所有税费和附加费用，无隐藏收费。
            </p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 bg-gradient-to-r from-[#FF9500] to-[#FFCC00] rounded-full flex items-center justify-center mb-6 mx-auto">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="white" className="w-8 h-8">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-[21px] font-semibold text-[#1D1D1F] mb-3">价格追踪</h3>
            <p className="text-[15px] text-[#86868B]">
              设置价格提醒，当您关注的航线价格下降时获得通知。
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
