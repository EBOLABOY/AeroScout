'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import {
  searchFlightsV2,
  FlightSearchRequestV2,
  SimplifiedSearchResponse,
  SimplifiedFlightItinerary,
  SimplifiedFlightSegment
} from '../../../lib/apiService';
import { useAlertStore } from '../../../store/alertStore';
import { useAuthStore } from '../../../store/authStore';
import { useAuthInit } from '../../../hooks/useAuthInit';

// 删除重复的接口定义，使用从 apiService 导入的类型

// 搜索步骤配置
const searchSteps = [
  { id: 0, title: '验证身份', description: '正在验证用户身份...', icon: '🔐' },
  { id: 1, title: '分析路线', description: '正在分析最优航线...', icon: '🗺️' },
  { id: 2, title: '查询航班', description: '正在搜索可用航班...', icon: '✈️' },
  { id: 3, title: '比较价格', description: '正在比较各航空公司价格...', icon: '💰' },
  { id: 4, title: '筛选结果', description: '正在筛选最优选项...', icon: '🔍' },
  { id: 5, title: '完成搜索', description: '搜索完成，正在加载结果...', icon: '✅' }
];

// 美观的搜索加载组件
const SearchLoadingComponent: React.FC<{
  currentStep: number;
  isAuthLoading: boolean;
  isInitialized: boolean;
}> = ({ currentStep, isAuthLoading, isInitialized }) => {
  const [displayStep, setDisplayStep] = useState(0);

  useEffect(() => {
    if (isAuthLoading || !isInitialized) {
      setDisplayStep(0);
      return;
    }

    // 自动推进步骤
    const stepInterval = setInterval(() => {
      setDisplayStep(prev => {
        if (prev < currentStep) {
          return prev + 1;
        }
        return prev;
      });
    }, 800); // 每800ms推进一步

    return () => clearInterval(stepInterval);
  }, [currentStep, isAuthLoading, isInitialized]);

  const currentStepData = searchSteps[displayStep] || searchSteps[0];
  const progress = ((displayStep + 1) / searchSteps.length) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#F8FAFC] via-[#F1F5F9] to-[#E2E8F0] flex items-center justify-center p-6">
      <div className="max-w-md w-full">
        {/* 主要加载卡片 */}
        <div className="bg-white rounded-3xl shadow-2xl p-8 border border-[#E2E8F0]">
          {/* 顶部图标和标题 */}
          <div className="text-center mb-8">
            <div className="w-20 h-20 mx-auto mb-4 bg-gradient-to-br from-[#3B82F6] to-[#1D4ED8] rounded-2xl flex items-center justify-center shadow-lg transform rotate-3 hover:rotate-0 transition-transform duration-500">
              <span className="text-3xl">{currentStepData.icon}</span>
            </div>
            <h2 className="text-[24px] font-bold text-[#1E293B] mb-2">
              {currentStepData.title}
            </h2>
            <p className="text-[16px] text-[#64748B]">
              {currentStepData.description}
            </p>
          </div>

          {/* 进度条 */}
          <div className="mb-8">
            <div className="flex justify-between items-center mb-3">
              <span className="text-[14px] font-medium text-[#64748B]">搜索进度</span>
              <span className="text-[14px] font-bold text-[#3B82F6]">{Math.round(progress)}%</span>
            </div>
            <div className="w-full bg-[#F1F5F9] rounded-full h-3 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-[#3B82F6] to-[#1D4ED8] rounded-full transition-all duration-1000 ease-out shadow-sm"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>

          {/* 步骤列表 */}
          <div className="space-y-3">
            {searchSteps.map((step, index) => (
              <div
                key={step.id}
                className={`flex items-center space-x-3 p-3 rounded-xl transition-all duration-300 ${
                  index <= displayStep
                    ? 'bg-gradient-to-r from-[#EBF4FF] to-[#DBEAFE] border border-[#BFDBFE]'
                    : 'bg-[#F8FAFC] border border-[#E2E8F0]'
                }`}
              >
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-[12px] font-bold transition-all duration-300 ${
                  index < displayStep
                    ? 'bg-[#10B981] text-white shadow-lg'
                    : index === displayStep
                    ? 'bg-[#3B82F6] text-white shadow-lg animate-pulse'
                    : 'bg-[#E2E8F0] text-[#94A3B8]'
                }`}>
                  {index < displayStep ? '✓' : index === displayStep ? '⟳' : step.id + 1}
                </div>
                <div className="flex-1">
                  <div className={`text-[14px] font-medium transition-colors duration-300 ${
                    index <= displayStep ? 'text-[#1E293B]' : 'text-[#94A3B8]'
                  }`}>
                    {step.title}
                  </div>
                </div>
                <div className="text-[16px]">
                  {step.icon}
                </div>
              </div>
            ))}
          </div>

          {/* 底部提示 */}
          <div className="mt-8 text-center">
            {displayStep === 5 ? (
              <div className="inline-flex items-center space-x-2 bg-[#ECFDF5] text-[#059669] px-4 py-2 rounded-full text-[13px] font-medium border border-[#A7F3D0] animate-bounce">
                <div className="w-2 h-2 bg-[#059669] rounded-full"></div>
                <span>搜索完成！正在加载结果...</span>
              </div>
            ) : (
              <div className="inline-flex items-center space-x-2 bg-[#F0F9FF] text-[#0369A1] px-4 py-2 rounded-full text-[13px] font-medium border border-[#BAE6FD]">
                <div className="w-2 h-2 bg-[#0369A1] rounded-full animate-pulse"></div>
                <span>正在为您寻找最优航班选择</span>
              </div>
            )}
          </div>
        </div>

        {/* 底部装饰 */}
        <div className="text-center mt-6">
          <div className="flex items-center justify-center space-x-2 mb-2">
            <div className="text-[16px] animate-bounce">✈️</div>
            <div className="w-8 border-t border-dashed border-[#CBD5E1] animate-pulse"></div>
            <div className="text-[16px] animate-bounce animation-delay-300">🌍</div>
          </div>
          <p className="text-[13px] text-[#94A3B8]">
            AeroScout • 智能航班搜索
          </p>
        </div>
      </div>
    </div>
  );
};

// 格式化时间显示 - 处理简化API的时间格式
const formatTime = (timeString: string) => {
  try {
    if (!timeString) return 'N/A';
    const date = new Date(timeString);
    if (isNaN(date.getTime())) return 'N/A';
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  } catch {
    return 'N/A';
  }
};

// 格式化持续时间
const formatDuration = (minutes: number) => {
  if (!minutes || minutes <= 0) return 'N/A';
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  return `${hours}h ${mins}m`;
};

// 获取中转信息 - 处理新的API数据结构
const getStopInfo = (flight: SimplifiedFlightItinerary) => {

  const layovers = flight.user_journey_layovers_to_display;

  // 根据 display_flight_type 判断航班类型
  if (flight.display_flight_type === '直达') {
    return { text: '直飞', color: 'text-[#34C759]' };
  }

  // 隐藏城市航班 - 显示用户感知的目的地作为中转
  if (flight.display_flight_type.includes('隐藏城市')) {
    if (flight.user_perceived_destination_airport) {
      // 将用户感知的目的地作为中转显示
      return {
        text: `经停 ${flight.user_perceived_destination_airport.code}`,
        detail: flight.user_perceived_destination_airport.name,
        color: 'text-[#8B5CF6]'
      };
    }
    return { text: '组合优惠', color: 'text-[#8B5CF6]' };
  }

  // 普通中转航班
  if (layovers && layovers.length > 0) {
    const stopAirports = layovers.map(layover => layover.airport_code);
    return {
      text: `${layovers.length}次中转`,
      detail: stopAirports.join(', '),
      color: 'text-[#FF9500]'
    };
  }

  // 默认为直飞
  return { text: '直飞', color: 'text-[#34C759]' };
};

// 动态判断航班类型 - 基于新的API数据结构
const getFlightType = (flight: SimplifiedFlightItinerary): 'direct' | 'transfer' | 'hidden_city' => {
  // 根据 display_flight_type 字段判断
  if (flight.display_flight_type === '直达') {
    return 'direct';
  }

  if (flight.display_flight_type.includes('隐藏城市')) {
    return 'hidden_city';
  }

  // 根据中转次数判断
  if (flight.user_journey_layovers_to_display && flight.user_journey_layovers_to_display.length > 0) {
    return 'transfer';
  }

  return 'direct';
};

// 获取航班显示类型（用于标签显示）
const getDisplayType = (flight: SimplifiedFlightItinerary): 'direct' | 'transfer' | 'hidden_city' => {
  return getFlightType(flight);
};

// 机场信息映射 (暂时保留但未使用)
const getAirportInfo = (code: string) => {
  const airportMap: Record<string, { name: string; city: string }> = {
    // 中国主要机场
    'PKX': { name: '北京大兴国际机场', city: '北京市' },
    'PEK': { name: '北京首都国际机场', city: '北京市' },
    'SHA': { name: '上海虹桥国际机场', city: '上海市' },
    'PVG': { name: '上海浦东国际机场', city: '上海市' },
    'CAN': { name: '广州白云国际机场', city: '广州市' },
    'SZX': { name: '深圳宝安国际机场', city: '深圳市' },
    'CTU': { name: '成都双流国际机场', city: '成都市' },
    'CSX': { name: '长沙黄花国际机场', city: '长沙市' },
    'WUH': { name: '武汉天河国际机场', city: '武汉市' },
    'XIY': { name: '西安咸阳国际机场', city: '西安市' },
    'KMG': { name: '昆明长水国际机场', city: '昆明市' },
    'URC': { name: '乌鲁木齐地窝堡国际机场', city: '乌鲁木齐市' },
    'TSN': { name: '天津滨海国际机场', city: '天津市' },
    'NKG': { name: '南京禄口国际机场', city: '南京市' },
    'HGH': { name: '杭州萧山国际机场', city: '杭州市' },
    'CGO': { name: '郑州新郑国际机场', city: '郑州市' },
    'SJW': { name: '石家庄正定国际机场', city: '石家庄市' },
    'TNA': { name: '济南遥墙国际机场', city: '济南市' },
    'TAO': { name: '青岛胶东国际机场', city: '青岛市' },
    'DLC': { name: '大连周水子国际机场', city: '大连市' },
    'SHE': { name: '沈阳桃仙国际机场', city: '沈阳市' },
    'CGQ': { name: '长春龙嘉国际机场', city: '长春市' },
    'HRB': { name: '哈尔滨太平国际机场', city: '哈尔滨市' },
    'HFE': { name: '合肥新桥国际机场', city: '合肥市' },
    'FOC': { name: '福州长乐国际机场', city: '福州市' },
    'XMN': { name: '厦门高崎国际机场', city: '厦门市' },
    'NNG': { name: '南宁吴圩国际机场', city: '南宁市' },
    'HAK': { name: '海口美兰国际机场', city: '海口市' },
    'SYX': { name: '三亚凤凰国际机场', city: '三亚市' },

    // 国际主要机场
    'LHR': { name: '伦敦希思罗机场', city: '伦敦' },
    'LGW': { name: '伦敦盖特威克机场', city: '伦敦' },
    'CDG': { name: '巴黎戴高乐机场', city: '巴黎' },
    'ORY': { name: '巴黎奥利机场', city: '巴黎' },
    'FRA': { name: '法兰克福机场', city: '法兰克福' },
    'MUC': { name: '慕尼黑机场', city: '慕尼黑' },
    'AMS': { name: '阿姆斯特丹史基浦机场', city: '阿姆斯特丹' },
    'MAD': { name: '马德里巴拉哈斯机场', city: '马德里' },
    'FCO': { name: '罗马菲乌米奇诺机场', city: '罗马' },
    'ZUR': { name: '苏黎世机场', city: '苏黎世' },
    'VIE': { name: '维也纳国际机场', city: '维也纳' },
    'CPH': { name: '哥本哈根机场', city: '哥本哈根' },
    'ARN': { name: '斯德哥尔摩阿兰达机场', city: '斯德哥尔摩' },
    'HEL': { name: '赫尔辛基万塔机场', city: '赫尔辛基' },
    'SVO': { name: '莫斯科谢列梅捷沃机场', city: '莫斯科' },
    'JFK': { name: '纽约肯尼迪国际机场', city: '纽约' },
    'LAX': { name: '洛杉矶国际机场', city: '洛杉矶' },
    'ORD': { name: '芝加哥奥黑尔国际机场', city: '芝加哥' },
    'SFO': { name: '旧金山国际机场', city: '旧金山' },
    'SEA': { name: '西雅图塔科马国际机场', city: '西雅图' },
    'YVR': { name: '温哥华国际机场', city: '温哥华' },
    'YYZ': { name: '多伦多皮尔逊国际机场', city: '多伦多' },
    'NRT': { name: '东京成田国际机场', city: '东京' },
    'HND': { name: '东京羽田机场', city: '东京' },
    'ICN': { name: '首尔仁川国际机场', city: '首尔' },
    'GMP': { name: '首尔金浦国际机场', city: '首尔' },
    'SIN': { name: '新加坡樟宜机场', city: '新加坡' },
    'BKK': { name: '曼谷素万那普机场', city: '曼谷' },
    'KUL': { name: '吉隆坡国际机场', city: '吉隆坡' },
    'SYD': { name: '悉尼金斯福德·史密斯机场', city: '悉尼' },
    'MEL': { name: '墨尔本机场', city: '墨尔本' },
    'DXB': { name: '迪拜国际机场', city: '迪拜' },
    'DOH': { name: '多哈哈马德国际机场', city: '多哈' },
    'IST': { name: '伊斯坦布尔机场', city: '伊斯坦布尔' }
  };

  return airportMap[code.toUpperCase()] || { name: `${code}机场`, city: code };
};

// 获取出发机场信息 - 使用新的API数据结构
const getDepartureAirportInfo = (flight: SimplifiedFlightItinerary) => {
  // 使用票面起始机场信息
  if (flight.ticketed_origin_airport) {
    return {
      code: flight.ticketed_origin_airport.code,
      name: flight.ticketed_origin_airport.name,
      city: flight.ticketed_origin_airport.city
    };
  }

  // 备选：使用第一个航段的起始机场
  if (flight.user_journey_segments_to_display && flight.user_journey_segments_to_display.length > 0) {
    const firstSegment = flight.user_journey_segments_to_display[0];
    return {
      code: firstSegment.origin.code,
      name: firstSegment.origin.name,
      city: firstSegment.origin.city
    };
  }

  return { code: 'N/A', name: '', city: '' };
};

// 获取实际目的地信息 - 使用新的API数据结构
const getActualDestination = (flight: SimplifiedFlightItinerary) => {
  // 对于隐藏城市航班，显示票面终点而不是用户感知的目的地
  if (flight.display_flight_type.includes('隐藏城市') && flight.ticketed_final_destination_airport) {
    return {
      code: flight.ticketed_final_destination_airport.code,
      name: flight.ticketed_final_destination_airport.name,
      city: flight.ticketed_final_destination_airport.city
    };
  }

  // 普通航班使用用户感知的目的地机场
  if (flight.user_perceived_destination_airport) {
    return {
      code: flight.user_perceived_destination_airport.code,
      name: flight.user_perceived_destination_airport.name,
      city: flight.user_perceived_destination_airport.city
    };
  }

  // 备选：使用最后一个航段的目的地
  if (flight.user_journey_segments_to_display && flight.user_journey_segments_to_display.length > 0) {
    const lastSegment = flight.user_journey_segments_to_display[flight.user_journey_segments_to_display.length - 1];
    return {
      code: lastSegment.ticketed_destination.code,
      name: lastSegment.ticketed_destination.name,
      city: lastSegment.ticketed_destination.city
    };
  }

  return { code: 'N/A', name: '', city: '' };
};

// 航班卡片组件
const FlightCard: React.FC<{
  flight: SimplifiedFlightItinerary;
  type?: 'direct' | 'transfer' | 'hidden_city';  // 改为可选，将动态判断
  index: number;
}> = ({ flight, type, index }) => {
  // 动态判断航班类型（如果没有传入type）
  const actualType = type || getDisplayType(flight);

  // 获取出发和到达机场信息
  const departureInfo = getDepartureAirportInfo(flight);
  const actualDestination = getActualDestination(flight);

  // 获取航班ID的简化版本
  const getShortFlightId = (id: string) => {
    if (!id) return 'N/A';
    try {
      if (id.includes(':')) {
        return id.split(':')[0] || id.substring(0, 8);
      }
      return id.substring(0, 8);
    } catch {
      return id.substring(0, 8);
    }
  };

  // 格式化完整的航班代码（航空公司代码 + 航班号）
  const getFullFlightNumber = (segment: SimplifiedFlightSegment) => {
    if (!segment) return 'N/A';

    const carrierCode = segment.marketing_carrier?.code || '';
    const flightNumber = segment.flight_number || '';

    // 如果航班号已经包含航空公司代码，直接返回
    if (flightNumber && flightNumber.match(/^[A-Z]{2,3}\d+/)) {
      return flightNumber;
    }

    // 否则组合航空公司代码和航班号
    if (carrierCode && flightNumber) {
      // 移除航班号中可能已有的航空公司代码
      const cleanFlightNumber = flightNumber.replace(/^[A-Z]{2,3}/, '');
      return `${carrierCode}${cleanFlightNumber}`;
    }

    return flightNumber || carrierCode || 'N/A';
  };

  const stopInfo = getStopInfo(flight);
  const price = flight.price?.amount || 0;
  const currency = flight.price?.currency || 'CNY';
  const currencySymbol = currency === 'EUR' ? '€' : currency === 'USD' ? '$' : '¥';

  // 判断是否为隐藏城市航班
  const isHiddenCity = flight.display_flight_type.includes('隐藏城市');

  // 判断是否为虚拟联运
  const isVirtualInterlining = flight.api_travel_hack_info?.is_virtual_interlining || false;

  // 获取类型标签
  const getTypeLabel = () => {
    switch (actualType) {
      case 'direct':
        return { text: '直飞', color: 'bg-[#34C759]', icon: '✈️' };
      case 'transfer':
        return { text: '中转', color: 'bg-[#FF9500]', icon: '🔄' };
      case 'hidden_city':
        return { text: '组合优惠', color: 'bg-[#8B5CF6]', icon: '💎' };
      default:
        return { text: '航班', color: 'bg-[#86868B]', icon: '✈️' };
    }
  };



  return (
    <div className={`bg-white rounded-2xl sm:rounded-3xl shadow-lg border-2 p-4 sm:p-6 lg:p-8 hover:shadow-xl transition-all duration-300 touch-manipulation ${
      isHiddenCity ? 'border-[#8B5CF6] bg-gradient-to-br from-[#F8F5FF] via-white to-[#FEFCFF]' : 'border-[#E2E8F0]'
    }`}
    style={{
      WebkitTapHighlightColor: 'transparent',
      touchAction: 'manipulation'
    }}>
      {/* 头部信息 - 移动端优化 */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between space-y-4 sm:space-y-0 mb-6 sm:mb-8">
        <div className="flex flex-col space-y-2 sm:space-y-3 min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2 sm:gap-3">
            <div className={`px-3 sm:px-5 py-1.5 sm:py-2.5 rounded-full text-[12px] sm:text-[14px] font-bold shadow-lg ${
              isHiddenCity
                ? 'bg-gradient-to-r from-[#8B5CF6] to-[#A855F7] text-white'
                : flight.display_flight_type === '直达'
                ? 'bg-gradient-to-r from-[#10B981] to-[#059669] text-white'
                : 'bg-gradient-to-r from-[#F59E0B] to-[#D97706] text-white'
            }`}>
              {flight.display_flight_type}
            </div>
            {isVirtualInterlining && (
              <div className="px-2 sm:px-3 py-1 sm:py-1.5 rounded-full text-[10px] sm:text-[12px] font-semibold bg-[#EF4444] text-white shadow-md">
                虚拟联运
              </div>
            )}
            {flight.booking_options && flight.booking_options.length > 1 && (
              <div className="px-2 sm:px-3 py-1 sm:py-1.5 rounded-full text-[10px] sm:text-[12px] font-semibold bg-[#F59E0B] text-white shadow-md">
                {flight.booking_options.length} PNR
              </div>
            )}
          </div>
          <div className="text-[11px] sm:text-[13px] text-[#64748B] font-medium">
            航班 #{getShortFlightId(flight.id)}
          </div>
        </div>
        <div className="text-left sm:text-right flex-shrink-0">
          <div className="text-[24px] sm:text-[28px] lg:text-[32px] font-bold text-[#1E293B] leading-none">
            {currencySymbol}{price.toLocaleString()}
          </div>
          <div className="text-[12px] sm:text-[14px] text-[#64748B] mt-1">
            {currency} • {flight.booking_options?.length || 1} 个选项
          </div>
          {flight.booking_options && flight.booking_options.length > 1 && (
            <div className="text-[10px] sm:text-[12px] text-[#10B981] mt-1">
              最低价格
            </div>
          )}
        </div>
      </div>

      {/* 主要航班信息 - 移动端优化 */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-6 lg:space-y-0 mb-6 sm:mb-8">
        <div className="flex flex-col sm:flex-row sm:items-center space-y-4 sm:space-y-0 sm:space-x-4 lg:space-x-10 flex-1">
          {/* 出发信息 */}
          <div className="text-center sm:text-left min-w-0 flex-shrink-0">
            <div className="text-[24px] sm:text-[28px] lg:text-[32px] font-bold text-[#1E293B] leading-none">
              {departureInfo.code}
            </div>
            <div className="text-[14px] sm:text-[16px] lg:text-[18px] font-semibold text-[#1E293B] mt-1 sm:mt-2">
              {formatTime(flight.user_journey_segments_to_display && flight.user_journey_segments_to_display.length > 0
                ? flight.user_journey_segments_to_display[0]?.departure?.local_time
                : flight.ticketed_departure_datetime_local || '')}
            </div>
            <div className="text-[12px] sm:text-[14px] text-[#64748B] font-semibold mt-1 max-w-[120px] sm:max-w-[140px] truncate mx-auto sm:mx-0">
              {departureInfo.name}
            </div>
            <div className="text-[11px] sm:text-[13px] text-[#94A3B8] mt-0.5">
              {departureInfo.city}
            </div>
          </div>

          {/* 航班路径 - 移动端优化 */}
          <div className="flex-1 text-center px-2 sm:px-4 lg:px-6">
            <div className="text-[14px] sm:text-[16px] text-[#64748B] font-semibold mb-2 sm:mb-3">
              {formatDuration(flight.user_journey_duration_minutes)}
            </div>

            {/* 航班路径可视化 - 移动端优化 */}
            <div className="flex items-center justify-center space-x-2 sm:space-x-4 mb-3 sm:mb-4">
              <div className="w-3 h-3 sm:w-4 sm:h-4 bg-[#10B981] rounded-full shadow-lg"></div>
              <div className="flex-1 border-t-2 sm:border-t-3 border-dashed border-[#CBD5E1] relative">
                {flight.user_journey_layovers_to_display && flight.user_journey_layovers_to_display.length > 0 && (
                  <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                    <div className="w-3 h-3 sm:w-5 sm:h-5 bg-[#F59E0B] rounded-full shadow-lg border-2 sm:border-3 border-white"></div>
                  </div>
                )}
              </div>
              <div className="w-3 h-3 sm:w-4 sm:h-4 bg-[#EF4444] rounded-full shadow-lg"></div>
            </div>

            <div className={`text-[12px] sm:text-[14px] font-bold ${stopInfo.color}`}>
              {stopInfo.text}
              {stopInfo.detail && (
                <div className="text-[10px] sm:text-[12px] text-[#64748B] mt-1 font-medium">
                  经停: {stopInfo.detail}
                </div>
              )}
            </div>
          </div>

          {/* 到达信息 */}
          <div className="text-center sm:text-right min-w-0 flex-shrink-0">
            <div className="text-[24px] sm:text-[28px] lg:text-[32px] font-bold text-[#1E293B] leading-none">
              {actualDestination.code}
            </div>
            <div className="text-[14px] sm:text-[16px] lg:text-[18px] font-semibold text-[#1E293B] mt-1 sm:mt-2">
              {formatTime(flight.user_journey_arrival_datetime_local)}
            </div>
            <div className="text-[12px] sm:text-[14px] text-[#64748B] font-semibold mt-1 max-w-[120px] sm:max-w-[140px] truncate mx-auto sm:mx-0">
              {actualDestination.name}
            </div>
            <div className="text-[11px] sm:text-[13px] text-[#94A3B8] mt-0.5">
              {actualDestination.city}
            </div>
          </div>
        </div>

        {/* 预订按钮 - 移动端优化 */}
        <div className="lg:ml-10 flex-shrink-0">
          <button
            onClick={() => {
              if (flight.default_booking_url) {
                window.open(flight.default_booking_url, '_blank');
              }
            }}
            className="w-full lg:w-auto bg-gradient-to-r from-[#3B82F6] to-[#1D4ED8] hover:from-[#2563EB] hover:to-[#1E40AF] active:from-[#1E40AF] active:to-[#1E3A8A] text-white px-6 sm:px-8 lg:px-10 py-3 sm:py-4 rounded-xl sm:rounded-2xl font-bold shadow-xl hover:shadow-2xl active:shadow-lg transition-all duration-200 transform hover:scale-105 active:scale-95 text-[14px] sm:text-[16px] min-h-[48px] flex items-center justify-center touch-manipulation"
            style={{
              WebkitTapHighlightColor: 'transparent',
              touchAction: 'manipulation'
            }}
          >
            立即预订
          </button>
        </div>
      </div>

      {/* 详细航段信息 - 移动端优化 */}
      {flight.user_journey_segments_to_display && flight.user_journey_segments_to_display.length > 0 && (
        <div className="border-t border-[#E2E8F0] pt-4 sm:pt-6">
          <div className="text-[14px] sm:text-[16px] font-semibold text-[#1E293B] mb-3 sm:mb-4 flex items-center">
            <svg className="w-4 h-4 sm:w-5 sm:h-5 mr-2 text-[#64748B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
            航段详情
          </div>
          <div className="space-y-3 sm:space-y-4">
            {flight.user_journey_segments_to_display.map((segment, segIndex) => (
              <div key={segIndex} className="bg-[#F8FAFC] rounded-xl sm:rounded-2xl p-3 sm:p-4 border border-[#E2E8F0]">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
                  <div className="flex flex-col xs:flex-row xs:items-center space-y-2 xs:space-y-0 xs:space-x-3 sm:space-x-4">
                    <div className="bg-white rounded-lg sm:rounded-xl px-2 sm:px-3 py-1.5 sm:py-2 border border-[#E2E8F0] self-start xs:self-auto">
                      <span className="font-bold text-[12px] sm:text-[14px] text-[#1E293B]">{getFullFlightNumber(segment)}</span>
                    </div>
                    <div className="min-w-0">
                      <div className="font-semibold text-[12px] sm:text-[14px] text-[#1E293B] truncate">
                        {segment.marketing_carrier?.name || segment.marketing_carrier?.code || 'N/A'}
                      </div>
                      {segment.operating_carrier && segment.operating_carrier.code !== segment.marketing_carrier?.code && (
                        <div className="text-[10px] sm:text-[12px] text-[#64748B] truncate">
                          执飞: {segment.operating_carrier.name || segment.operating_carrier.code}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="text-left sm:text-right">
                    <div className="font-semibold text-[12px] sm:text-[14px] text-[#1E293B]">
                      {segment.origin.code} → {segment.ticketed_destination.code}
                    </div>
                    <div className="text-[10px] sm:text-[12px] text-[#64748B]">
                      {formatDuration(segment.duration_minutes)}
                    </div>
                  </div>
                </div>
                <div className="mt-2 sm:mt-3 flex flex-col xs:flex-row xs:items-center xs:justify-between space-y-1 xs:space-y-0 text-[11px] sm:text-[13px] text-[#64748B]">
                  <div className="truncate">
                    <span className="font-medium">{formatTime(segment.departure.local_time)}</span>
                    <span className="mx-1 sm:mx-2">•</span>
                    <span className="truncate">{segment.origin.name}</span>
                  </div>
                  <div className="text-left xs:text-right truncate">
                    <span className="font-medium">{formatTime(segment.arrival.local_time)}</span>
                    <span className="mx-1 sm:mx-2">•</span>
                    <span className="truncate">{segment.ticketed_destination.name}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 隐藏城市航班的特殊提示 - 增强版 */}
      {flight.user_alert_notes && flight.user_alert_notes.length > 0 && (() => {
        // 过滤掉包含"票面终点"的提示信息
        const filteredNotes = flight.user_alert_notes.filter(note =>
          !note.includes('票面终点')
        );

        if (filteredNotes.length === 0) return null;

        return (
          <div className="border-t border-[#E2E8F0] pt-6">
            <div className="text-[16px] font-semibold text-[#EF4444] mb-4 flex items-center">
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
              重要提示
            </div>
            <div className="space-y-3">
              {filteredNotes.map((note, noteIndex) => (
                <div key={noteIndex} className="bg-gradient-to-r from-[#FEF2F2] to-[#FFF7ED] border border-[#FECACA] rounded-2xl p-4">
                  <div className="flex items-start space-x-3">
                    <div className="w-6 h-6 bg-[#EF4444] rounded-full flex items-center justify-center flex-shrink-0 mt-0.5">
                      <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01" />
                      </svg>
                    </div>
                    <div className="text-[14px] text-[#DC2626] font-medium leading-relaxed">
                      {note}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      })()}


    </div>
  );
};

const FlightSearchResults: React.FC = () => {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { showAlert } = useAlertStore();

  const { isInitialized, isLoading: authLoading } = useAuthInit();

  const [searchResults, setSearchResults] = useState<SimplifiedSearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchStep, setSearchStep] = useState(0); // 搜索步骤状态

  // 计算总航班数 - 包括直飞和组合优惠航班
  const totalFlights = searchResults ?
    (searchResults.direct_flights?.length || 0) +
    (searchResults.hidden_city_flights?.length || 0) : 0;

  useEffect(() => {
    // 等待认证初始化完成
    if (!isInitialized || authLoading) {
      return;
    }

    const performSearch = async () => {
      try {
        setIsLoading(true);
        setError(null);
        setSearchStep(1); // 开始分析路线

        // 从URL参数构建搜索请求
        const searchData: FlightSearchRequestV2 = {
          origin_iata: searchParams.get('origin') || '',
          destination_iata: searchParams.get('destination') || '',
          departure_date_from: searchParams.get('departureDate') || '',
          departure_date_to: searchParams.get('departureDate') || '',
          return_date_from: searchParams.get('returnDate') || undefined,
          return_date_to: searchParams.get('returnDate') || undefined,
          adults: parseInt(searchParams.get('adults') || '1'),
          children: parseInt(searchParams.get('children') || '0'),
          infants: parseInt(searchParams.get('infants') || '0'),
          cabin_class: searchParams.get('cabinClass') || 'ECONOMY',
          direct_flights_only_for_primary: searchParams.get('directFlightsOnly') === 'true',
          enable_hub_probe: searchParams.get('enableHubProbe') === 'true',
          is_one_way: searchParams.get('isOneWay') === 'true',
          market: 'cn',
          // 添加搜索配置字段
          include_hidden_city: true,  // 包含组合优惠航班
          max_stopover_count: 3,
          direct_flights_only: false,
          max_results: 50,
          enable_cache: true,
          sort_strategy: 'PRICE_ASC'
        };

        // 验证必需参数
        if (!searchData.origin_iata || !searchData.destination_iata || !searchData.departure_date_from) {
          throw new Error('缺少必需的搜索参数');
        }

        // 模拟搜索步骤推进
        setTimeout(() => setSearchStep(2), 1000); // 查询航班
        setTimeout(() => setSearchStep(3), 2000); // 比较价格
        setTimeout(() => setSearchStep(4), 3000); // 筛选结果

        const results = await searchFlightsV2(searchData);

        setSearchStep(5); // 完成搜索
        setTimeout(() => {
          setSearchResults(results);
          setIsLoading(false);
        }, 1200); // 延迟显示结果，让用户看到完成动画
      } catch (err) {
        console.error('航班搜索失败:', err);
        const errorMessage = err instanceof Error ? err.message : '搜索失败，请稍后重试';
        setError(errorMessage);
        showAlert(errorMessage, 'error');
      } finally {
        setIsLoading(false);
      }
    };

    if (searchParams.get('origin') && searchParams.get('destination')) {
      performSearch();
    } else {
      setIsLoading(false);
      setError('缺少搜索参数');
    }
  }, [searchParams, showAlert, isInitialized, authLoading]);

  if (isLoading || authLoading || !isInitialized) {
    return (
      <SearchLoadingComponent
        currentStep={authLoading || !isInitialized ? 0 : searchStep}
        isAuthLoading={authLoading}
        isInitialized={isInitialized}
      />
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-[#F5F5F7] flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="w-16 h-16 mx-auto mb-4 bg-[#FF3B30] rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h2 className="text-[20px] font-semibold text-[#1D1D1F] mb-2">搜索失败</h2>
          <p className="text-[#86868B] mb-4">{error}</p>
          <button
            onClick={() => router.push('/search')}
            className="bg-[#0071E3] text-white px-6 py-2 rounded-full hover:bg-[#0056B3] transition-colors"
          >
            返回搜索
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F5F5F7]">
      {/* 顶部导航 - 移动端优化 */}
      <nav className="bg-white/90 backdrop-blur-md sticky top-0 z-50 border-b border-[#E5E5EA] safe-top">
        <div className="max-w-6xl mx-auto px-3 sm:px-4 py-2 sm:py-3 flex justify-between items-center">
          <div className="flex items-center space-x-2 sm:space-x-4 min-w-0 flex-1">
            <button
              onClick={() => router.push('/search')}
              className="flex items-center text-[#1D1D1F] hover:text-[#0071E3] transition-colors p-1 sm:p-0 min-h-[44px]"
            >
              <svg className="w-5 h-5 mr-1 sm:mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span className="text-[12px] sm:text-[14px] font-medium hidden xs:inline">返回搜索</span>
            </button>
            <div className="h-4 w-px bg-[#E5E5EA] hidden sm:block"></div>
            <h1 className="text-[16px] sm:text-[21px] font-medium text-[#1D1D1F] truncate">
              <span className="hidden sm:inline">航班搜索结果</span>
              <span className="sm:hidden">搜索结果</span>
            </h1>
          </div>

          {/* 搜索状态指示器 */}
          <div className="flex items-center space-x-2 sm:space-x-3 flex-shrink-0">
            {totalFlights > 0 && (
              <div className="bg-[#34C759]/10 text-[#34C759] px-2 sm:px-3 py-1 sm:py-1.5 rounded-full text-[11px] sm:text-[14px] font-medium">
                <span className="hidden xs:inline">找到 </span>{totalFlights}<span className="hidden sm:inline"> 个航班</span>
              </div>
            )}
          </div>
        </div>
      </nav>

      <div className="max-w-6xl mx-auto px-3 sm:px-4 py-4 sm:py-6">
        {/* 搜索结果头部 - 移动端优化 */}
        <div className="mb-4 sm:mb-6">
          <div className="bg-white rounded-2xl shadow-sm p-4 sm:p-6 border border-[#E8E8ED]">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
              <div className="min-w-0 flex-1">
                <h1 className="text-[18px] sm:text-[24px] font-semibold text-[#1D1D1F] mb-1 sm:mb-2 truncate">
                  {searchParams.get('origin')} → {searchParams.get('destination')}
                </h1>
                <p className="text-[#86868B] text-[12px] sm:text-[14px]">
                  {searchParams.get('departureDate')} · 单程 · {searchParams.get('cabinClass') === 'BUSINESS' ? '商务舱' : '经济舱'}
                </p>
              </div>
              <div className="text-left sm:text-right flex-shrink-0">
                <p className="text-[#0071E3] text-[16px] sm:text-[18px] font-semibold">
                  找到 {totalFlights} 个航班
                </p>
                {searchResults && (
                  <p className="text-[#86868B] text-[10px] sm:text-[12px] mt-1">
                    搜索ID: {searchResults.search_id.substring(0, 8)}...
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* 直飞航班 */}
        {searchResults && searchResults.direct_flights && searchResults.direct_flights.length > 0 && (
          <div className="mb-8">
            <h2 className="text-[20px] font-semibold text-[#1D1D1F] mb-4 flex items-center">
              <div className="w-6 h-6 bg-[#34C759] rounded-full flex items-center justify-center mr-3">
                <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              直飞航班 ({searchResults.direct_flights?.length || 0})
            </h2>
            <div className="space-y-4">
              {(searchResults.direct_flights || []).map((flight, index) => (
                <FlightCard
                  key={`direct-${flight.id}-${index}`}
                  flight={flight}
                  index={index}
                />
              ))}
            </div>
          </div>
        )}



        {/* 组合优惠航班 */}
        {searchResults && searchResults.hidden_city_flights && searchResults.hidden_city_flights.length > 0 && (
          <div className="mb-8">
            <h2 className="text-[20px] font-semibold text-[#1D1D1F] mb-4 flex items-center">
              <div className="w-6 h-6 bg-[#8B5CF6] rounded-full flex items-center justify-center mr-3">
                <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4l3 9h9l-7 5 3 9-8-6-8 6 3-9-7-5h9l3-9z" />
                </svg>
              </div>
              组合优惠 ({searchResults.hidden_city_flights?.length || 0})
              <div className="ml-3 text-[12px] bg-[#8B5CF6]/10 text-[#8B5CF6] px-2 py-1 rounded-full">
                特价推荐
              </div>
            </h2>
            <div className="space-y-4">
              {(searchResults.hidden_city_flights || []).map((flight, index) => (
                <FlightCard
                  key={`hidden-${flight.id}-${index}`}
                  flight={flight}
                  index={index}
                />
              ))}
            </div>
          </div>
        )}

        {/* 免责声明 */}
        {searchResults && searchResults.disclaimers && (
          searchResults.disclaimers.show_direct_flight_disclaimer_key ||
          searchResults.disclaimers.show_hidden_city_disclaimer_key
        ) && (
          <div className="mb-8">
            <div className="bg-[#FFF3CD] border border-[#FFEAA7] rounded-2xl p-4">
              <h3 className="text-[16px] font-semibold text-[#856404] mb-2 flex items-center">
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
                重要提示
              </h3>
              <ul className="text-[14px] text-[#856404] space-y-1">
                {searchResults.disclaimers.show_direct_flight_disclaimer_key && (
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>直飞航班价格可能会有变动，请以实际预订页面为准</span>
                  </li>
                )}
                {searchResults.disclaimers.show_hidden_city_disclaimer_key && (
                  <li className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>组合优惠航班可能涉及特殊预订条件，请仔细阅读预订条款</span>
                  </li>
                )}
              </ul>
            </div>
          </div>
        )}

        {/* 无结果提示 */}
        {totalFlights === 0 && !isLoading && (
          <div className="text-center py-12">
            <div className="w-16 h-16 mx-auto mb-4 bg-[#F5F5F7] rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-[#86868B]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <h3 className="text-[20px] font-semibold text-[#1D1D1F] mb-2">未找到航班</h3>
            <p className="text-[#86868B] mb-4">请尝试调整搜索条件或选择其他日期</p>
            <button
              onClick={() => router.push('/search')}
              className="bg-[#0071E3] text-white px-6 py-2 rounded-full hover:bg-[#0056B3] transition-colors"
            >
              修改搜索条件
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// 使用Suspense包装组件以处理useSearchParams
const FlightSearchResultsPage: React.FC = () => {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-[#F5F5F7] flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-[#0071E3] border-t-transparent mx-auto mb-4"></div>
          <p className="text-[#86868B] text-[16px]">加载中...</p>
        </div>
      </div>
    }>
      <FlightSearchResults />
    </Suspense>
  );
};

export default FlightSearchResultsPage;
