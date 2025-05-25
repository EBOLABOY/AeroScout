'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import axios from 'axios';
import apiClient from '@/lib/apiService';
import { useAuthStore } from '@/store/authStore';
import Link from 'next/link';
import Button from '@/components/common/Button';
import Input from '@/components/common/Input';

interface LoginFormData {
  email: string;
  password: string;
}

const LoginPage = () => {
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
    <div className="min-h-screen flex items-center justify-center bg-white py-12 px-4 sm:px-6 lg:px-8 animate-fadeIn">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-semibold text-[#1D1D1F] tracking-tight">登录账户</h2>
          <p className="mt-2 text-[#86868B] text-[15px]">欢迎回来，请登录您的账户</p>
        </div>

        <div className="mt-8 bg-white rounded-apple shadow-apple p-8 border border-[#E8E8ED] animate-scaleIn">
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
              <p className="text-[14px] text-[#86868B]">
                没有账户？{' '}
                <Link href="/auth/register" className="text-[#0071E3] hover:text-[#0077ED] transition-colors font-medium">
                  注册
                </Link>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;