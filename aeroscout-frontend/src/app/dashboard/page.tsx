'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '../../store/authStore';
import { useAlertStore } from '../../store/alertStore';
import {
  getUserRecentSearches,
  getUserApiUsageStats,
  getUserInvitationCodes,
  RecentSearchResponse,
  ApiUsageStatsResponse,
  InvitationCodeResponse
} from '../../lib/apiService';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import AuthGuard from '../../components/AuthGuard';

const DashboardContent: React.FC = () => {
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const { showAlert } = useAlertStore();

  const [recentSearches, setRecentSearches] = useState<RecentSearchResponse | null>(null);
  const [apiUsageStats, setApiUsageStats] = useState<ApiUsageStatsResponse | null>(null);
  const [invitationCodes, setInvitationCodes] = useState<InvitationCodeResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setIsLoading(true);

        // 并行加载所有数据
        const [searchesData, usageData, codesData] = await Promise.allSettled([
          getUserRecentSearches(10),
          getUserApiUsageStats(),
          getUserInvitationCodes()
        ]);

        if (searchesData.status === 'fulfilled') {
          setRecentSearches(searchesData.value);
        }

        if (usageData.status === 'fulfilled') {
          console.log('API使用统计数据:', usageData.value);
          setApiUsageStats(usageData.value);
        } else {
          console.error('获取API使用统计失败:', usageData.reason);
        }

        if (codesData.status === 'fulfilled') {
          setInvitationCodes(codesData.value);
        }
      } catch (error) {
        console.error('加载仪表板数据失败:', error);
        showAlert('加载数据失败，请刷新页面重试', 'error');
      } finally {
        setIsLoading(false);
      }
    };

    loadDashboardData();
  }, [router, showAlert]);

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-[#F5F5F7] flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="large" />
          <p className="mt-4 text-[#86868B] text-[16px]">加载仪表板数据...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#007AFF] via-[#5856D6] to-[#AF52DE]">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-white/5 rounded-full blur-3xl animate-float"></div>
        <div className="absolute top-3/4 right-1/4 w-80 h-80 bg-purple-300/5 rounded-full blur-3xl animate-float-delayed"></div>
        <div className="absolute bottom-1/4 left-1/3 w-64 h-64 bg-blue-300/5 rounded-full blur-3xl animate-float"></div>
      </div>

      {/* 顶部导航 */}
      <nav className="relative z-10 bg-white/8 backdrop-blur-3xl border-b border-white/15 sticky top-0">
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => router.push('/search')}
              className="flex items-center space-x-2 text-white hover:text-white/80 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span className="font-medium">返回首页</span>
            </button>
            <div className="h-4 w-px bg-white/20"></div>
            <h1 className="text-xl font-bold text-white">
              <span className="bg-gradient-to-r from-cyan-300 via-blue-400 to-purple-500 bg-clip-text text-transparent">
                AeroScout
              </span>
              <span className="text-white/80 font-normal ml-2">控制面板</span>
            </h1>
          </div>

          <div className="flex items-center space-x-4">
            <span className="text-[14px] text-white/70">
              欢迎，{user?.username || '用户'}
            </span>
            <button
              onClick={handleLogout}
              className="text-[14px] text-white/80 hover:text-white bg-white/10 hover:bg-white/20 px-3 py-1.5 rounded-lg transition-all duration-200 border border-white/20"
            >
              退出登录
            </button>
          </div>
        </div>
      </nav>

      <div className="relative z-10 max-w-6xl mx-auto px-6 py-8">
        {/* 用户信息卡片 */}
        <div className="mb-8">
          <div className="bg-white/95 backdrop-blur-3xl rounded-3xl shadow-2xl border border-white/20 p-8 animate-fadeIn">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-[28px] font-bold text-gray-900 mb-3">
                  <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    {user?.username || '用户'}
                  </span>
                </h2>
                <div className="space-y-2">
                  <p className="text-gray-600 text-[15px] flex items-center">
                    <svg className="w-4 h-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    {user?.email || '未设置'}
                  </p>
                  <p className="text-gray-600 text-[15px] flex items-center">
                    <svg className="w-4 h-4 mr-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    {user?.is_admin ? '管理员' : '普通用户'}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <button
                  onClick={() => router.push('/search')}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 rounded-2xl font-semibold transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
                >
                  开始搜索航班
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* API使用统计 */}
        <div className="mb-8">
          <h3 className="text-[24px] font-bold text-white mb-6 text-center">API使用统计</h3>
          {apiUsageStats ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white/95 backdrop-blur-3xl rounded-2xl shadow-xl border border-white/20 p-6 animate-fadeIn">
                <div className="text-center">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    </svg>
                  </div>
                  <div className="text-[32px] font-bold text-blue-600 mb-2">
                    {apiUsageStats.data.poi_calls_today}
                  </div>
                  <div className="text-[14px] text-gray-700 font-medium">今日POI调用</div>
                  <div className="text-[12px] text-gray-500 mt-1">
                    限制: {apiUsageStats.data.poi_daily_limit >= 999999 ? '无限制' : apiUsageStats.data.poi_daily_limit}
                  </div>
                </div>
              </div>
              <div className="bg-white/95 backdrop-blur-3xl rounded-2xl shadow-xl border border-white/20 p-6 animate-fadeIn animation-delay-100">
                <div className="text-center">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                  </div>
                  <div className="text-[32px] font-bold text-green-600 mb-2">
                    {apiUsageStats.data.flight_calls_today}
                  </div>
                  <div className="text-[14px] text-gray-700 font-medium">今日航班调用</div>
                  <div className="text-[12px] text-gray-500 mt-1">
                    限制: {apiUsageStats.data.flight_daily_limit >= 999999 ? '无限制' : apiUsageStats.data.flight_daily_limit}
                  </div>
                </div>
              </div>
              <div className="bg-white/95 backdrop-blur-3xl rounded-2xl shadow-xl border border-white/20 p-6 animate-fadeIn animation-delay-200">
                <div className="text-center">
                  <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <div className="text-[32px] font-bold text-orange-600 mb-2">
                    {apiUsageStats.data.usage_percentage.toFixed(1)}%
                  </div>
                  <div className="text-[14px] text-gray-700 font-medium">使用率</div>
                  <div className="text-[12px] text-gray-500 mt-1">
                    {apiUsageStats.data.is_near_limit ? '接近限制' : '正常'}
                  </div>
                </div>
              </div>
              <div className="bg-white/95 backdrop-blur-3xl rounded-2xl shadow-xl border border-white/20 p-6 animate-fadeIn animation-delay-300">
                <div className="text-center">
                  <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div className="text-[32px] font-bold text-purple-600 mb-2">
                    {new Date(apiUsageStats.data.reset_date).toLocaleDateString()}
                  </div>
                  <div className="text-[14px] text-gray-700 font-medium">重置日期</div>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white/95 backdrop-blur-3xl rounded-2xl shadow-xl border border-white/20 p-8 text-center">
              <div className="text-gray-500">
                <svg className="w-12 h-12 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <p className="text-[16px] font-medium">无法加载API使用统计</p>
                <p className="text-[14px] text-gray-400 mt-1">请刷新页面重试</p>
              </div>
            </div>
          )}
        </div>

        {/* 最近搜索 */}
        {recentSearches && recentSearches.data.length > 0 && (
          <div className="mb-6">
            <h3 className="text-[20px] font-semibold text-[#1D1D1F] mb-4">最近搜索</h3>
            <div className="bg-white rounded-2xl shadow-sm border border-[#E8E8ED] overflow-hidden">
              <div className="divide-y divide-[#E8E8ED]">
                {recentSearches.data.map((search, index) => (
                  <div key={search.id} className="p-4 hover:bg-[#F5F5F7] transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-4">
                          <div className="text-[16px] font-medium text-[#1D1D1F]">
                            {search.from_location} → {search.to_location}
                          </div>
                          <div className="text-[14px] text-[#86868B]">
                            {search.date}
                          </div>
                          <div className="text-[14px] text-[#86868B]">
                            {search.passengers}位乘客
                          </div>
                        </div>
                        <div className="text-[12px] text-[#86868B] mt-1">
                          搜索时间: {new Date(search.searched_at).toLocaleString()}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {search.is_favorite && (
                          <div className="text-[#FF9500]">
                            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                            </svg>
                          </div>
                        )}
                        <button
                          onClick={() => {
                            // 这里可以添加重新搜索的逻辑
                            router.push('/search');
                          }}
                          className="text-[#0071E3] hover:text-[#0056B3] text-[14px] transition-colors"
                        >
                          重新搜索
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* 邀请码 */}
        {invitationCodes && invitationCodes.data.length > 0 && (
          <div className="mb-6">
            <h3 className="text-[20px] font-semibold text-[#1D1D1F] mb-4">我的邀请码</h3>
            <div className="bg-white rounded-2xl shadow-sm border border-[#E8E8ED] overflow-hidden">
              <div className="divide-y divide-[#E8E8ED]">
                {invitationCodes.data.map((code) => (
                  <div key={code.id} className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="text-[16px] font-mono font-medium text-[#1D1D1F]">
                          {code.code}
                        </div>
                        <div className="text-[12px] text-[#86868B] mt-1">
                          创建时间: {new Date(code.created_at).toLocaleString()}
                          {code.used_at && ` · 使用时间: ${new Date(code.used_at).toLocaleString()}`}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 rounded-full text-[12px] font-medium ${
                          code.is_used
                            ? 'bg-[#86868B]/10 text-[#86868B]'
                            : 'bg-[#34C759]/10 text-[#34C759]'
                        }`}>
                          {code.is_used ? '已使用' : '未使用'}
                        </span>
                        {!code.is_used && (
                          <button
                            onClick={() => {
                              navigator.clipboard.writeText(code.code);
                              showAlert('邀请码已复制到剪贴板', 'success');
                            }}
                            className="text-[#0071E3] hover:text-[#0056B3] text-[14px] transition-colors"
                          >
                            复制
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* 快速操作 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <button
            onClick={() => router.push('/search')}
            className="bg-white rounded-2xl shadow-sm border border-[#E8E8ED] p-6 hover:shadow-md transition-shadow text-left"
          >
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-[#0071E3] rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </div>
              <div>
                <div className="text-[16px] font-medium text-[#1D1D1F]">搜索航班</div>
                <div className="text-[14px] text-[#86868B]">查找最优惠的航班价格</div>
              </div>
            </div>
          </button>

          {user?.is_admin && (
            <button
              onClick={() => router.push('/admin')}
              className="bg-white rounded-2xl shadow-sm border border-[#E8E8ED] p-6 hover:shadow-md transition-shadow text-left"
            >
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-[#FF9500] rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <div>
                  <div className="text-[16px] font-medium text-[#1D1D1F]">管理面板</div>
                  <div className="text-[14px] text-[#86868B]">系统管理和配置</div>
                </div>
              </div>
            </button>
          )}

          <button
            onClick={() => window.location.href = 'mailto:1242772513@izlx.de'}
            className="bg-white/95 backdrop-blur-3xl rounded-2xl shadow-xl border border-white/20 p-6 hover:shadow-2xl transition-all duration-300 text-left transform hover:scale-105"
          >
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-[#34C759] rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <div className="text-[16px] font-medium text-[#1D1D1F]">联系支持</div>
                <div className="text-[14px] text-[#86868B]">获取帮助和技术支持</div>
              </div>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

const DashboardPage: React.FC = () => {
  return (
    <AuthGuard requireAuth={true}>
      <DashboardContent />
    </AuthGuard>
  );
};

export default DashboardPage;
