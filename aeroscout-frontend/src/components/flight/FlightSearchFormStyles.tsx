'use client';

import React, { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import AirportSelector from '../airport/AirportSelector';
import { Airport } from '../../types/airport';
import { FlightSearchRequest } from '../../types/api';
import { useAlertStore } from '../../store/alertStore';

interface FlightSearchFormStylesProps {
  onSearch?: (searchData: FlightSearchRequest) => void;
  style?: 'minimal' | 'segmented' | 'modern' | 'compact';
}

const FlightSearchFormStyles: React.FC<FlightSearchFormStylesProps> = ({
  onSearch,
  style = 'modern'
}) => {
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

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      const searchData: FlightSearchRequest = {
        origin_iata: origin!.code,
        destination_iata: destination!.code,
        departure_date_from: departureDate,
        departure_date_to: departureDate,
        adults: 1,
        children: 0,
        infants: 0,
        cabin_class: cabinClass,
        direct_flights_only_for_primary: false,
        enable_hub_probe: true,
        is_one_way: true,
      };

      if (onSearch) {
        await onSearch(searchData);
      } else {
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

  // 极简主义风格
  const MinimalStyle = () => (
    <div className="bg-white/90 backdrop-blur-2xl rounded-2xl shadow-lg border border-white/30 p-6 animate-fadeIn">
      <div className="flex flex-col lg:flex-row lg:items-end gap-4">
        <div className="flex-1">
          <label className="block text-sm text-gray-700 mb-2 font-medium">出发地</label>
          <AirportSelector
            value={origin}
            onChange={setOrigin}
            placeholder="选择出发机场"
            mode="dep"
            className="w-full"
          />
        </div>
        <div className="flex-1">
          <label className="block text-sm text-gray-700 mb-2 font-medium">目的地</label>
          <AirportSelector
            value={destination}
            onChange={setDestination}
            placeholder="选择目的地机场"
            mode="dep"
            className="w-full"
          />
        </div>
        <div className="flex-1">
          <label className="block text-sm text-gray-700 mb-2 font-medium">出发日期</label>
          <input
            type="date"
            value={departureDate}
            onChange={(e) => setDepartureDate(e.target.value)}
            min={getTodayDate()}
            className="w-full px-3 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 bg-white"
            required
          />
        </div>
        <div className="flex-1">
          <label className="block text-sm text-gray-700 mb-2 font-medium">舱位</label>
          <select
            value={cabinClass}
            onChange={(e) => setCabinClass(e.target.value)}
            className="w-full px-3 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 bg-white"
          >
            <option value="ECONOMY">经济舱</option>
            <option value="BUSINESS">商务舱</option>
          </select>
        </div>
        <button
          type="submit"
          disabled={isLoading}
          className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-xl font-medium transition-colors duration-200 disabled:bg-gray-400 whitespace-nowrap"
        >
          {isLoading ? '搜索中...' : '搜索'}
        </button>
      </div>
    </div>
  );

  // 分段式设计
  const SegmentedStyle = () => (
    <div className="space-y-6">
      <div className="bg-white/95 backdrop-blur-3xl rounded-2xl shadow-xl border border-white/20 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <svg className="w-5 h-5 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          </svg>
          选择目的地
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <AirportSelector
            value={origin}
            onChange={setOrigin}
            placeholder="出发地"
            mode="dep"
            className="w-full"
          />
          <AirportSelector
            value={destination}
            onChange={setDestination}
            placeholder="目的地"
            mode="dep"
            className="w-full"
          />
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
          <input
            type="date"
            value={departureDate}
            onChange={(e) => setDepartureDate(e.target.value)}
            min={getTodayDate()}
            className="px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 bg-white"
            required
          />
          <select
            value={cabinClass}
            onChange={(e) => setCabinClass(e.target.value)}
            className="px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900 bg-white"
          >
            <option value="ECONOMY">经济舱</option>
            <option value="BUSINESS">商务舱</option>
          </select>
        </div>
      </div>
      <div className="text-center">
        <button
          type="submit"
          disabled={isLoading}
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-12 py-4 rounded-2xl font-semibold text-lg shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105 disabled:transform-none disabled:from-gray-400 disabled:to-gray-500"
        >
          {isLoading ? '搜索中...' : '开始搜索'}
        </button>
      </div>
    </div>
  );

  // 紧凑型风格
  const CompactStyle = () => (
    <div className="bg-white/95 backdrop-blur-3xl rounded-3xl shadow-xl border border-white/20 p-6 animate-scaleIn">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">出发地</label>
          <AirportSelector
            value={origin}
            onChange={setOrigin}
            placeholder="出发机场"
            mode="dep"
            className="w-full"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">目的地</label>
          <AirportSelector
            value={destination}
            onChange={setDestination}
            placeholder="目的地机场"
            mode="dep"
            className="w-full"
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">出发日期</label>
          <input
            type="date"
            value={departureDate}
            onChange={(e) => setDepartureDate(e.target.value)}
            min={getTodayDate()}
            className="w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
            required
          />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">舱位</label>
          <select
            value={cabinClass}
            onChange={(e) => setCabinClass(e.target.value)}
            className="w-full px-3 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
          >
            <option value="ECONOMY">经济舱</option>
            <option value="BUSINESS">商务舱</option>
          </select>
        </div>
      </div>
      <div className="text-center">
        <button
          type="submit"
          disabled={isLoading}
          className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white px-8 py-3 rounded-2xl font-medium transition-all duration-200 disabled:bg-gray-400 shadow-lg hover:shadow-xl transform hover:scale-105 disabled:transform-none"
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
              <span>搜索航班</span>
            </div>
          )}
        </button>
      </div>
    </div>
  );

  // 卡片式风格
  const CardStyle = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="bg-white/95 backdrop-blur-3xl rounded-2xl shadow-xl border border-white/20 p-6 space-y-4">
        <div className="flex items-center space-x-2 mb-4">
          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900">出发地</h3>
        </div>
        <AirportSelector
          value={origin}
          onChange={setOrigin}
          placeholder="选择出发机场"
          mode="dep"
          className="w-full"
        />
      </div>

      <div className="bg-white/95 backdrop-blur-3xl rounded-2xl shadow-xl border border-white/20 p-6 space-y-4">
        <div className="flex items-center space-x-2 mb-4">
          <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900">目的地</h3>
        </div>
        <AirportSelector
          value={destination}
          onChange={setDestination}
          placeholder="选择目的地机场"
          mode="dep"
          className="w-full"
        />
      </div>

      <div className="bg-white/95 backdrop-blur-3xl rounded-2xl shadow-xl border border-white/20 p-6 space-y-4">
        <div className="flex items-center space-x-2 mb-4">
          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900">出发日期</h3>
        </div>
        <input
          type="date"
          value={departureDate}
          onChange={(e) => setDepartureDate(e.target.value)}
          min={getTodayDate()}
          className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          required
        />
      </div>

      <div className="bg-white/95 backdrop-blur-3xl rounded-2xl shadow-xl border border-white/20 p-6 space-y-4">
        <div className="flex items-center space-x-2 mb-4">
          <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
            <svg className="w-4 h-4 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
            </svg>
          </div>
          <h3 className="text-lg font-semibold text-gray-900">舱位等级</h3>
        </div>
        <select
          value={cabinClass}
          onChange={(e) => setCabinClass(e.target.value)}
          className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="ECONOMY">经济舱</option>
          <option value="BUSINESS">商务舱</option>
        </select>
      </div>

      <div className="md:col-span-2 text-center pt-4">
        <button
          type="submit"
          disabled={isLoading}
          className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-700 hover:from-blue-700 hover:via-purple-700 hover:to-blue-800 text-white px-16 py-4 rounded-2xl font-semibold text-lg shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105 disabled:transform-none disabled:from-gray-400 disabled:to-gray-500"
        >
          {isLoading ? '搜索中...' : '开始搜索'}
        </button>
      </div>
    </div>
  );

  return (
    <div className="w-full max-w-6xl mx-auto">
      <form onSubmit={handleSubmit} className="relative">
        {style === 'minimal' && <MinimalStyle />}
        {style === 'segmented' && <SegmentedStyle />}
        {style === 'compact' && <CompactStyle />}
        {style === 'modern' && <CardStyle />}
      </form>
    </div>
  );
};

export default FlightSearchFormStyles;
