'use client';

import React, { useState, useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { createInvitationCode, populateHubs } from '@/lib/apiService';

const AdminPage: React.FC = () => {
  const router = useRouter();
  const { isAuthenticated, isAdmin, currentUser, logout } = useAuthStore();

  const [invitationCode, setInvitationCode] = useState<string | null>(null);
  const [invitationError, setInvitationError] = useState<string | null>(null);
  const [invitationLoading, setInvitationLoading] = useState<boolean>(false);

  const [populateHubsMessage, setPopulateHubsMessage] = useState<string | null>(null);
  const [populateHubsError, setPopulateHubsError] = useState<string | null>(null);
  const [populateHubsLoading, setPopulateHubsLoading] = useState<boolean>(false);
  
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    // 如果用户未认证或不是管理员，则重定向到登录页或首页
    // 确保在客户端执行
    if (typeof window !== 'undefined') {
      if (!isAuthenticated) {
        router.replace('/auth/login');
      } else if (!isAdmin) {
        // 如果已登录但不是管理员，可以重定向到仪表盘或提示无权限
        // 这里暂时重定向到仪表盘
        router.replace('/dashboard');
      }
    }
  }, [isAuthenticated, isAdmin, router]);

  // 确保在认证和权限检查通过后再渲染内容
  if (!isAuthenticated || !isAdmin) {
    // 可以显示一个加载状态或者 null，直到 useEffect 中的重定向完成
    return <div className="flex justify-center items-center h-screen"><p>Loading or unauthorized...</p></div>;
  }

  const handleCreateInvitation = async () => {
    setInvitationLoading(true);
    setInvitationError(null);
    setInvitationCode(null);
    try {
      const response = await createInvitationCode();
      setInvitationCode(response.invitation_code);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        setInvitationError(error.response?.data?.detail || error.message || 'Failed to create invitation code.');
      } else {
        setInvitationError('An unexpected error occurred.');
      }
    } finally {
      setInvitationLoading(false);
    }
  };

  const handlePopulateHubs = async () => {
    setPopulateHubsLoading(true);
    setPopulateHubsError(null);
    setPopulateHubsMessage(null);
    try {
      const response = await populateHubs();
      setPopulateHubsMessage(response.message);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        setPopulateHubsError(error.response?.data?.detail || error.message || 'Failed to populate hubs.');
      } else {
        setPopulateHubsError('An unexpected error occurred.');
      }
    } finally {
      setPopulateHubsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* 顶部导航 - 苹果官网风格 */}
      <nav className="bg-white/90 backdrop-blur-md sticky top-0 z-50 border-b border-[#E5E5EA]">
        <div className="max-w-[980px] mx-auto px-5 py-3 flex justify-between items-center">
          <div>
            <Link href="/" className="text-[21px] font-medium text-[#1D1D1F] bg-gradient-to-r from-[#0066CC] to-[#5AC8FA] bg-clip-text text-transparent transition-apple hover:opacity-80">AeroScout</Link>
          </div>

          {/* 移动端菜单按钮 */}
          <div className="md:hidden">
            <button className="p-2 rounded-full hover:bg-[#F5F5F7] transition-apple">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-[#1D1D1F]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>

          {/* 桌面端导航 - 根据登录状态显示不同内容 */}
          {mounted && (
            <div className="hidden md:flex items-center space-x-4">
              {isAuthenticated ? (
                <>
                  <Link
                    href="/dashboard"
                    className="text-[14px] font-medium text-[#1D1D1F] hover:text-[#0071E3] px-3 py-1.5 rounded-full transition-apple"
                  >
                    控制面板
                  </Link>
                  <div className="relative">
                    <button
                      onClick={() => setShowUserMenu(!showUserMenu)}
                      className="flex items-center space-x-2 text-[14px] font-medium text-[#1D1D1F] hover:text-[#0071E3] px-3 py-1.5 rounded-full transition-apple"
                    >
                      <span>{currentUser?.email || '用户'}</span>
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className={`h-4 w-4 transition-transform ${showUserMenu ? 'rotate-180' : ''}`}
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>

                    {showUserMenu && (
                      <div className="absolute right-0 mt-2 w-48 bg-white rounded-apple shadow-apple-sm border border-[#E8E8ED] py-1 z-20">
                        <Link
                          href="/dashboard"
                          className="block px-4 py-2 text-sm text-[#1D1D1F] hover:bg-[#F5F5F7] transition-apple"
                        >
                          控制面板
                        </Link>
                        <Link
                          href="/settings"
                          className="block px-4 py-2 text-sm text-[#1D1D1F] hover:bg-[#F5F5F7] transition-apple"
                        >
                          账户设置
                        </Link>
                        <button
                          onClick={() => {
                            logout();
                            window.location.href = '/auth/login';
                          }}
                          className="block w-full text-left px-4 py-2 text-sm text-[#FF3B30] hover:bg-[#F5F5F7] transition-apple"
                        >
                          登出
                        </button>
                      </div>
                    )}
                  </div>
                </>
              ) : (
                <>
                  <Link
                    href="/auth/login"
                    className="text-[14px] font-medium text-[#1D1D1F] hover:text-[#0071E3] px-3 py-1.5 rounded-full transition-apple"
                  >
                    登录
                  </Link>
                  <Link
                    href="/auth/register"
                    className="text-[14px] font-medium text-white bg-[#0071E3] hover:bg-[#0077ED] px-4 py-1.5 rounded-full shadow-apple-sm transition-apple"
                  >
                    注册
                  </Link>
                </>
              )}
            </div>
          )}
        </div>
      </nav>

      {/* 主标题区 */}
      <section className="bg-white pt-8 pb-12">
        <div className="max-w-[980px] mx-auto px-5">
          <div className="flex flex-col items-center justify-between">
            <div className="text-center mb-8">
              <div className="flex items-center justify-center mb-4">
                <div className="w-8 h-8 rounded-full bg-[#0066CC] flex items-center justify-center mr-3">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="white" className="w-4 h-4">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <span className="text-[16px] font-medium text-[#0066CC]">管理员控制面板</span>
              </div>
              <h1 className="text-[32px] font-bold text-[#1D1D1F] tracking-tight leading-tight mb-2">系统管理</h1>
              <p className="text-[17px] text-[#86868B] max-w-lg mx-auto">
                管理员专属功能区，轻松管理邀请码和系统数据
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 管理员功能卡片区 */}
      <section className="max-w-[980px] mx-auto px-5 pb-16">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* 邀请码卡片 */}
          <div className="bg-gradient-to-b from-[#E6F2FF] to-white rounded-2xl p-8 shadow-md">
            <div className="w-14 h-14 bg-gradient-to-r from-[#0066CC] to-[#5AC8FA] rounded-full flex items-center justify-center mb-6 shadow-lg">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="white" className="w-7 h-7">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-[21px] font-semibold text-[#1D1D1F] mb-3">生成邀请码</h3>
            <p className="text-[15px] text-[#86868B] mb-6">
              创建新的邀请码，用于邀请新用户注册系统
            </p>
            
            <button
              onClick={handleCreateInvitation}
              disabled={invitationLoading}
              className="w-full bg-gradient-to-r from-[#0066CC] to-[#5AC8FA] text-white font-medium py-3 px-4 rounded-full disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:shadow-lg"
            >
              {invitationLoading ? '生成中...' : '生成邀请码'}
            </button>
            
            {invitationCode && (
              <div className="mt-6 p-4 bg-white border border-[#E5E5EA] rounded-xl">
                <p className="font-medium text-[#1D1D1F] mb-2">新邀请码:</p>
                <div className="bg-[#F2F2F7] p-3 rounded-lg">
                  <p className="text-lg font-mono text-[#0066CC] select-all">{invitationCode}</p>
                </div>
              </div>
            )}
            
            {invitationError && (
              <div className="mt-6 p-4 bg-[#FEF2F2] border border-[#FECACA] rounded-xl">
                <p className="font-medium text-[#EF4444] mb-2">错误:</p>
                <p className="text-[#B91C1C]">{invitationError}</p>
              </div>
            )}
          </div>

          {/* 枢纽城市卡片 */}
          <div className="bg-gradient-to-b from-[#FFF8E6] to-white rounded-2xl p-8 shadow-md">
            <div className="w-14 h-14 bg-gradient-to-r from-[#FF9500] to-[#FFCC00] rounded-full flex items-center justify-center mb-6 shadow-lg">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="white" className="w-7 h-7">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-[21px] font-semibold text-[#1D1D1F] mb-3">枢纽城市管理</h3>
            <p className="text-[15px] text-[#86868B] mb-6">
              更新系统中的枢纽城市数据，用于航班搜索优化
            </p>
            
            <button
              onClick={handlePopulateHubs}
              disabled={populateHubsLoading}
              className="w-full bg-gradient-to-r from-[#FF9500] to-[#FFCC00] text-white font-medium py-3 px-4 rounded-full disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:shadow-lg"
            >
              {populateHubsLoading ? '更新中...' : '更新中国枢纽城市'}
            </button>
            
            {populateHubsMessage && (
              <div className="mt-6 p-4 bg-white border border-[#E5E5EA] rounded-xl">
                <p className="font-medium text-[#1D1D1F] mb-2">更新结果:</p>
                <p className="text-[#34C759]">{populateHubsMessage}</p>
              </div>
            )}
            
            {populateHubsError && (
              <div className="mt-6 p-4 bg-[#FEF2F2] border border-[#FECACA] rounded-xl">
                <p className="font-medium text-[#EF4444] mb-2">错误:</p>
                <p className="text-[#B91C1C]">{populateHubsError}</p>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* 页脚 */}
      <footer className="border-t border-[#E5E5EA] py-10">
        <div className="max-w-[980px] mx-auto px-5 text-center">
          <p className="text-[14px] text-[#86868B]">
            &copy; {new Date().getFullYear()} AeroScout 管理系统. 保留所有权利.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default AdminPage;