"use client"; // 将 RootLayout 转换为客户端组件以使用 hooks

import { Inter } from 'next/font/google';
import Link from 'next/link'; // 导入 Link 组件
import './globals.css';
import { useAuthStore } from '@/store/authStore';
import React, { useState, useEffect } from 'react';
import DisclaimerModal, { hasUserAcceptedDisclaimer } from '@/components/common/DisclaimerModal';
import { useAlertStore } from '@/store/alertStore';
import Alert from '@/components/common/Alert';

// 配置 Inter 字体作为 SF Pro 的替代品
// Inter 是一个开源字体，设计风格与 SF Pro 非常相似
const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
  weight: ['400', '500', '600', '700'],
});

// 不再需要单独的 sfProText 和 sfProDisplay 变量
// 直接使用 inter 变量

// Metadata 不能在 "use client" 组件中直接导出，
// 通常建议将其放在父级服务器组件或 page.tsx 中。
// 但对于根布局，Next.js 有特定处理方式，我们暂时保留，
// 如果 Next.js 报错，则需要调整。
// export const metadata: Metadata = { // 这行在 "use client" 中会引起问题
//   title: 'AeroScout',
//   description: '搜索和发现具有价格优势的航班组合',
// };

const AppFooter = () => (
  <footer className="text-center py-6 mt-auto border-t border-[#E8E8ED]">
    <div className="container mx-auto px-4">
      <div className="flex justify-center space-x-8 mb-4">
        <Link href="/privacy-policy" className="text-[#0071E3] text-[15px] hover:underline transition-apple">隐私政策</Link>
        <Link href="/terms-of-service" className="text-[#0071E3] text-[15px] hover:underline transition-apple">服务条款</Link>
        <a href="#" className="text-[#0071E3] text-[15px] hover:underline transition-apple">关于我们</a>
      </div>
      <p className="text-[13px] text-[#8E8E93] mb-2">&copy; {new Date().getFullYear()} AeroScout. 保留所有权利.</p>
      <p className="text-[12px] text-[#8E8E93] max-w-md mx-auto">
        我们使用必要的存储技术（如 localStorage）来支持应用核心功能，例如用户认证。
        继续使用即表示您同意我们的数据处理方式。
      </p>
    </div>
  </footer>
);


export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const [showDisclaimer, setShowDisclaimer] = useState(false);
  const { isOpen: isAlertOpen, message: alertMessage, variant: alertVariant, title: alertTitle, hideAlert } = useAlertStore();

  useEffect(() => {
    const initAuth = async () => {
      // 检查认证状态
      const accessToken = localStorage.getItem('access_token');
      if (accessToken) {
        useAuthStore.getState().setAccessToken(accessToken);
        useAuthStore.getState().setAuthenticated(true);
        await useAuthStore.getState().fetchCurrentUser(); // 调用 fetchCurrentUser
      }

      // 检查免责声明状态
      if (!hasUserAcceptedDisclaimer()) {
        setShowDisclaimer(true);
      }
    };
    initAuth();
  }, []);

  const handleDisclaimerClose = () => {
    setShowDisclaimer(false);
  };

  return (
    <html lang="zh-CN" className="h-full">
      <head>
        <title>AeroScout - 智能航班搜索</title>
        <meta name="description" content="AeroScout 帮助您搜索和发现具有价格优势的航班组合，节省旅行成本" />
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
        <meta name="theme-color" content="#0071E3" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
      </head>
      <body className={`${inter.variable} flex flex-col min-h-screen bg-[#FFFFFF] text-[#1D1D1F]`}>
        <div className="flex-grow">{children}</div>
        <AppFooter />
        {showDisclaimer && <DisclaimerModal isOpenInitially={true} onClose={handleDisclaimerClose} />}
        {isAlertOpen && (
          <div className="fixed top-5 right-5 z-50 max-w-sm w-full">
            <Alert title={alertTitle} variant={alertVariant} className="shadow-lg" onClose={hideAlert}>
              {alertMessage}
            </Alert>
          </div>
        )}
      </body>
    </html>
  );
}
