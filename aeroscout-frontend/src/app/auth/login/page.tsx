'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import axios from 'axios';
import apiClient from '../../../lib/apiService';
import { useAuthStore } from '../../../store/authStore';
import Link from 'next/link';
import Button from '../../../components/common/Button';
import Input from '../../../components/common/Input';
import AuthGuard from '../../../components/AuthGuard';

interface LoginFormData {
  email: string;
  password: string;
}

const LoginContent = () => {
  const router = useRouter();
  const { setAuthenticated, setAccessToken, setCurrentUser } = useAuthStore();
  const { register, handleSubmit, formState: { errors } } = useForm<LoginFormData>();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    try {
      // 使用 application/x-www-form-urlencoded 格式发送请求
      const formData = new URLSearchParams();
      formData.append('username', data.email);
      formData.append('password', data.password);

      const response = await apiClient.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });

      const { access_token } = response.data;
      setAccessToken(access_token);
      localStorage.setItem('access_token', access_token);
      setAuthenticated(true);

      // 获取用户信息
      const userResponse = await apiClient.get('/users/me');
      setCurrentUser(userResponse.data);

      router.push('/dashboard');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        setErrorMessage(error.response?.data?.detail || '登录失败，请重试。');
      } else {
        setErrorMessage('登录失败，请重试。');
      }
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#007AFF] via-[#5856D6] to-[#AF52DE]">
      {/* 背景装饰 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-white/5 rounded-full blur-3xl animate-float"></div>
        <div className="absolute top-3/4 right-1/4 w-80 h-80 bg-purple-300/5 rounded-full blur-3xl animate-float-delayed"></div>
        <div className="absolute bottom-1/4 left-1/3 w-64 h-64 bg-blue-300/5 rounded-full blur-3xl animate-float"></div>
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
          <h1 className="text-xl font-bold text-white">用户登录</h1>
          <div className="w-20"></div>
        </div>
      </nav>

      {/* 主内容 */}
      <div className="relative z-10 flex items-center justify-center px-6 py-16 min-h-[calc(100vh-80px)]">
        <div className="w-full max-w-md">
          {/* 品牌标题 */}
          <div className="text-center mb-12 animate-fadeIn">
            <h1 className="text-[42px] font-bold tracking-tight leading-none text-white mb-4">
              <span className="bg-gradient-to-r from-cyan-300 via-blue-400 to-purple-500 bg-clip-text text-transparent">
                AeroScout
              </span>
            </h1>
            <p className="text-[18px] text-white/70 font-light">欢迎回来</p>
          </div>

          {/* 登录表单 */}
          <div className="bg-white/95 backdrop-blur-3xl rounded-3xl shadow-2xl border border-white/20 p-8 animate-scaleIn">
          <form className="space-y-6" onSubmit={handleSubmit(onSubmit)}>
            {errorMessage && (
              <div className="bg-[#FFF1F0] border border-[#FF3B30] text-[#FF3B30] px-4 py-3 rounded-lg animate-fadeIn" role="alert">
                <div className="flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <span>{errorMessage}</span>
                </div>
              </div>
            )}

            <div className="space-y-4">
              <div>
                <Input
                  id="email-address"
                  type="email"
                  label="邮箱地址"
                  autoComplete="email"
                  variant="filled"
                  placeholder="请输入您的邮箱"
                  error={errors.email?.message}
                  {...register('email', {
                    required: '邮箱是必填项',
                    pattern: {
                      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                      message: '无效的邮箱地址'
                    }
                  })}
                />
              </div>

              <div>
                <Input
                  id="password"
                  type={isPasswordVisible ? 'text' : 'password'}
                  label="密码"
                  autoComplete="current-password"
                  variant="filled"
                  placeholder="请输入您的密码"
                  error={errors.password?.message}
                  icon={
                    <button
                      type="button"
                      onClick={() => setIsPasswordVisible(!isPasswordVisible)}
                      className="text-[#8E8E93] hover:text-[#0071E3] transition-colors"
                    >
                      {isPasswordVisible ? '隐藏' : '显示'}
                    </button>
                  }
                  {...register('password', { required: '密码是必填项' })}
                />
              </div>
            </div>

            <div className="pt-2">
              <Button
                type="submit"
                variant="primary"
                fullWidth
                size="lg"
                isLoading={isLoading}
                className="rounded-full shadow-apple transition-apple-slow"
              >
                登录
              </Button>
            </div>

            <div className="text-center pt-4">
              <p className="text-[14px] text-gray-600">
                没有账户？{' '}
                <Link href="/auth/register" className="text-blue-600 hover:text-blue-700 transition-colors font-medium">
                  注册
                </Link>
              </p>
            </div>
          </form>
          </div>

          {/* 底部链接 */}
          <div className="text-center mt-8 animate-fadeIn animation-delay-300">
            <div className="flex justify-center space-x-6 text-[14px]">
              <Link href="/about" className="text-white/60 hover:text-white/80 transition-colors">
                关于我们
              </Link>
              <Link href="/privacy" className="text-white/60 hover:text-white/80 transition-colors">
                隐私政策
              </Link>
              <Link href="/terms" className="text-white/60 hover:text-white/80 transition-colors">
                服务条款
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const LoginPage = () => {
  return (
    <AuthGuard requireAuth={false}>
      <LoginContent />
    </AuthGuard>
  );
};

export default LoginPage;