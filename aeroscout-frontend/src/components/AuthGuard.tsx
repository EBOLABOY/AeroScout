'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '../store/authStore';
import { useAuthInit } from '../hooks/useAuthInit';
import LoadingSpinner from './common/LoadingSpinner';

interface AuthGuardProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  requireAdmin?: boolean;
}

const AuthGuard: React.FC<AuthGuardProps> = ({
  children,
  requireAuth = true,
  requireAdmin = false
}) => {
  const router = useRouter();
  const { isAuthenticated, user } = useAuthStore();
  const { isInitialized, isLoading } = useAuthInit();

  useEffect(() => {
    if (!isInitialized || isLoading) return;

    // 需要认证但未认证
    if (requireAuth && !isAuthenticated) {
      router.push('/auth/login');
      return;
    }

    // 需要管理员权限但不是管理员
    if (requireAdmin && (!isAuthenticated || !user?.is_admin)) {
      router.push('/dashboard');
      return;
    }

    // 不需要认证但已认证（如登录页面）
    if (!requireAuth && isAuthenticated) {
      router.push('/dashboard');
      return;
    }
  }, [isInitialized, isLoading, isAuthenticated, user, requireAuth, requireAdmin, router]);

  // 显示加载状态
  if (isLoading || !isInitialized) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#007AFF] via-[#5856D6] to-[#AF52DE] flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner size="large" />
          <p className="mt-4 text-white text-[16px]">正在验证身份...</p>
        </div>
      </div>
    );
  }

  // 认证检查失败的情况
  if (requireAuth && !isAuthenticated) {
    return null; // 将重定向到登录页
  }

  if (requireAdmin && (!isAuthenticated || !user?.is_admin)) {
    return null; // 将重定向到dashboard
  }

  if (!requireAuth && isAuthenticated) {
    return null; // 将重定向到dashboard
  }

  // 认证检查通过，渲染子组件
  return <>{children}</>;
};

export default AuthGuard;
