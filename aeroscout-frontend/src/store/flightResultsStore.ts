import { create } from 'zustand';
import { ApiFlightItinerary } from '@/lib/apiService';

export const POLLING_TIMEOUT_DURATION = 2 * 60 * 1000; // 2 minutes
export const MAX_CONSECUTIVE_FAILURES = 5;

export type SearchStatus = 'idle' | 'loading' | 'success' | 'error' | 'stopped'; // 添加 'stopped' 状态
export type PollingStoppedReason = 'timeout' | 'max_failures';

// 定义更具体的类型
export interface AirportInfo {
  code: string; // IATA code, e.g., "PVG"
  name: string; // e.g., "Shanghai Pudong International Airport"
  cityName: string; // e.g., "Shanghai" - mapped from apiService.ApiAirportInfo.city_name
  cityCode?: string;
  countryName?: string;
  countryCode?: string;
}

export interface AirlineInfo {
  code: string; // IATA code
  name: string;
  logoUrl?: string; // mapped from apiService.ApiAirlineInfo.logo_url
}

export interface FlightSegment {
  id?: string;
  airlineCode: string; // mapped from apiService.ApiFlightSegment.airline_code
  airlineName: string; // mapped from apiService.ApiFlightSegment.airline_name
  airlineLogoUrl?: string; // 航空公司 Logo 的 URL
  flightNumber: string; // mapped from apiService.ApiFlightSegment.flight_number
  departureAirportCode: string; // mapped from apiService.ApiFlightSegment.departure_airport_code
  departureAirportName: string; // mapped from apiService.ApiFlightSegment.departure_airport_name
  departureAirportFull?: string; // 出发机场的详细名称/信息
  departureCityName: string; // mapped from apiService.ApiFlightSegment.departure_city_name
  departureTime: string; // mapped from apiService.ApiFlightSegment.departure_time
  departureTerminal?: string; // Added: e.g., "T2" - assumed from apiSegment.departure_terminal
  arrivalAirportCode: string; // mapped from apiService.ApiFlightSegment.arrival_airport_code
  arrivalAirportName: string; // mapped from apiService.ApiFlightSegment.arrival_airport_name
  arrivalAirportFull?: string; // 到达机场的详细名称/信息
  arrivalCityName: string; // mapped from apiService.ApiFlightSegment.arrival_city_name
  arrivalTime: string; // mapped from apiService.ApiFlightSegment.arrival_time
  arrivalTerminal?: string; // Added: e.g., "T1" - assumed from apiSegment.arrival_terminal
  durationMinutes: number; // mapped from apiService.ApiFlightSegment.duration_minutes
  cabinClass?: string; // mapped from apiService.ApiFlightSegment.cabin_class
  equipment?: string; // 机型信息
  isLayover?: boolean; // 标记此航段是否为中转停留的一部分
  layoverDuration?: string; // 如果是中转，中转时长
  nextSegmentRequiresAirportChange?: boolean; // 如果是中转，下一段是否需要更换机场
  isBaggageRecheck?: boolean; // 如果是中转，是否需要重新托运行李
  operatingCarrierCode?: string; // 实际执飞航司代码
  operatingCarrierName?: string; // 实际执飞航司名称
}

export interface TransferInfo {
  city?: string; // City where the transfer occurs
  durationMinutes: number; // Duration of the layover in minutes
  isDifferentAirport: boolean; // True if transfer involves changing airports
  airportChangeDetail?: {
    fromAirportCode: string;
    toAirportCode: string;
  };
  layoverTime?: string; // Formatted layover time e.g., "2h 30m"
  isBaggageRecheck?: boolean; // Whether baggage needs to be rechecked during this transfer
  isAirlineChange?: boolean; // Whether the airline changes during this transfer
  fromAirline?: {
    code: string;
    name: string;
  };
  toAirline?: {
    code: string;
    name: string;
  };
}

