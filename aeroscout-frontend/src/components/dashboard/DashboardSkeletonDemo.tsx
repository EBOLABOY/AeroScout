import React from 'react';
import { Card, CardHeader, CardContent, CardFooter } from '@/components/common/Card';
import Link from 'next/link';
import { 
  SearchRecordSkeleton, 
  ApiUsageSkeleton, 
  ChartSkeleton, 
  InvitationCodeSkeleton,
  TextSkeleton 
} from '@/components/common/Skeleton';

/**
 * Dashboard页面骨架屏演示组件
 * 用于展示和测试骨架屏整体效果
 */
const DashboardSkeletonDemo: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-[#F5F5F7]">
      {/* 顶部导航栏骨架屏 */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto py-3 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <Link href="/dashboard" className="flex items-center">
            <span className="text-xl font-semibold text-[#1D1D1F]">AeroScout</span>
          </Link>
          
          <div className="flex items-center space-x-2">
            <div className="h-8 w-8 rounded-full bg-gray-200 animate-pulse"></div>
            <TextSkeleton width={120} height={20} />
          </div>
        </div>
      </header>

      <main className="flex-1 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* 欢迎与概览区骨架屏 */}
          <div className="mb-8">
            <Card variant="plain" className="bg-transparent p-0">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                <div>
                  <TextSkeleton height={36} width={240} className="mb-2" />
                  <TextSkeleton height={20} width={320} />
                </div>
                <div className="mt-4 md:mt-0">
                  <div className="h-10 w-36 bg-gray-200 animate-pulse rounded-md"></div>
                </div>
              </div>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              {/* 最近搜索记录骨架屏 */}
              <Card variant="elevated" className="mb-6">
                <CardHeader withBorder>
                  <div className="flex justify-between items-center">
                    <TextSkeleton height={24} width={120} />
                    <TextSkeleton height={18} width={60} />
                  </div>
                </CardHeader>
                <CardContent>
                  {/* 搜索筛选器骨架屏 */}
                  <div className="mb-4 p-4 border border-[#E8E8ED] rounded-apple bg-white">
                    <TextSkeleton height={16} width={100} className="mb-3" />
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div>
                        <TextSkeleton height={16} width={60} className="mb-1" />
                        <div className="h-10 w-full bg-gray-200 animate-pulse rounded-md"></div>
                      </div>
                      <div>
                        <TextSkeleton height={16} width={60} className="mb-1" />
                        <div className="h-10 w-full bg-gray-200 animate-pulse rounded-md"></div>
                      </div>
                    </div>
                    <div className="flex items-center justify-between mt-4">
                      <div className="flex items-center gap-3">
                        <div className="h-8 w-24 bg-gray-200 animate-pulse rounded-md"></div>
                        <div className="h-8 w-24 bg-gray-200 animate-pulse rounded-md"></div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="h-8 w-32 bg-gray-200 animate-pulse rounded-md"></div>
                        <div className="flex items-center">
                          <div className="h-4 w-4 bg-gray-200 animate-pulse rounded mr-2"></div>
                          <TextSkeleton width={80} height={16} />
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  {/* 搜索记录项骨架屏 */}
                  <div className="space-y-4">
                    {Array.from({ length: 3 }).map((_, index) => (
                      <SearchRecordSkeleton key={`search-skeleton-${index}`} />
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>

            <div>
              {/* 账户信息骨架屏 */}
              <Card variant="elevated" className="mb-6">
                <CardHeader withBorder>
                  <TextSkeleton height={24} width={100} />
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {Array.from({ length: 3 }).map((_, index) => (
                      <div key={`account-skeleton-${index}`}>
                        <TextSkeleton height={16} width={80} className="mb-1" />
                        <TextSkeleton height={20} width={160} />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* API使用情况骨架屏 */}
              <Card variant="elevated">
                <CardHeader withBorder>
                  <TextSkeleton height={24} width={120} />
                </CardHeader>
                <CardContent>
                  <ApiUsageSkeleton />
                </CardContent>
                <CardFooter withBorder>
                  <div className="h-8 w-full bg-gray-200 animate-pulse rounded-md"></div>
                </CardFooter>
              </Card>
              
              {/* API使用趋势图表骨架屏 */}
              <div className="mt-6">
                <Card variant="elevated" className="mb-6">
                  <CardHeader withBorder>
                    <TextSkeleton height={24} width={120} />
                  </CardHeader>
                  <CardContent>
                    <ChartSkeleton />
                  </CardContent>
                </Card>
              </div>
              
              {/* API使用详情骨架屏 */}
              <div className="mt-6">
                <Card variant="elevated" className="mb-6">
                  <CardHeader withBorder>
                    <TextSkeleton height={24} width={120} />
                  </CardHeader>
                  <CardContent>
                    <ApiUsageSkeleton />
                  </CardContent>
                </Card>
              </div>
              
              {/* 邀请码骨架屏 */}
              <Card variant="elevated" className="mt-6">
                <CardHeader withBorder>
                  <TextSkeleton height={24} width={100} />
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {Array.from({ length: 2 }).map((_, index) => (
                      <InvitationCodeSkeleton key={`invitation-skeleton-${index}`} />
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default DashboardSkeletonDemo;