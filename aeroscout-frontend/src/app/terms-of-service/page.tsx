'use client';

import React, { useState, useEffect } from 'react';
import { legalService } from '../../services/legalService';

const TermsOfServicePage = () => {
  const [termsText, setTermsText] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchTermsOfService = async () => {
      try {
        setIsLoading(true);
        const text = await legalService.getTermsOfServiceText();
        setTermsText(text);
      } catch (error) {
        console.error('获取服务条款失败:', error);
        // 如果获取失败，显示一个简短的错误提示
        setTermsText('<p className="text-red-500">无法加载服务条款内容。请稍后再试。</p>');
      } finally {
        setIsLoading(false);
      }
    };

    fetchTermsOfService();
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-center">服务条款</h1>
      
      {isLoading ? (
        <div className="flex justify-center items-center py-10">
          <div className="animate-pulse text-center">
            <p className="text-gray-500">正在加载服务条款...</p>
          </div>
        </div>
      ) : (
        <div
          className="prose max-w-none"
          dangerouslySetInnerHTML={{ __html: termsText }}
        />
      )}
    </div>
  );
};

export default TermsOfServicePage;