'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useForm } from 'react-hook-form';
import axios from 'axios';
import apiClient from '@/lib/apiService';
import Link from 'next/link';
import Button from '@/components/common/Button';
import Input from '@/components/common/Input';

interface RegisterFormData {
  email: string;
  password: string;
  confirmPassword: string;
  invitationCode: string;
}

const RegisterPage = () => {
  const router = useRouter();
  const { register, handleSubmit, watch, formState: { errors } } = useForm<RegisterFormData>();
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isPasswordVisible, setIsPasswordVisible] = useState(false);
  const [isConfirmPasswordVisible, setIsConfirmPasswordVisible] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const password = watch('password', '');

  const onSubmit = async (data: RegisterFormData) => {
    setIsLoading(true);
    try {
      await apiClient.post('/auth/register', {
        email: data.email,
        password: data.password,
        invitation_code: data.invitationCode,
      });
      router.push('/auth/login');
    } catch (error) {
      if (axios.isAxiosError(error)) {
        setErrorMessage(error.response?.data?.detail || '注册失败，请重试。');
      } else {
        setErrorMessage('注册失败，请重试。');
      }
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-white py-12 px-4 sm:px-6 lg:px-8 animate-fadeIn">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h2 className="text-3xl font-semibold text-[#1D1D1F] tracking-tight">创建账户</h2>
          <p className="mt-2 text-[#86868B] text-[15px]">加入AeroScout，开始您的旅程</p>
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
                  autoComplete="new-password"
                  variant="filled"
                  placeholder="请设置您的密码"
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
                  {...register('password', {
                    required: '密码是必填项',
                    minLength: {
                      value: 8,
                      message: '密码至少需要8个字符'
                    }
                  })}
                />
              </div>

              <div>
                <Input
                  id="confirm-password"
                  type={isConfirmPasswordVisible ? 'text' : 'password'}
                  label="确认密码"
                  autoComplete="new-password"
                  variant="filled"
                  placeholder="请再次输入密码"
                  error={errors.confirmPassword?.message}
                  icon={
                    <button
                      type="button"
                      onClick={() => setIsConfirmPasswordVisible(!isConfirmPasswordVisible)}
                      className="text-[#8E8E93] hover:text-[#0071E3] transition-colors"
                    >
                      {isConfirmPasswordVisible ? '隐藏' : '显示'}
                    </button>
                  }
                  {...register('confirmPassword', {
                    required: '确认密码是必填项',
                    validate: value => value === password || '两次输入的密码不一致'
                  })}
                />
              </div>

              <div>
                <Input
                  id="invitation-code"
                  type="text"
                  label="邀请码"
                  variant="filled"
                  placeholder="请输入邀请码"
                  error={errors.invitationCode?.message}
                  {...register('invitationCode', { required: '邀请码是必填项' })}
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
                注册
              </Button>
            </div>

            <div className="text-center pt-4">
              <p className="text-[14px] text-[#86868B]">
                已有账户？{' '}
                <Link href="/auth/login" className="text-[#0071E3] hover:text-[#0077ED] transition-colors font-medium">
                  登录
                </Link>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;