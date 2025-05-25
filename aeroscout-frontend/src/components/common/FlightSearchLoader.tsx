'use client';

import React, { useEffect, useState } from 'react';

interface FlightSearchLoaderProps {
  isVisible: boolean;
  searchParams?: {
    origin?: string;
    destination?: string;
    departureDate?: string;
  };
}

const FlightSearchLoader: React.FC<FlightSearchLoaderProps> = ({
  isVisible,
  searchParams
}) => {
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState(0);
  const [elapsedTime, setElapsedTime] = useState(0);

  const searchSteps = [
    { text: '正在连接航班搜索引擎...', duration: 1000 },
    { text: '搜索直飞航班...', duration: 2000 },
    { text: '分析隐藏城市航班...', duration: 2500 },
    { text: '优化价格组合...', duration: 1500 },
    { text: '整理搜索结果...', duration: 1000 },
  ];

  useEffect(() => {
    if (!isVisible) {
      setProgress(0);
      setCurrentStep(0);
      setElapsedTime(0);
      return;
    }

    // 进度条动画
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 95) return prev; // 最多到95%，等待实际完成
        return prev + Math.random() * 3 + 1;
      });
    }, 200);

    // 步骤切换动画
    const stepInterval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev < searchSteps.length - 1) {
          return prev + 1;
        }
        return prev;
      });
    }, 2000);

    // 计时器
    const timeInterval = setInterval(() => {
      setElapsedTime(prev => prev + 1);
    }, 1000);

    return () => {
      clearInterval(progressInterval);
      clearInterval(stepInterval);
      clearInterval(timeInterval);
    };
  }, [isVisible, searchSteps.length]);

  if (!isVisible) return null;

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-md w-full mx-4 animate-fadeIn">
        {/* 头部 */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 mx-auto mb-4 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full flex items-center justify-center shadow-lg">
            <svg className="w-8 h-8 text-white animate-bounce" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">正在搜索航班</h3>
          {searchParams && (
            <p className="text-sm text-gray-600">
              {searchParams.origin} → {searchParams.destination}
              {searchParams.departureDate && (
                <span className="block mt-1">{searchParams.departureDate}</span>
              )}
            </p>
          )}
        </div>

        {/* 进度条 */}
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>搜索进度</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            >
              <div className="h-full bg-white/30 animate-pulse"></div>
            </div>
          </div>
        </div>

        {/* 当前步骤 */}
        <div className="mb-6">
          <div className="flex items-center space-x-3">
            <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
              <svg className="w-3 h-3 text-white animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <span className="text-sm font-medium text-gray-900">
              {searchSteps[currentStep]?.text || '正在处理...'}
            </span>
          </div>
        </div>

        {/* 步骤列表 */}
        <div className="space-y-2 mb-6">
          {searchSteps.map((step, index) => (
            <div key={index} className="flex items-center space-x-3">
              <div className={`w-4 h-4 rounded-full flex items-center justify-center ${
                index < currentStep
                  ? 'bg-green-500'
                  : index === currentStep
                    ? 'bg-blue-500 animate-pulse'
                    : 'bg-gray-200'
              }`}>
                {index < currentStep && (
                  <svg className="w-2.5 h-2.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                  </svg>
                )}
              </div>
              <span className={`text-xs ${
                index <= currentStep ? 'text-gray-900' : 'text-gray-400'
              }`}>
                {step.text}
              </span>
            </div>
          ))}
        </div>

        {/* 底部信息 */}
        <div className="flex justify-between items-center text-xs text-gray-500 pt-4 border-t border-gray-100">
          <span>搜索时间: {formatTime(elapsedTime)}</span>
          <span className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span>AeroScout 引擎</span>
          </span>
        </div>

        {/* 装饰性动画元素 */}
        <div className="absolute -top-2 -right-2 w-4 h-4 bg-blue-400 rounded-full animate-ping opacity-75"></div>
        <div className="absolute -bottom-2 -left-2 w-3 h-3 bg-indigo-400 rounded-full animate-ping opacity-75" style={{ animationDelay: '1s' }}></div>
      </div>
    </div>
  );
};

export default FlightSearchLoader;