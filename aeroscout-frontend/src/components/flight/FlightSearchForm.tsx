'use client';

import React, { useState, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import AirportSelector from '../airport/AirportSelector';
import Button from '../common/Button';
import { Airport } from '../../types/airport';
import { FlightSearchRequest } from '../../types/api';
import { useAlertStore } from '../../store/alertStore';

interface FlightSearchFormProps {
  onSearch?: (searchData: FlightSearchRequest) => void;
}

const FlightSearchForm: React.FC<FlightSearchFormProps> = ({ onSearch }) => {
  const router = useRouter();
  const { showAlert } = useAlertStore();

  // 获取今天的日期
  const getTodayDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  // 表单状态
  const [origin, setOrigin] = useState<Airport | null>(null);
  const [destination, setDestination] = useState<Airport | null>(null);
  const [departureDate, setDepartureDate] = useState(getTodayDate());
  const [cabinClass, setCabinClass] = useState('ECONOMY');
  const [isLoading, setIsLoading] = useState(false);

  // 自动聚焦到第一个输入框
  useEffect(() => {
    const timer = setTimeout(() => {
      const firstInput = document.querySelector('input[placeholder="选择出发机场"]') as HTMLInputElement;
      if (firstInput) {
        firstInput.focus();
      }
    }, 500);
    return () => clearTimeout(timer);
  }, []);



  // 验证表单
  const validateForm = (): boolean => {
    if (!origin) {
      showAlert('请选择出发地', 'error');
      return false;
    }
    if (!destination) {
      showAlert('请选择目的地', 'error');
      return false;
    }
    if (origin.code === destination.code) {
      showAlert('出发地和目的地不能相同', 'error');
      return false;
    }
    if (!departureDate) {
      showAlert('请选择出发日期', 'error');
      return false;
    }
    return true;
  };

  // 处理表单提交
  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    console.log('🚀 搜索表单提交');

    if (!validateForm()) {
      console.log('❌ 表单验证失败');
      return;
    }

    console.log('✅ 表单验证通过，开始搜索');
    setIsLoading(true);

    try {
      // 构建搜索请求数据
      const searchData: FlightSearchRequest = {
        origin_iata: origin!.code,
        destination_iata: destination!.code,
        departure_date_from: departureDate,
        departure_date_to: departureDate, // 使用相同日期作为范围
        adults: 1, // 默认1位成人
        children: 0,
        infants: 0,
        cabin_class: cabinClass,
        direct_flights_only_for_primary: false,
        enable_hub_probe: true,
        is_one_way: true, // 固定为单程
      };

      // 如果有回调函数，调用它
      if (onSearch) {
        await onSearch(searchData);
      } else {
        // 否则导航到结果页面
        const searchParams = new URLSearchParams({
          origin: origin!.code,
          destination: destination!.code,
          departureDate,
          adults: '1',
          children: '0',
          infants: '0',
          cabinClass,
          directFlightsOnly: 'false',
          enableHubProbe: 'true',
          isOneWay: 'true',
        });

        router.push(`/search/results?${searchParams.toString()}`);
      }
    } catch (error) {
      console.error('搜索失败:', error);
      showAlert('搜索失败，请稍后重试', 'error');
    } finally {
      setIsLoading(false);
    }
  }, [origin, destination, departureDate, cabinClass, onSearch, router, showAlert]);

  return (
    <div className="w-full max-w-6xl mx-auto">
      <form onSubmit={handleSubmit} className="relative">
        {/* 样式选项1: 极简主义风格 */}
        {/* <div className="bg-white/90 backdrop-blur-2xl rounded-2xl shadow-lg border border-white/30 p-6 animate-fadeIn">
          <div className="flex flex-col lg:flex-row lg:items-end gap-4">
            <div className="flex-1">
              <label className="block text-sm text-gray-700 mb-2">出发地</label>
              <AirportSelector value={origin} onChange={setOrigin} placeholder="出发机场" mode="dep" className="w-full" />
            </div>
            <div className="flex-1">
              <label className="block text-sm text-gray-700 mb-2">目的地</label>
              <AirportSelector value={destination} onChange={setDestination} placeholder="目的地机场" mode="dep" className="w-full" />
            </div>
            <div className="flex-1">
              <label className="block text-sm text-gray-700 mb-2">出发日期</label>
              <input type="date" value={departureDate} onChange={(e) => setDepartureDate(e.target.value)} min={getTodayDate()} className="w-full px-3 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent" required />
            </div>
            <div className="flex-1">
              <label className="block text-sm text-gray-700 mb-2">舱位</label>
              <select value={cabinClass} onChange={(e) => setCabinClass(e.target.value)} className="w-full px-3 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                <option value="ECONOMY">经济舱</option>
                <option value="BUSINESS">商务舱</option>
              </select>
            </div>
            <button type="submit" disabled={isLoading} className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-xl font-medium transition-colors duration-200 disabled:bg-gray-400">
              {isLoading ? '搜索中...' : '搜索'}
            </button>
          </div>
        </div> */}

        {/* 样式选项2: 分段式设计 */}
        {/* <div className="space-y-6">
          <div className="bg-white/95 backdrop-blur-3xl rounded-2xl shadow-xl border border-white/20 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <svg className="w-5 h-5 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              </svg>
              选择目的地
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <AirportSelector value={origin} onChange={setOrigin} placeholder="出发地" mode="dep" className="w-full" />
              <AirportSelector value={destination} onChange={setDestination} placeholder="目的地" mode="dep" className="w-full" />
            </div>
          </div>
          <div className="bg-white/95 backdrop-blur-3xl rounded-2xl shadow-xl border border-white/20 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <svg className="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              选择日期和舱位
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input type="date" value={departureDate} onChange={(e) => setDepartureDate(e.target.value)} min={getTodayDate()} className="px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500" required />
              <select value={cabinClass} onChange={(e) => setCabinClass(e.target.value)} className="px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
                <option value="ECONOMY">经济舱</option>
                <option value="BUSINESS">商务舱</option>
              </select>
            </div>
          </div>
          <div className="text-center">
            <button type="submit" disabled={isLoading} className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-12 py-4 rounded-2xl font-semibold text-lg shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105">
              {isLoading ? '搜索中...' : '开始搜索'}
            </button>
          </div>
        </div> */}

        {/* 极简主义风格 - 单行布局 */}
        <div className="bg-white/90 backdrop-blur-2xl rounded-2xl shadow-lg border border-white/30 p-6 animate-fadeIn">
          {/* 单行表单布局 */}
          <div className="flex flex-col lg:flex-row lg:items-end gap-4">
            {/* 出发地 */}
            <div className="flex-1">
              <label htmlFor="origin-input" className="block text-sm text-gray-700 mb-2 font-medium">出发地</label>
              <AirportSelector
                value={origin}
                onChange={setOrigin}
                placeholder="选择出发机场"
                mode="dep"
                className="w-full"
              />
            </div>

            {/* 交换按钮 - 在移动端隐藏，桌面端显示 */}
            <div className="hidden lg:flex flex-shrink-0 pb-2">
              <button
                type="button"
                className="w-8 h-8 bg-blue-500 hover:bg-blue-600 rounded-full flex items-center justify-center transition-colors duration-200 shadow-md hover:shadow-lg"
                onClick={() => {
                  const temp = origin;
                  setOrigin(destination);
                  setDestination(temp);
                }}
                title="交换出发地和目的地"
              >
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                </svg>
              </button>
            </div>

            {/* 目的地 */}
            <div className="flex-1">
              <label htmlFor="destination-input" className="block text-sm text-gray-700 mb-2 font-medium">目的地</label>
              <AirportSelector
                value={destination}
                onChange={setDestination}
                placeholder="选择目的地机场"
                mode="dep"
                className="w-full"
              />
            </div>

            {/* 出发日期 */}
            <div className="flex-1">
              <label htmlFor="departure-date" className="block text-sm text-gray-700 mb-2 font-medium">出发日期</label>
              <input
                id="departure-date"
                type="date"
                value={departureDate}
                onChange={(e) => setDepartureDate(e.target.value)}
                min={getTodayDate()}
                className="w-full px-3 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 bg-white transition-all duration-200 hover:border-gray-400"
                required
                aria-label="选择出发日期"
              />
            </div>

            {/* 舱位 */}
            <div className="flex-1">
              <label htmlFor="cabin-class" className="block text-sm text-gray-700 mb-2 font-medium">舱位</label>
              <select
                id="cabin-class"
                value={cabinClass}
                onChange={(e) => setCabinClass(e.target.value)}
                className="w-full px-3 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 bg-white transition-all duration-200 hover:border-gray-400 appearance-none cursor-pointer"
                aria-label="选择舱位等级"
              >
                <option value="ECONOMY">经济舱</option>
                <option value="BUSINESS">商务舱</option>
              </select>
            </div>

            {/* 搜索按钮 */}
            <div className="flex-shrink-0">
              <button
                type="submit"
                disabled={isLoading}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-8 py-3 rounded-xl font-medium transition-colors duration-200 disabled:cursor-not-allowed whitespace-nowrap shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none"
              >
                {isLoading ? (
                  <div className="flex items-center justify-center space-x-2">
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                    <span>搜索中...</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center space-x-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                    <span>搜索</span>
                  </div>
                )}
              </button>
            </div>
          </div>

          {/* 移动端交换按钮 - 更简洁 */}
          <div className="lg:hidden flex justify-center mt-3">
            <button
              type="button"
              className="w-8 h-8 bg-blue-500 hover:bg-blue-600 rounded-full flex items-center justify-center transition-colors duration-200 shadow-sm"
              onClick={() => {
                const temp = origin;
                setOrigin(destination);
                setDestination(temp);
              }}
              title="交换出发地和目的地"
              aria-label="交换出发地和目的地"
            >
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
              </svg>
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default FlightSearchForm;