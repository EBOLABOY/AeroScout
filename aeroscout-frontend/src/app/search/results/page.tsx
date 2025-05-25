'use client';

import React from 'react';
import { useFlightResultsStore, FlightItinerary } from '@/store/flightResultsStore';
import { useRouter } from 'next/navigation';

export default function FlightResultsPage() {
  const router = useRouter();
  const {
    directFlights,
    comboDeals,
    searchStatus,
    disclaimers,
    error
  } = useFlightResultsStore();

  const totalFlights = directFlights.length + comboDeals.length;

  return (
    <div className="min-h-screen bg-white">
      {/* 顶部导航 - 苹果官网风格 */}
      <nav className="bg-white/90 backdrop-blur-md sticky top-0 z-50 border-b border-[#E5E5EA]">
        <div className="max-w-[980px] mx-auto px-5 py-3 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => router.push('/')}
              className="flex items-center text-[#1D1D1F] hover:text-[#0071E3] transition-apple"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span className="text-[14px] font-medium">返回搜索</span>
            </button>
            <div className="h-4 w-px bg-[#E5E5EA]"></div>
            <h1 className="text-[21px] font-medium text-[#1D1D1F]">航班搜索结果</h1>
          </div>

          {/* 搜索状态指示器 */}
          <div className="flex items-center space-x-3">
            {searchStatus === 'loading' && (
              <div className="flex items-center text-[#0071E3]">
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-[#0071E3] border-t-transparent mr-2"></div>
                <span className="text-[14px] font-medium">搜索中...</span>
              </div>
            )}
            {totalFlights > 0 && (
              <div className="bg-[#34C759]/10 text-[#34C759] px-3 py-1.5 rounded-full text-[14px] font-medium">
                找到 {totalFlights} 个航班
              </div>
            )}
          </div>
        </div>
      </nav>

      <div className="max-w-[980px] mx-auto px-5 py-8">
        {/* 错误状态 */}
        {error && (
          <div className="mb-6 bg-[#FF3B30]/5 border border-[#FF3B30]/20 rounded-2xl p-6">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-[#FF3B30]/10 rounded-full flex items-center justify-center mr-4">
                <svg className="w-5 h-5 text-[#FF3B30]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h3 className="text-[17px] font-semibold text-[#1D1D1F] mb-1">搜索出现问题</h3>
                <p className="text-[15px] text-[#86868B]">
                  {typeof error === 'string' ? error : error.message}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* 加载状态 */}
        {searchStatus === 'loading' && totalFlights === 0 && (
          <div className="text-center py-20">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-[#0071E3]/10 rounded-full mb-6">
              <div className="animate-spin rounded-full h-10 w-10 border-3 border-[#0071E3] border-t-transparent"></div>
            </div>
            <h2 className="text-[28px] font-semibold text-[#1D1D1F] mb-3">正在搜索最优航班</h2>
            <p className="text-[17px] text-[#86868B]">请稍候，我们正在为您寻找最佳选择...</p>
          </div>
        )}

        {/* 无结果状态 */}
        {searchStatus === 'success' && totalFlights === 0 && (
          <div className="text-center py-20">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-[#86868B]/10 rounded-full mb-6">
              <svg className="w-10 h-10 text-[#86868B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
              </svg>
            </div>
            <h2 className="text-[28px] font-semibold text-[#1D1D1F] mb-3">未找到符合条件的航班</h2>
            <p className="text-[17px] text-[#86868B] mb-8">请尝试调整您的搜索条件</p>
            <button
              onClick={() => router.push('/')}
              className="bg-[#0071E3] hover:bg-[#0077ED] text-white px-6 py-3 rounded-full text-[17px] font-medium shadow-apple-sm transition-apple"
            >
              重新搜索
            </button>
          </div>
        )}

        {/* 直飞航班 */}
        {directFlights.length > 0 && (
          <div className="mb-12">
            <div className="flex items-center mb-8">
              <div className="flex items-center">
                <div className="w-4 h-4 bg-[#34C759] rounded-full mr-4"></div>
                <h2 className="text-[28px] font-semibold text-[#1D1D1F]">直飞航班</h2>
                <span className="ml-4 bg-[#34C759]/10 text-[#34C759] px-3 py-1.5 rounded-full text-[14px] font-medium">
                  {directFlights.length} 个
                </span>
              </div>
            </div>
            <div className="space-y-4">
              {directFlights.map((flight, index) => (
                <FlightCard key={flight.id || index} flight={flight} />
              ))}
            </div>
          </div>
        )}

        {/* 组合航班 */}
        {comboDeals.length > 0 && (
          <div className="mb-12">
            <div className="flex items-center mb-8">
              <div className="flex items-center">
                <div className="w-4 h-4 bg-[#AF52DE] rounded-full mr-4"></div>
                <h2 className="text-[28px] font-semibold text-[#1D1D1F]">隐藏城市航班</h2>
                <span className="ml-4 bg-[#AF52DE]/10 text-[#AF52DE] px-3 py-1.5 rounded-full text-[14px] font-medium">
                  {comboDeals.length} 个
                </span>
              </div>
            </div>
            <div className="space-y-4">
              {comboDeals.map((flight, index) => (
                <FlightCard key={flight.id || index} flight={flight} />
              ))}
            </div>
          </div>
        )}

        {/* 免责声明 */}
        {disclaimers.length > 0 && (
          <div className="mt-12 bg-[#0071E3]/5 border border-[#0071E3]/20 rounded-2xl p-6">
            <h3 className="text-[17px] font-semibold text-[#1D1D1F] mb-4 flex items-center">
              <div className="w-5 h-5 bg-[#0071E3]/10 rounded-full flex items-center justify-center mr-3">
                <svg className="w-3 h-3 text-[#0071E3]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              重要提示
            </h3>
            <ul className="text-[15px] text-[#86868B] space-y-3">
              {disclaimers.map((disclaimer, index) => (
                <li key={index} className="flex items-start">
                  <span className="w-1.5 h-1.5 bg-[#86868B] rounded-full mr-3 mt-2 flex-shrink-0"></span>
                  <span>{disclaimer}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

// 简化的航班卡片组件
function FlightCard({ flight }: { flight: FlightItinerary }) {
  const formatTime = (timeStr: string) => {
    try {
      const date = new Date(timeStr);
      return date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      });
    } catch {
      return timeStr;
    }
  };

  const formatDate = (timeStr: string) => {
    try {
      const date = new Date(timeStr);
      return date.toLocaleDateString('zh-CN', {
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return '';
    }
  };

  const firstSegment = flight.segments[0];
  const lastSegment = flight.segments[flight.segments.length - 1];

  if (!firstSegment || !lastSegment) return null;

  return (
    <div className="bg-white rounded-2xl shadow-apple-sm border border-[#E8E8ED] hover:shadow-apple-md transition-apple">
      <div className="p-8">
        {/* 顶部：价格和标签 */}
        <div className="flex justify-between items-start mb-8">
          <div className="flex items-center space-x-3">
            {/* 根据航班类型和实际航段数量显示标签 */}
            {(() => {
              // 如果是隐藏城市航班，强制显示为中转航班
              if (flight.isHiddenCity || flight.hiddenDestination) {
                const actualStops = flight.segments ? flight.segments.length - 1 : 1; // 隐藏城市航班至少1次中转
                const displayStops = Math.max(actualStops, 1); // 确保至少显示1次中转
                return (
                  <span className="bg-[#0071E3]/10 text-[#0071E3] px-3 py-1.5 rounded-full text-[12px] font-medium">
                    {displayStops} 次中转
                  </span>
                );
              }

              // 普通航班逻辑
              if (flight.isDirectFlight || flight.numberOfStops === 0 || !flight.numberOfStops) {
                return (
                  <span className="bg-[#34C759]/10 text-[#34C759] px-3 py-1.5 rounded-full text-[12px] font-medium">
                    直飞
                  </span>
                );
              } else {
                return (
                  <span className="bg-[#0071E3]/10 text-[#0071E3] px-3 py-1.5 rounded-full text-[12px] font-medium">
                    {flight.numberOfStops} 次中转
                  </span>
                );
              }
            })()}
          </div>
          <div className="text-right">
            <div className="text-[32px] font-semibold text-[#1D1D1F] tracking-tight">
              ¥{flight.price.amount.toLocaleString()}
            </div>
            <div className="text-[14px] text-[#86868B] mt-1">含税价格</div>
          </div>
        </div>

        {/* 主要航班信息 */}
        <div className="flex items-center justify-between">
          {/* 出发信息 */}
          <div className="text-center">
            <div className="text-[32px] font-semibold text-[#1D1D1F] tracking-tight">
              {formatTime(firstSegment.departureTime)}
            </div>
            <div className="text-[14px] text-[#86868B] mt-2">
              {formatDate(firstSegment.departureTime)}
            </div>
            <div className="text-[21px] font-semibold text-[#1D1D1F] mt-4">
              {firstSegment.departureAirportCode}
            </div>
            <div className="text-[15px] text-[#86868B] mt-1">
              {firstSegment.departureCityName}
            </div>
          </div>

          {/* 航班路径 */}
          <div className="flex-1 mx-12">
            <div className="relative">
              <div className="flex items-center justify-center">
                <div className="flex-1 border-t-2 border-[#E8E8ED]"></div>
                <div className="mx-6 text-center">
                  <div className="bg-[#F5F5F7] rounded-full p-3 mb-3">
                    <svg className="w-6 h-6 text-[#86868B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                    </svg>
                  </div>
                  <div className="text-[15px] text-[#86868B] font-medium">
                    {flight.totalTravelTime ||
                     (flight.totalDurationMinutes && flight.totalDurationMinutes > 0
                       ? `${Math.floor(flight.totalDurationMinutes / 60)}h${flight.totalDurationMinutes % 60 > 0 ? ` ${flight.totalDurationMinutes % 60}m` : ''}`
                       : 'N/A')}
                  </div>
                  {(() => {
                    // 如果是隐藏城市航班，强制显示为中转航班
                    if (flight.isHiddenCity || flight.hiddenDestination) {
                      const actualStops = flight.segments ? flight.segments.length - 1 : 1; // 隐藏城市航班至少1次中转
                      const displayStops = Math.max(actualStops, 1); // 确保至少显示1次中转
                      return (
                        <div className="text-[12px] text-[#86868B] mt-2">
                          {displayStops} 次中转
                        </div>
                      );
                    }

                    // 普通航班逻辑
                    if (flight.numberOfStops === 0 || !flight.numberOfStops) {
                      return (
                        <div className="text-[12px] text-[#34C759] mt-2 font-medium">
                          直飞
                        </div>
                      );
                    } else {
                      return (
                        <div className="text-[12px] text-[#86868B] mt-2">
                          {flight.numberOfStops} 次中转
                        </div>
                      );
                    }
                  })()}
                </div>
                <div className="flex-1 border-t-2 border-[#E8E8ED]"></div>
              </div>
            </div>
          </div>

          {/* 到达信息 */}
          <div className="text-center">
            <div className="text-[32px] font-semibold text-[#1D1D1F] tracking-tight">
              {formatTime(lastSegment.arrivalTime)}
            </div>
            <div className="text-[14px] text-[#86868B] mt-2">
              {formatDate(lastSegment.arrivalTime)}
            </div>
            <div className="text-[21px] font-semibold text-[#1D1D1F] mt-4">
              {(flight.hiddenDestination && flight.hiddenDestination.code)
                ? flight.hiddenDestination.code
                : (lastSegment.arrivalAirportCode || 'N/A')}
            </div>
            <div className="text-[15px] text-[#86868B] mt-1">
              {(flight.hiddenDestination && flight.hiddenDestination.cityName)
                ? flight.hiddenDestination.cityName
                : (lastSegment.arrivalCityName || '未知城市')}
            </div>
            {/* 在落地时间下方显示实际目的地信息 */}
            {flight.hiddenDestination && (
              <div className="text-[12px] text-[#0071E3] mt-2 font-medium">
                {flight.hiddenDestination.cityName || flight.hiddenDestination.name}
              </div>
            )}
          </div>
        </div>

        {/* 航空公司信息 */}
        <div className="mt-8 pt-6 border-t border-[#E8E8ED]">
          <div className="flex items-center justify-between text-[15px]">
            <div className="flex items-center text-[#86868B]">
              <span className="font-medium text-[#1D1D1F]">航空公司:</span>
              <span className="ml-3">
                {flight.airlines?.map(airline => airline.name).join(', ') ||
                 flight.segments.map(seg => seg.airlineName).join(', ')}
              </span>
            </div>
            <div className="flex items-center text-[#86868B]">
              <span className="font-medium text-[#1D1D1F]">航班号:</span>
              <span className="ml-3">
                {flight.segments.map(seg => `${seg.airlineCode} ${seg.flightNumber}`).join(', ')}
              </span>
            </div>
          </div>
        </div>

        {/* 中转信息 */}
        {flight.transfers && flight.transfers.length > 0 && (
          <div className="mt-6 p-4 bg-[#FF9500]/5 border border-[#FF9500]/20 rounded-2xl">
            <div className="text-[15px]">
              <span className="font-semibold text-[#1D1D1F]">中转信息:</span>
              {flight.transfers.map((transfer, index) => (
                <span key={index} className="ml-3 text-[#86868B]">
                  在{transfer.city}中转{transfer.layoverTime}
                  {transfer.isDifferentAirport && <span className="text-[#FF9500] font-medium"> (需换机场)</span>}
                  {index < flight.transfers!.length - 1 && ', '}
                </span>
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