export interface FlightItinerary {
  id: string; // Unique ID for the itinerary
  segments: FlightSegment[];
  transfers?: TransferInfo[]; // Added: Detailed transfer information
  totalDurationMinutes: number; // mapped from apiService.ApiFlightItinerary.total_duration_minutes
  totalTravelTime?: string; // 整个行程的总旅行时间（包括中转）
  price: {
    amount: number;
    currency: string;
  };
  airlines?: Array<{ // 参与该行程的所有航司信息
    code: string;
    name: string;
    logoUrl?: string;
  }>;
  isDirectFlight: boolean; // mapped from apiService.ApiFlightItinerary.is_direct_flight
  bookingToken?: string; // mapped from apiService.ApiFlightItinerary.booking_token
  deepLink?: string; // mapped from apiService.ApiFlightItinerary.deep_link
  // Added for more itinerary details
  numberOfStops?: number;
  isProbeSuggestion?: boolean; // 是否为通过"中国中转城市探测"逻辑找到的建议
  probeHub?: string; // 如果是探测建议，相关的枢纽城市代码或名称
  probeDisclaimer?: string; // Specific disclaimer for this probe suggestion
  isComboDeal?: boolean; // Though often determined by array, map if API provides
  providerName?: string; // e.g., "Kiwi.com"
  tags?: string[]; // For any other relevant tags from the API
  // 添加自行中转和隐藏城市标志
  isSelfTransfer?: boolean; // 是否为自行中转航班
  isHiddenCity?: boolean; // 是否为隐藏城市航班
  isThrowawayDeal?: boolean; // 是否为甩尾票
  isTrueHiddenCity?: boolean; // 是否为真正的隐藏城市航班
  hiddenDestination?: { // 隐藏目的地信息（用于甩尾票）
    code: string; // 机场代码
    name: string; // 机场名称
    cityName: string; // 城市名称
    countryName?: string; // 国家名称
  };
  // Optional: store the raw API data for debugging or advanced use cases
  // rawApiItinerary?: ApiFlightItinerary;
}

export interface FlightData { // API 响应中 'result' 字段的结构 (TaskResultData in apiService)
  directFlights?: ApiFlightItinerary[]; // Corresponds to "direct_flights" in TaskResultData
  comboDeals?: ApiFlightItinerary[]; // Corresponds to "combo_deals" in TaskResultData
  disclaimers?: string[];
  // 🔧 添加后端实际返回的字段名支持
  direct_flights?: ApiFlightItinerary[]; // 后端实际返回的字段名
  hidden_city_flights?: ApiFlightItinerary[]; // 后端实际返回的字段名
  // 根据 API_Documentation.md 或实际 API 响应，可能还有 search_parameters, context 等字段
}

export interface ErrorInfo {
  message: string;
  type?: 'network' | 'server' | 'client' | 'timeout' | string;
  details?: Record<string, unknown>; // 使用Record<string, unknown>代替any，更安全
}

interface FlightResultsState {
  taskId: string | null;
  searchStatus: SearchStatus;
  directFlights: FlightItinerary[];
  comboDeals: FlightItinerary[];
  disclaimers: string[];
  error: string | ErrorInfo | null;
  // 新增状态用于超时和连续失败处理
  pollingTimeoutId: NodeJS.Timeout | null;
  consecutiveFailures: number;
  pollingStoppedReason: PollingStoppedReason | null;
  lastActivityTime: number | null;

  // Actions
  setSearchInitiated: (taskId: string) => void;
  setSearchPolling: () => void; // 用于任务状态 PENDING/STARTED 时，维持 loading 状态
  setSearchSuccess: (data: FlightData, isFinalResult: boolean) => void; // 添加 isFinalResult 参数
  setSearchError: (errorMessage: string | ErrorInfo) => void;
  resetFlightSearch: () => void;
  // 新增 action 用于处理轮询停止
  stopPolling: (reason: PollingStoppedReason) => void;
  // 新增立即设置loading状态的action
  setSearchLoading: () => void;
}

const initialState: Omit<FlightResultsState, 'setSearchInitiated' | 'setSearchPolling' | 'setSearchSuccess' | 'setSearchError' | 'resetFlightSearch' | 'stopPolling' | 'setSearchLoading'> = {
  taskId: null,
  searchStatus: 'idle',
  directFlights: [],
  comboDeals: [],
  disclaimers: [],
  error: null,
  // 初始化新增状态
  pollingTimeoutId: null,
  consecutiveFailures: 0,
  pollingStoppedReason: null,
  lastActivityTime: null,
};

