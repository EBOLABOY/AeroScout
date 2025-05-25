'use client';

import React, { useState, useEffect } from 'react';
import { legalService } from '../../services/legalService';

const PrivacyPolicyPage = () => {
  const [policyText, setPolicyText] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchPrivacyPolicy = async () => {
      try {
        setIsLoading(true);
        const text = await legalService.getPrivacyPolicyText();
        setPolicyText(text);
      } catch (error) {
        console.error('获取隐私政策失败:', error);
        // 如果获取失败，显示一个简短的错误提示
        setPolicyText('<p className="text-red-500">无法加载隐私政策内容。请稍后再试。</p>');
      } finally {
        setIsLoading(false);
      }
    };

    fetchPrivacyPolicy();
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-center">隐私政策</h1>
      
      {isLoading ? (
        <div className="flex justify-center items-center py-10">
          <div className="animate-pulse text-center">
            <p className="text-gray-500">正在加载隐私政策...</p>
          </div>
        </div>
      ) : (
        <div
          className="prose max-w-none"
          dangerouslySetInnerHTML={{ __html: policyText }}
        />
      )}
    </div>
  );
};

export default PrivacyPolicyPage;