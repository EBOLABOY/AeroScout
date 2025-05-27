'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '../../../store/authStore';
import { useAlertStore } from '../../../store/alertStore';
import Button from '../../../components/common/Button';
import AuthGuard from '../../../components/AuthGuard';

const RegisterContent: React.FC = () => {
  const router = useRouter();
  const { register } = useAuthStore();
  const { showAlert } = useAlertStore();

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    invitationCode: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const validateForm = (): boolean => {
    if (!formData.username.trim()) {
      showAlert('请输入用户名', 'error');
      return false;
    }
    if (!formData.email.trim()) {
      showAlert('请输入邮箱地址', 'error');
      return false;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      showAlert('请输入有效的邮箱地址', 'error');
      return false;
    }
    if (!formData.password) {
      showAlert('请输入密码', 'error');
      return false;
    }
    if (formData.password.length < 6) {
      showAlert('密码长度至少为6位', 'error');
      return false;
    }
    if (formData.password !== formData.confirmPassword) {
      showAlert('两次输入的密码不一致', 'error');
      return false;
    }
    if (!formData.invitationCode.trim()) {
      showAlert('请输入邀请码', 'error');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    try {
      await register({
        username: formData.username.trim(),
        email: formData.email.trim(),
        password: formData.password,
        invitation_code: formData.invitationCode.trim(),
      });

      showAlert('注册成功！请登录', 'success');
      router.push('/auth/login');
    } catch (error) {
      console.error('注册失败:', error);
      // 错误已在store中处理并显示
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F5F5F7] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* 头部 */}
        <div className="text-center">
          <Link href="/" className="inline-block">
            <span className="text-[32px] font-medium bg-gradient-to-r from-[#0066CC] to-[#5AC8FA] bg-clip-text text-transparent">
              AeroScout
            </span>
          </Link>
          <h2 className="mt-6 text-[28px] font-semibold text-[#1D1D1F]">
            创建您的账户
          </h2>
          <p className="mt-2 text-[16px] text-[#86868B]">
            加入AeroScout，开始您的智能航班搜索之旅
          </p>
        </div>

        {/* 注册表单 */}
        <div className="bg-white rounded-2xl shadow-sm border border-[#E8E8ED] p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* 用户名 */}
            <div>
              <label htmlFor="username" className="block text-[14px] font-medium text-[#1D1D1F] mb-2">
                用户名
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                value={formData.username}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-[#D2D2D7] rounded-xl focus:ring-2 focus:ring-[#0071E3] focus:border-[#0071E3] transition-colors text-[14px]"
                placeholder="请输入用户名"
              />
            </div>

            {/* 邮箱 */}
            <div>
              <label htmlFor="email" className="block text-[14px] font-medium text-[#1D1D1F] mb-2">
                邮箱地址
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-[#D2D2D7] rounded-xl focus:ring-2 focus:ring-[#0071E3] focus:border-[#0071E3] transition-colors text-[14px]"
                placeholder="请输入邮箱地址"
              />
            </div>

            {/* 密码 */}
            <div>
              <label htmlFor="password" className="block text-[14px] font-medium text-[#1D1D1F] mb-2">
                密码
              </label>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={formData.password}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 pr-12 border border-[#D2D2D7] rounded-xl focus:ring-2 focus:ring-[#0071E3] focus:border-[#0071E3] transition-colors text-[14px]"
                  placeholder="请输入密码（至少6位）"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 flex items-center pr-3"
                >
                  <svg
                    className="h-5 w-5 text-[#86868B]"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    {showPassword ? (
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                    ) : (
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    )}
                  </svg>
                </button>
              </div>
            </div>

            {/* 确认密码 */}
            <div>
              <label htmlFor="confirmPassword" className="block text-[14px] font-medium text-[#1D1D1F] mb-2">
                确认密码
              </label>
              <div className="relative">
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  required
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 pr-12 border border-[#D2D2D7] rounded-xl focus:ring-2 focus:ring-[#0071E3] focus:border-[#0071E3] transition-colors text-[14px]"
                  placeholder="请再次输入密码"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute inset-y-0 right-0 flex items-center pr-3"
                >
                  <svg
                    className="h-5 w-5 text-[#86868B]"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    {showConfirmPassword ? (
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                    ) : (
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    )}
                  </svg>
                </button>
              </div>
            </div>

            {/* 邀请码 */}
            <div>
              <label htmlFor="invitationCode" className="block text-[14px] font-medium text-[#1D1D1F] mb-2">
                邀请码
              </label>
              <input
                id="invitationCode"
                name="invitationCode"
                type="text"
                required
                value={formData.invitationCode}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-[#D2D2D7] rounded-xl focus:ring-2 focus:ring-[#0071E3] focus:border-[#0071E3] transition-colors text-[14px]"
                placeholder="请输入邀请码"
              />
              <p className="mt-1 text-[12px] text-[#86868B]">
                需要邀请码才能注册。如果您没有邀请码，请联系我们获取。
              </p>
            </div>

            {/* 提交按钮 */}
            <div className="pt-4">
              <Button
                type="submit"
                variant="primary"
                size="lg"
                isLoading={isLoading}
                disabled={isLoading}
                fullWidth={true}
              >
                {isLoading ? '注册中...' : '创建账户'}
              </Button>
            </div>
          </form>

          {/* 登录链接 */}
          <div className="mt-6 text-center">
            <p className="text-[14px] text-[#86868B]">
              已有账户？{' '}
              <Link
                href="/auth/login"
                className="text-[#0071E3] hover:text-[#0056B3] font-medium transition-colors"
              >
                立即登录
              </Link>
            </p>
          </div>
        </div>

        {/* 服务条款 */}
        <div className="text-center">
          <p className="text-[12px] text-[#86868B]">
            注册即表示您同意我们的{' '}
            <Link href="/terms-of-service" className="text-[#0071E3] hover:text-[#0056B3] transition-colors">
              服务条款
            </Link>
            {' '}和{' '}
            <Link href="/privacy-policy" className="text-[#0071E3] hover:text-[#0056B3] transition-colors">
              隐私政策
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

const RegisterPage: React.FC = () => {
  return (
    <AuthGuard requireAuth={false}>
      <RegisterContent />
    </AuthGuard>
  );
};

export default RegisterPage;