export const useFlightResultsStore = create<FlightResultsState>((set, get) => ({
  ...initialState,

  setSearchLoading: () => {
    console.log('🔄 [DEBUG] 立即设置loading状态');
    set({
      searchStatus: 'loading',
      error: null,
      lastActivityTime: Date.now(),
    });
  },

  setSearchInitiated: (taskId) => {
    const { pollingTimeoutId } = get();
    if (pollingTimeoutId) {
      clearTimeout(pollingTimeoutId);
    }
    const newTimeoutId = setTimeout(() => get().stopPolling('timeout'), POLLING_TIMEOUT_DURATION);

    set({
      ...initialState, // 重置结果和错误，开始新的搜索
      taskId,
      searchStatus: 'loading',
      lastActivityTime: Date.now(),
      pollingTimeoutId: newTimeoutId,
      consecutiveFailures: 0,
      pollingStoppedReason: null,
    });
  },

  setSearchPolling: () =>
    set((state) => {
      if (state.pollingStoppedReason) { // 如果已停止，则不改变状态
        return {};
      }
      // 仅当当前状态为 'loading' 时，才需要显式设置为 'loading'
      // 如果已经是 'success' 或 'error'，则不应覆盖
      if (state.searchStatus === 'loading') {
        return { searchStatus: 'loading', lastActivityTime: Date.now() };
      }
      // 如果是从 'idle' 状态因为某种原因调用（理论上不应该），也设置为 'loading'
      if (state.searchStatus === 'idle' && state.taskId) {
         return { searchStatus: 'loading', lastActivityTime: Date.now() };
      }
      return {}; // 其他状态下不改变
    }),

  setSearchSuccess: (data: FlightData, isFinalResult: boolean) => {
    console.log('🔍 === setSearchSuccess 调试信息 ===');
    console.log('🔍 接收到的原始数据:', data);
    console.log('🔍 数据类型:', typeof data);
    console.log('🔍 是否为最终结果:', isFinalResult);
    console.log('🔍 directFlights 字段:', data.directFlights);
    console.log('🔍 comboDeals 字段:', data.comboDeals);
    console.log('🔍 directFlights 长度:', data.directFlights?.length);
    console.log('🔍 comboDeals 长度:', data.comboDeals?.length);
    
    // 🔍 添加详细的API响应数据结构分析
    console.log('🔍 === API响应数据结构详细分析 ===');
    console.log('🔍 完整的data对象键名:', Object.keys(data));
    
    // 检查是否有其他可能的字段名
    const possibleFlightFields = ['directFlights', 'direct_flights', 'comboDeals', 'combo_deals', 'hiddenCityFlights', 'hidden_city_flights'];
    possibleFlightFields.forEach(field => {
      const fieldValue = (data as Record<string, unknown>)[field];
      if (fieldValue) {
        console.log(`🔍 发现字段 ${field}:`, fieldValue);
        console.log(`🔍 ${field} 长度:`, Array.isArray(fieldValue) ? fieldValue.length : '不是数组');
        
        // 如果是数组且有数据，显示第一个元素的结构
        if (Array.isArray(fieldValue) && fieldValue.length > 0) {
          const firstItem = fieldValue[0] as Record<string, unknown>;
          console.log(`🔍 ${field} 第一个元素的键名:`, Object.keys(firstItem));
          console.log(`🔍 ${field} 第一个元素完整数据:`, firstItem);
          
          // 检查航段数据结构
          const possibleSegmentFields = ['segments', 'outbound_segments', 'inbound_segments', 'sector', 'sectorSegments'];
          possibleSegmentFields.forEach(segField => {
            const segmentValue = firstItem[segField];
            if (segmentValue) {
              console.log(`🔍 ${field} 中发现航段字段 ${segField}:`, segmentValue);
              if (Array.isArray(segmentValue) && segmentValue.length > 0) {
                console.log(`🔍 ${segField} 第一个航段数据:`, segmentValue[0]);
              }
            }
          });
        }
      }
    });
    
    const { pollingTimeoutId } = get();
    if (pollingTimeoutId) {
      clearTimeout(pollingTimeoutId);
    }

    let newTimeoutId: NodeJS.Timeout | null = null;
    if (!isFinalResult) {
      newTimeoutId = setTimeout(() => get().stopPolling('timeout'), POLLING_TIMEOUT_DURATION);
    }

    // 🔧 修复数据映射逻辑，支持后端实际返回的字段名
    console.log('开始映射 API 数据到 Store 格式...');
    
    // 支持后端实际返回的字段名
    const directFlights = data.directFlights || data.direct_flights || [];
    const hiddenCityFlights = data.comboDeals || data.hidden_city_flights || [];
    
    console.log('🔧 使用的数据源:');
    console.log('- directFlights 来源:', data.directFlights ? 'data.directFlights' : 'data.direct_flights');
    console.log('- hiddenCityFlights 来源:', data.comboDeals ? 'data.comboDeals' : 'data.hidden_city_flights');
    console.log('- directFlights 数量:', directFlights.length);
    console.log('- hiddenCityFlights 数量:', hiddenCityFlights.length);
    
    const mappedDirectFlights = directFlights.map(mapApiItineraryToStoreItinerary);
    const mappedComboDeals = hiddenCityFlights.map(mapApiItineraryToStoreItinerary);
    
    console.log('映射完成:');
    console.log('- 直飞航班映射结果数量:', mappedDirectFlights.length);
    console.log('- 隐藏城市航班映射结果数量:', mappedComboDeals.length);
    
    // 后端已经处理去重，前端直接使用映射结果
    console.log('使用后端去重结果:');
    console.log('- 直飞航班数量:', mappedDirectFlights.length);
    console.log('- 组合航班数量:', mappedComboDeals.length);
    
    // 如果有映射结果，显示第一个的详细信息
    if (mappedDirectFlights.length > 0) {
      console.log('第一个映射后的直飞航班:', mappedDirectFlights[0]);
    }
    if (mappedComboDeals.length > 0) {
      console.log('第一个映射后的组合航班:', mappedComboDeals[0]);
    }

    set({
      directFlights: mappedDirectFlights,
      comboDeals: mappedComboDeals,
      disclaimers: data.disclaimers || [],
      searchStatus: isFinalResult ? 'success' : 'loading', // 如果不是最终结果，保持loading以继续轮询
      error: null, // 清除之前的错误
      consecutiveFailures: 0, // 重置连续失败次数
      lastActivityTime: Date.now(),
      pollingTimeoutId: newTimeoutId,
      pollingStoppedReason: isFinalResult ? get().pollingStoppedReason : null, // 如果是最终结果，保留之前的停止原因（如果有），否则重置
    });
    
    console.log('Store 状态更新完成');
    console.log('当前 Store 状态:', get());
  },

  setSearchError: (error: string | ErrorInfo) => {
    const { pollingTimeoutId, consecutiveFailures: prevFailures } = get();
    if (pollingTimeoutId) {
      clearTimeout(pollingTimeoutId);
    }
    const currentFailures = prevFailures + 1;

    if (currentFailures >= MAX_CONSECUTIVE_FAILURES) {
      get().stopPolling('max_failures');
      set({
        searchStatus: 'stopped', // 更新状态为 stopped
        error: error,
        consecutiveFailures: currentFailures,
        pollingTimeoutId: null,
        lastActivityTime: Date.now(),
      });
    } else {
      // 如果未达到最大失败次数，仍然设置超时以便下次轮询
      const newTimeoutId = setTimeout(() => get().stopPolling('timeout'), POLLING_TIMEOUT_DURATION);
      set({
        searchStatus: 'error', // 或 'loading' 如果希望错误后继续尝试轮询直到超时或最大失败
        error: error,
        consecutiveFailures: currentFailures,
        pollingTimeoutId: newTimeoutId, // 重新设置超时
        lastActivityTime: Date.now(),
      });
    }
  },

  stopPolling: (reason: PollingStoppedReason) => {
    const { pollingTimeoutId } = get();
    if (pollingTimeoutId) {
      clearTimeout(pollingTimeoutId);
    }
    let errorMessage: ErrorInfo | string = '搜索已停止。';
    if (reason === 'timeout') {
        errorMessage = { type: 'timeout', message: '搜索超时，请稍后重试或调整搜索条件。' };
    } else if (reason === 'max_failures') {
        errorMessage = { type: 'max_failures', message: '多次尝试连接失败，请检查您的网络连接或稍后重试。' };
    }

    set({
      searchStatus: 'stopped',
      pollingStoppedReason: reason,
      pollingTimeoutId: null,
      error: errorMessage, // 设置相应的错误信息
      lastActivityTime: Date.now(),
    });
  },

  resetFlightSearch: () => {
    const { pollingTimeoutId } = get();
    if (pollingTimeoutId) {
      clearTimeout(pollingTimeoutId);
    }
    set(initialState);
  },
}));


