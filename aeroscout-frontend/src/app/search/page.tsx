'use client';

import React, { useEffect, useState } from 'react';
import FlightSearchForm from '../../components/flight/FlightSearchForm';
import Link from 'next/link';
import { useAuthStore } from '../../store/authStore';
import { useAuthInit } from '../../hooks/useAuthInit';

export default function SearchPage() {
  const { isAuthenticated, currentUser, logout } = useAuthStore();
  const [mounted, setMounted] = useState(false);
  const { isInitialized, isLoading } = useAuthInit();

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="full-viewport-bg no-overscroll">
      {/* 精致渐变背景 - 现代苹果风格 */}
      <div className="fixed-background">
        {/* 主渐变层 */}
        <div className="absolute inset-0 bg-gradient-to-br from-[#007AFF] via-[#5856D6] to-[#AF52DE] animate-gradient"></div>

        {/* 光效层 */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/5 via-transparent to-white/5"></div>

        {/* 微妙纹理层 */}
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-white/10 rounded-full blur-3xl animate-float"></div>
          <div className="absolute top-3/4 right-1/4 w-80 h-80 bg-purple-300/10 rounded-full blur-3xl animate-float-delayed"></div>
          <div className="absolute bottom-1/4 left-1/3 w-64 h-64 bg-blue-300/10 rounded-full blur-3xl animate-float"></div>
        </div>

        {/* 星点装饰 */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-20 left-20 w-2 h-2 bg-white/40 rounded-full animate-twinkle"></div>
          <div className="absolute top-40 right-32 w-1 h-1 bg-white/30 rounded-full animate-twinkle delay-500"></div>
          <div className="absolute bottom-32 left-1/4 w-1.5 h-1.5 bg-white/35 rounded-full animate-twinkle delay-1000"></div>
          <div className="absolute top-1/3 right-1/4 w-1 h-1 bg-white/25 rounded-full animate-twinkle delay-700"></div>
        </div>
      </div>

      {/* 精致顶部导航 - 现代毛玻璃效果 - 移动端优化 */}
      <nav className="relative z-10 bg-white/8 backdrop-blur-3xl border-b border-white/15 shadow-lg safe-top">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 sm:py-5 flex justify-between items-center">
          <Link href="/" className="group flex items-center space-x-1 sm:space-x-2">
            {/* Logo图标 */}
            <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-white/20 to-white/10 rounded-xl flex items-center justify-center backdrop-blur-sm border border-white/20 group-hover:scale-110 transition-all duration-300">
              <svg className="w-4 h-4 sm:w-6 sm:h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </div>
            {/* Logo文字 */}
            <span className="text-[20px] sm:text-[26px] font-bold text-white group-hover:text-white/90 transition-all duration-300">
              <span className="bg-gradient-to-r from-white via-blue-100 to-white bg-clip-text text-transparent">AeroScout</span>
            </span>
          </Link>

          {mounted && (
            <>
              {isLoading || !isInitialized ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                  <span className="text-[14px] text-white/70">加载中...</span>
                </div>
              ) : (
                <div className="flex items-center space-x-2 sm:space-x-4">
                  {isAuthenticated ? (
                    <>
                      {/* 控制面板按钮 - 移动端友好设计 */}
                      <Link
                        href="/dashboard"
                        className="group flex items-center justify-center w-10 h-10 sm:w-auto sm:h-auto sm:space-x-2 sm:px-4 sm:py-2.5 text-white/80 hover:text-white transition-all duration-300 rounded-full sm:rounded-xl bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/20 hover:border-white/30 shadow-lg hover:shadow-xl transform hover:scale-105 min-h-[44px] min-w-[44px]"
                        title="控制面板"
                      >
                        <svg className="w-5 h-5 sm:w-4 sm:h-4 group-hover:scale-110 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                        <span className="hidden sm:inline text-[13px] sm:text-[15px] font-medium">控制面板</span>
                      </Link>

                      {/* 用户名显示 - 移动端简化 */}
                      <div className="flex items-center space-x-2">
                        <div className="w-8 h-8 sm:w-6 sm:h-6 bg-gradient-to-br from-white/30 to-white/20 rounded-full flex items-center justify-center border border-white/30">
                          <svg className="w-4 h-4 sm:w-3 sm:h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                          </svg>
                        </div>
                        <span className="hidden xs:inline text-[13px] sm:text-[15px] font-medium text-white/90 truncate max-w-[80px] sm:max-w-none">
                          {currentUser?.username || '用户'}
                        </span>
                      </div>

                      {/* 登出按钮 - 移动端友好设计 */}
                      <button
                        onClick={() => {
                          logout();
                          window.location.href = '/auth/login';
                        }}
                        className="group flex items-center justify-center w-10 h-10 sm:w-auto sm:h-auto sm:space-x-2 sm:px-3 sm:py-1.5 text-white/70 hover:text-white/90 rounded-full sm:rounded-lg bg-white/5 hover:bg-white/15 transition-all duration-200 min-h-[44px] min-w-[44px] border border-white/10 hover:border-white/20"
                        title="登出"
                      >
                        <svg className="w-4 h-4 group-hover:scale-110 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                        </svg>
                        <span className="hidden sm:inline text-[12px] sm:text-[14px] font-medium">登出</span>
                      </button>
                    </>
                  ) : (
                    <>
                      <Link
                        href="/auth/login"
                        className="group flex items-center space-x-1 sm:space-x-2 text-[13px] sm:text-[15px] font-medium text-white/80 hover:text-white transition-all duration-300 px-2 sm:px-4 py-2 sm:py-2.5 rounded-xl hover:bg-white/10 backdrop-blur-sm border border-white/10 hover:border-white/20 min-h-[44px]"
                      >
                        <svg className="w-3 h-3 sm:w-4 sm:h-4 group-hover:scale-110 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                        </svg>
                        <span>登录</span>
                      </Link>
                      <Link
                        href="/auth/register"
                        className="group flex items-center space-x-1 sm:space-x-2 text-[13px] sm:text-[15px] font-medium text-white bg-gradient-to-r from-white/20 to-white/15 hover:from-white/30 hover:to-white/25 backdrop-blur-sm px-3 sm:px-6 py-2 sm:py-2.5 rounded-full border border-white/30 hover:border-white/40 shadow-lg transition-all duration-300 transform hover:scale-105 hover:shadow-xl min-h-[44px]"
                      >
                        <svg className="w-3 h-3 sm:w-4 sm:h-4 group-hover:scale-110 transition-transform duration-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
                        </svg>
                        <span>注册</span>
                      </Link>
                    </>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </nav>

      {/* 主内容区域 - 极简设计 - 移动端优化 */}
      <main className="relative z-10 flex-1 flex items-center justify-center px-4 sm:px-6 py-8 sm:py-16 overflow-visible">
        <div className="w-full max-w-5xl overflow-visible">
          {/* 苹果风格品牌区域 */}
          <div className="text-center mb-8 sm:mb-14 animate-fadeIn">
            {/* 主标题 - 炫彩加粗版本 - 移动端优化 */}
            <h1 className="text-[32px] xs:text-[36px] sm:text-[48px] md:text-[56px] lg:text-[64px] font-bold tracking-tight leading-none mb-4 sm:mb-6">
              <span className="bg-gradient-to-r from-cyan-300 via-blue-400 to-purple-500 bg-clip-text text-transparent animate-gradient-x drop-shadow-lg">
                AeroScout
              </span>
            </h1>

            {/* 苹果风格装饰线和副标题 */}
            <div className="animate-fadeIn animation-delay-300">
              {/* 精致分隔线 */}
              <div className="flex items-center justify-center mb-3 sm:mb-4">
                <div className="w-8 sm:w-12 h-px bg-gradient-to-r from-transparent via-white/30 to-transparent"></div>
                <div className="mx-2 sm:mx-4 w-1 h-1 bg-white/40 rounded-full"></div>
                <div className="w-8 sm:w-12 h-px bg-gradient-to-r from-transparent via-white/30 to-transparent"></div>
              </div>

              {/* 副标题 */}
              <p className="text-[14px] sm:text-[16px] text-white/60 font-light tracking-wide">
                智能航班搜索
              </p>
            </div>
          </div>

          {/* 搜索表单区域 */}
          <div className="relative overflow-visible animate-fadeIn animation-delay-200" style={{ zIndex: 'auto' }}>
            <FlightSearchForm />
          </div>
        </div>
      </main>

      {/* 精致页脚 */}
      <footer className="relative z-10 py-12 mt-24">
        <div className="max-w-5xl mx-auto px-6">
          <div className="text-center">
            <div className="mb-6">
              <div className="flex items-center justify-center space-x-6 mb-4">
                <Link href="/about" className="text-[14px] text-white/60 hover:text-white/80 transition-colors duration-300">
                  关于我们
                </Link>
                <div className="w-1 h-1 bg-white/30 rounded-full"></div>
                <Link href="/privacy" className="text-[14px] text-white/60 hover:text-white/80 transition-colors duration-300">
                  隐私政策
                </Link>
                <div className="w-1 h-1 bg-white/30 rounded-full"></div>
                <Link href="/terms" className="text-[14px] text-white/60 hover:text-white/80 transition-colors duration-300">
                  服务条款
                </Link>
              </div>
            </div>
            <div className="flex items-center justify-center space-x-2 mb-4">
              <div className="w-6 h-6 bg-gradient-to-br from-white/20 to-white/10 rounded-lg flex items-center justify-center">
                <svg className="w-4 h-4 text-white/70" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </div>
              <p className="text-[14px] text-white/50 font-light">
                &copy; {new Date().getFullYear()} AeroScout. 让旅行更简单。
              </p>
            </div>
            <p className="text-[12px] text-white/40 font-light">
              Powered by advanced flight search technology
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