// 以上类型定义已移至文件顶部并取消注释

// 映射函数：将 API 响应类型转换为前端状态类型
// 导出以便测试
export const mapApiItineraryToStoreItinerary = (apiItinerary: Record<string, unknown>): FlightItinerary => {
  console.log('=== mapApiItineraryToStoreItinerary 调试 ===');
  console.log('输入的 apiItinerary:', apiItinerary);
  
  // === 价格调试信息 ===
  console.log('=== 价格字段调试 ===');
  console.log('price:', apiItinerary.price, typeof apiItinerary.price);
  console.log('currency:', apiItinerary.currency, typeof apiItinerary.currency);
  console.log('原始price字段（deprecated）:', apiItinerary.price_eur);
  
  // 🔧 处理后端实际返回的数据结构
  const segments = (apiItinerary.segments as Record<string, unknown>[]) ||
                   (apiItinerary.outbound_segments as Record<string, unknown>[]) || [];
  console.log('🔧 提取的 segments:', segments);
  console.log('🔧 segments 来源:', apiItinerary.segments ? 'apiItinerary.segments' : 'apiItinerary.outbound_segments');
  
  // 计算总旅行时间 - 支持多种字段名
  const totalDurationMinutes = (apiItinerary.totalDurationMinutes as number) ||
                               (apiItinerary.total_duration_minutes as number) ||
                               (apiItinerary.duration_minutes as number) ||
                               (apiItinerary.duration as number) || 0;
  
  // 添加飞行时间调试信息
  console.log('=== 飞行时间字段调试 ===');
  console.log('totalDurationMinutes:', apiItinerary.totalDurationMinutes, typeof apiItinerary.totalDurationMinutes);
  console.log('total_duration_minutes:', apiItinerary.total_duration_minutes, typeof apiItinerary.total_duration_minutes);
  console.log('duration_minutes:', apiItinerary.duration_minutes, typeof apiItinerary.duration_minutes);
  console.log('duration:', apiItinerary.duration, typeof apiItinerary.duration);
  console.log('最终使用的totalDurationMinutes:', totalDurationMinutes);
  
  const totalTravelTime = (() => {
    const hours = Math.floor(totalDurationMinutes / 60);
    const minutes = totalDurationMinutes % 60;
    const timeStr = `${hours}h ${minutes > 0 ? `${minutes}m` : ''}`.trim();
    console.log('格式化后的飞行时间:', timeStr);
    return timeStr;
  })();

  // 确定是否为直飞航班
  const isDirectFlight = segments.length === 1;

  // 计算中转次数
  const numberOfStops = segments.length > 0 ? segments.length - 1 : 0;
  
  // 🔍 添加调试日志来诊断中转判断问题
  console.log('🔍 数据映射器中转诊断 - 航班ID:', apiItinerary.id);
  console.log('🔍 原始segments数量:', segments.length);
  console.log('🔍 计算的isDirectFlight:', isDirectFlight);
  console.log('🔍 计算的numberOfStops:', numberOfStops);
  console.log('🔍 原始segments详情:', segments.map((seg, idx) => ({
    index: idx,
    from: `${seg.departure_city || seg.departureCityName}(${seg.departure_airport || seg.departureAirportCode})`,
    to: `${seg.arrival_city || seg.arrivalCityName}(${seg.arrival_airport || seg.arrivalAirportCode})`,
    flight: seg.flight_number || seg.flightNumber
  })));

  // 映射航段信息
  const mappedSegments = segments.map((segment: Record<string, unknown>, index: number) => {
    console.log(`映射航段 ${index + 1}:`, segment);
    
    // 🔧 处理后端Kiwi API字段名到前端字段名的映射
    const carrier = segment.carrier as Record<string, unknown> || {};
    const origin = segment.origin as Record<string, unknown> || {};
    const destination = segment.destination as Record<string, unknown> || {};
    const departure = segment.departure as Record<string, unknown> || {};
    const arrival = segment.arrival as Record<string, unknown> || {};
    
    const mappedSegment = {
      id: (segment.id as string) || `segment-${index}`,
      // 🔧 支持Kiwi API的carrier结构
      airlineCode: (carrier.code as string) || (segment.carrier_code as string) || (segment.airlineCode as string) || '',
      airlineName: (carrier.name as string) || (segment.carrier_name as string) || (segment.airlineName as string) || '',
      flightNumber: (segment.flight_number as string) || (segment.flightNumber as string) || '',
      // 🔧 支持Kiwi API的origin/destination结构
      departureAirportCode: (origin.code as string) || (segment.departure_airport as string) || (segment.departureAirportCode as string) || '',
      departureAirportName: (origin.name as string) || (segment.departure_airport_name as string) || (segment.departureAirportName as string) || '',
      departureCityName: (origin.city as string) || (segment.departure_city as string) || (segment.departureCityName as string) || '',
      departureTime: (departure.local_time as string) || (segment.departure_time as string) || (segment.departureTime as string) || '',
      arrivalAirportCode: (destination.code as string) || (segment.arrival_airport as string) || (segment.arrivalAirportCode as string) || '',
      arrivalAirportName: (destination.name as string) || (segment.arrival_airport_name as string) || (segment.arrivalAirportName as string) || '',
      arrivalCityName: (destination.city as string) || (segment.arrival_city as string) || (segment.arrivalCityName as string) || '',
      arrivalTime: (arrival.local_time as string) || (segment.arrival_time as string) || (segment.arrivalTime as string) || '',
      durationMinutes: (segment.duration_minutes as number) || (segment.durationMinutes as number) || 0,
      cabinClass: (segment.cabin_class as string) || (segment.cabinClass as string) || '',
      airlineLogoUrl: (segment.airlineLogoUrl as string) || ((carrier.code as string) || (segment.carrier_code as string) || (segment.airlineCode as string)
        ? `https://daisycon.io/images/airline/?width=300&height=150&iata=${(carrier.code as string) || (segment.carrier_code as string) || (segment.airlineCode as string)}`
        : undefined),
      departureAirportFull: (origin.name as string) || (segment.departure_airport_name as string) || (segment.departureAirportName as string)
        ? `${(origin.name as string) || (segment.departure_airport_name as string) || (segment.departureAirportName as string)} (${(origin.code as string) || (segment.departure_airport as string) || (segment.departureAirportCode as string)})`
        : (origin.code as string) || (segment.departure_airport as string) || (segment.departureAirportCode as string) || '',
      arrivalAirportFull: (destination.name as string) || (segment.arrival_airport_name as string) || (segment.arrivalAirportName as string)
        ? `${(destination.name as string) || (segment.arrival_airport_name as string) || (segment.arrivalAirportName as string)} (${(destination.code as string) || (segment.arrival_airport as string) || (segment.arrivalAirportCode as string)})`
        : (destination.code as string) || (segment.arrival_airport as string) || (segment.arrivalAirportCode as string) || '',
      equipment: (segment.aircraft as string) || (segment.equipment as string),
      isLayover: index > 0,
      operatingCarrierCode: (segment.operating_carrier_code as string) || (segment.operatingCarrierCode as string),
      operatingCarrierName: (segment.operating_carrier_name as string) || (segment.operatingCarrierName as string),
    };
    
    console.log(`映射后的航段 ${index + 1}:`, mappedSegment);
    return mappedSegment;
  });

  // 构建中转信息
  const transfers = segments.length > 1
    ? segments.slice(0, -1).map((currentSegment: Record<string, unknown>, index: number) => {
        const nextSegment = segments[index + 1];

        // 🔧 支持Kiwi API的嵌套结构
        const currentArrivalData = (currentSegment.arrival as Record<string, unknown>) || {};
        const nextDepartureData = (nextSegment.departure as Record<string, unknown>) || {};
        const currentDestination = (currentSegment.destination as Record<string, unknown>) || {};
        const nextOrigin = (nextSegment.origin as Record<string, unknown>) || {};
        const currentCarrierData = (currentSegment.carrier as Record<string, unknown>) || {};
        const nextCarrierData = (nextSegment.carrier as Record<string, unknown>) || {};
        
        // 计算中转时长
        const currentArrivalTime = (currentArrivalData.local_time as string) || (currentSegment.arrival_time as string) || (currentSegment.arrivalTime as string);
        const nextDepartureTime = (nextDepartureData.local_time as string) || (nextSegment.departure_time as string) || (nextSegment.departureTime as string);
        const currentArrival = new Date(currentArrivalTime).getTime();
        const nextDeparture = new Date(nextDepartureTime).getTime();
        const durationMinutes = Math.round((nextDeparture - currentArrival) / (1000 * 60));

        // 格式化中转时间
        const hours = Math.floor(durationMinutes / 60);
        const minutes = durationMinutes % 60;
        const layoverTime = `${hours > 0 ? `${hours}h ` : ''}${minutes > 0 ? `${minutes}m` : (hours === 0 ? '0m' : '')}`.trim();

        // 检查是否需要换机场
        const currentArrivalAirport = (currentDestination.code as string) || (currentSegment.arrival_airport as string) || (currentSegment.arrivalAirportCode as string);
        const nextDepartureAirport = (nextOrigin.code as string) || (nextSegment.departure_airport as string) || (nextSegment.departureAirportCode as string);
        const isDifferentAirport = currentArrivalAirport !== nextDepartureAirport;
        
        let airportChangeDetail;
        if (isDifferentAirport) {
          airportChangeDetail = {
            fromAirportCode: currentArrivalAirport,
            toAirportCode: nextDepartureAirport,
          };
        }

        // 检查是否更换航空公司
        const currentCarrier = (currentCarrierData.code as string) || (currentSegment.carrier_code as string) || (currentSegment.airlineCode as string);
        const nextCarrier = (nextCarrierData.code as string) || (nextSegment.carrier_code as string) || (nextSegment.airlineCode as string);
        const isAirlineChange = currentCarrier !== nextCarrier;

        return {
          city: (currentDestination.city as string) || (currentSegment.arrival_city as string) || (currentSegment.arrivalCityName as string) || '未知城市',
          durationMinutes,
          isDifferentAirport,
          airportChangeDetail,
          layoverTime,
          isBaggageRecheck: isDifferentAirport, // 简化逻辑：不同机场需要重新托运
          isAirlineChange,
          fromAirline: {
            code: currentCarrier || '',
            name: (currentCarrierData.name as string) || (currentSegment.carrier_name as string) || (currentSegment.airlineName as string) || '',
          },
          toAirline: {
            code: nextCarrier || '',
            name: (nextCarrierData.name as string) || (nextSegment.carrier_name as string) || (nextSegment.airlineName as string) || '',
          },
        };
      })
    : undefined;

  // 🔧 构建所有参与航司信息，支持Kiwi API的carrier结构
  const airlines = segments.reduce((acc: Array<{ code: string; name: string; logoUrl?: string }>, segment: Record<string, unknown>) => {
    const carrier = segment.carrier as Record<string, unknown> || {};
    const carrierCode = (carrier.code as string) || (segment.carrier_code as string) || (segment.airlineCode as string);
    const carrierName = (carrier.name as string) || (segment.carrier_name as string) || (segment.airlineName as string);
    
    if (carrierCode && !acc.find(a => a.code === carrierCode)) {
      acc.push({
        code: carrierCode,
        name: carrierName || '',
        logoUrl: `https://daisycon.io/images/airline/?width=300&height=150&iata=${carrierCode}`,
      });
    }
    return acc;
  }, []);

  // 查找隐藏目的地信息（优先从顶层字段提取，然后从segments中提取）
  let hiddenDestination: FlightItinerary['hiddenDestination'];
  
  // 首先检查顶层的hiddenDestination字段（V2 API适配器传入的）
  if (apiItinerary.hiddenDestination) {
    const hiddenDest = apiItinerary.hiddenDestination as Record<string, unknown>;
    hiddenDestination = {
      code: (hiddenDest.code as string) || '',
      name: (hiddenDest.name as string) || '',
      cityName: (hiddenDest.cityName as string) || (hiddenDest.city_name as string) ||
                ((hiddenDest.city as Record<string, unknown>)?.name as string) || '',
      countryName: (hiddenDest.countryName as string) || (hiddenDest.country_name as string) ||
                   ((hiddenDest.country as Record<string, unknown>)?.name as string) || '',
    };
    console.log('🎯 从顶层字段找到隐藏目的地:', hiddenDestination);
  } else {
    // 如果顶层没有，再从segments中查找（兼容旧版本）
    for (const segment of segments) {
      if (segment.hidden_destination || segment.hiddenDestination) {
        const hiddenDest = segment.hidden_destination || segment.hiddenDestination;
        if (typeof hiddenDest === 'object' && hiddenDest !== null) {
          const dest = hiddenDest as Record<string, unknown>;
          hiddenDestination = {
            code: (dest.code as string) || '',
            name: (dest.name as string) || '',
            cityName: (dest.city_name as string) || (dest.cityName as string) ||
                      ((dest.city as Record<string, unknown>)?.name as string) || '',
            countryName: (dest.country_name as string) || (dest.countryName as string) ||
                         ((dest.country as Record<string, unknown>)?.name as string) || '',
          };
          console.log('🎯 从segments中找到隐藏目的地:', hiddenDestination);
          break; // 找到第一个隐藏目的地就停止
        }
      }
    }
  }

  // 🔧 构建最终的航班行程对象，正确处理隐藏城市航班标记
  const isHiddenCityFlight = (apiItinerary.is_hidden_city as boolean) ||
                             (apiItinerary.flight_type as string) === 'hidden_city' ||
                             false;
  
  // 🔧 如果是隐藏城市航班，重新计算直飞状态
  // 隐藏城市航班虽然只有一个航段，但实际上是中转航班（在中转城市下机）
  const actualIsDirectFlight = isHiddenCityFlight ? false : isDirectFlight;
  const actualNumberOfStops = isHiddenCityFlight ? 1 : numberOfStops; // 隐藏城市航班至少有1次中转
  
  console.log('🔧 隐藏城市航班处理:');
  console.log('- 原始isDirectFlight:', isDirectFlight);
  console.log('- isHiddenCityFlight:', isHiddenCityFlight);
  console.log('- 修正后的actualIsDirectFlight:', actualIsDirectFlight);
  console.log('- 原始numberOfStops:', numberOfStops);
  console.log('- 修正后的actualNumberOfStops:', actualNumberOfStops);
  
  const result: FlightItinerary = {
    id: (apiItinerary.id as string) || '',
    segments: mappedSegments,
    transfers,
    totalDurationMinutes,
    totalTravelTime,
    price: {
      amount: (() => {
        const priceValue = apiItinerary.price;
        if (typeof priceValue === 'number') {
          return priceValue;
        }
        if (typeof priceValue === 'object' && priceValue !== null) {
          const priceObj = priceValue as Record<string, unknown>;
          const amount = priceObj.amount;
          if (typeof amount === 'string') {
            return parseFloat(amount) || 0;
          }
          if (typeof amount === 'number') {
            return amount;
          }
        }
        return 0;
      })(),
      currency: (apiItinerary.currency as string) || 'CNY',
    },
    airlines,
    isDirectFlight: actualIsDirectFlight, // 🔧 使用修正后的直飞状态
    bookingToken: (apiItinerary.booking_token as string),
    deepLink: (apiItinerary.deep_link as string),
    numberOfStops: actualNumberOfStops, // 🔧 使用修正后的中转次数
    isProbeSuggestion: (apiItinerary.is_probe_suggestion as boolean) || false,
    probeHub: (apiItinerary.probe_hub as string),
    probeDisclaimer: (apiItinerary.probe_disclaimer as string),
    isComboDeal: false, // 根据数组位置确定
    providerName: 'Kiwi.com',
    isSelfTransfer: (apiItinerary.is_self_transfer as boolean) || false,
    isHiddenCity: isHiddenCityFlight, // 🔧 使用正确的隐藏城市标记
    isThrowawayDeal: (apiItinerary.is_throwaway_deal as boolean) || false,
    isTrueHiddenCity: (apiItinerary.is_true_hidden_city as boolean) || false,
    hiddenDestination,
  };

  console.log('=== 简化后的价格映射结果 ===');
  console.log('最终价格对象:', result.price);
  console.log('甩尾票标记:', result.isHiddenCity, result.isThrowawayDeal);
  console.log('最终映射结果:', result);
  return result;
};