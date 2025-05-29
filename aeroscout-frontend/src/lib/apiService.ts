import axios, { AxiosError } from 'axios';
import { useAuthStore } from '../store/authStore';
import { getFriendlyErrorMessage } from './errorHandler';
import { useAlertStore } from '../store/alertStore';

// 创建 axios 实例
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json; charset=utf-8',
    'Accept': 'application/json',
    'Accept-Charset': 'utf-8',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const accessToken = useAuthStore.getState().accessToken;
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error: AxiosError) => {
    const { showAlert } = useAlertStore.getState();
    // 使用更具体的类型断言，AxiosError 的结构与 ApiError 兼容
    const friendlyMessage = getFriendlyErrorMessage(error as unknown as Parameters<typeof getFriendlyErrorMessage>[0]);

    if (error.response?.status === 401) {
      // 对于401错误，除了显示提示外，还需要执行登出和重定向
      showAlert(friendlyMessage, 'error', '认证失败');
      useAuthStore.getState().logout();
      if (typeof window !== 'undefined' && window.location.pathname !== '/auth/login') {
        window.location.href = '/auth/login';
      }
    } else {
      // 对于其他错误，只显示提示
      // 避免在已经准备跳转到登录页时再次弹出非401的错误提示
      if (!(error.response?.status === 401 && typeof window !== 'undefined' && window.location.pathname === '/auth/login')) {
         showAlert(friendlyMessage, 'error');
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;

// Types for Airport Search (新的简化接口)
export interface AirportSearchRequest {
  query: string;
  trip_type: 'flight' | string;
  mode: 'dep' | 'arr' | string;
}

export interface AirportInfo {
  code: string; // 机场IATA代码
  name: string; // 机场名称
  city: string; // 城市名称
  country: string; // 国家名称
  type: string; // POI类型
}

export interface AirportSearchResponse {
  success: boolean;
  airports: AirportInfo[];
  total: number;
  query: string;
}

// 保留旧的POI接口以兼容现有代码
export interface PoiSearchRequest {
  query: string;
  trip_type: 'flight' | string;
  mode: 'dep' | 'arr' | string;
}

export interface PoiItem {
  id?: string | number;
  name?: string;
  code?: string;
  city_name?: string;
  country_name?: string;
  display_name?: string;
  type?: 'AIRPORT' | 'CITY' | 'LOCATION' | string;
  iata?: string;
  coordinates?: {
    latitude?: number;
    longitude?: number;
  };
  label?: string;
  value?: string;
  source?: string;
  isDomestic?: boolean;
  isPopular?: boolean;
  [key: string]: unknown;
}

export interface PoiSearchResponseData {
  ResponseStatus?: {
    Ack?: string;
    Errors?: unknown[];
    Build?: string;
    Version?: string;
    [key: string]: unknown;
  };
  keyword?: string;
  dataList?: PoiItem[];
  results?: PoiItem[];
  list?: PoiItem[];
  [key: string]: unknown;
}

export interface PoiSearchResponse {
  success: boolean;
  data: PoiSearchResponseData;
}

// Types for Flight Search
export interface FlightSearchRequestPayload {
  origin_iata: string;
  destination_iata: string;
  departure_date_from: string;
  departure_date_to: string;
  // TODO: Add other relevant fields based on FlightSearchForm.tsx payload
  is_one_way: boolean;
}

/**
 * 搜索机场 (新的简化接口)
 * @param params - 搜索参数
 * @returns 机场搜索响应
 */
export const searchAirports = async (params: AirportSearchRequest): Promise<AirportSearchResponse> => {
  try {
    const response = await apiClient.post<AirportSearchResponse>('/api/v1/poi/search', params);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Searches for Points of Interest (POI) like airports or cities.
 * @param params - The search parameters.
 * @returns A promise that resolves to the POI search response.
 * @deprecated 使用 searchAirports 替代
 */
export const searchPoi = async (params: PoiSearchRequest): Promise<PoiSearchResponse> => {
  try {
    const response = await apiClient.post<PoiSearchResponse>('/api/v1/poi/search', params);
    return response.data;
  } catch (error) {
    // 错误已在拦截器中处理并显示提示，这里不再需要console.error
    // 仍然向上抛出错误，以便调用方可以根据需要执行额外的逻辑 (例如停止加载状态)
    throw error;
  }
};

// Types for Task Result from API
// These types should match the structure in API_Documentation.md for task results (lines 380-389)
// and the FlightItinerary structure used by the backend's Kiwi service (though not directly exposed, it influences these fields)

export interface ApiAirportInfo {
    code: string; // IATA code, e.g., "PVG"
    name: string; // Airport name, e.g., "Shanghai Pudong International Airport"
    city_name: string; // City name, e.g., "Shanghai"
    city_code?: string; // City IATA code if available
    country_name?: string; // Country name
    country_code?: string; // Country code
}

export interface ApiAirlineInfo {
    code: string; // Airline IATA code, e.g., "CA"
    name: string; // Airline name, e.g., "Air China"
    logo_url?: string; // URL for the airline's logo
}

// 请确保替换或更新文件中已有的 ApiFlightSegment 和 ApiFlightItinerary 接口
// (通常这些类型定义在文件的顶部或特定区域)

export interface ApiFlightSegment {
    id?: string; // 后端: segment_id (Optional[str]) -> 前端: id (可选字符串)
    departureAirportCode: string; // 后端: departure_airport (str) -> 前端: departureAirportCode (字符串)
    departureAirportName?: string; // 后端: departure_airport_name (Optional[str]) -> 前端: departureAirportName (可选字符串)
    departureCityName?: string; // 后端: departure_city (Optional[str]) -> 前端: departureCityName (可选字符串)
    arrivalAirportCode: string; // 后端: arrival_airport (str) -> 前端: arrivalAirportCode (字符串)
    arrivalAirportName?: string; // 后端: arrival_airport_name (Optional[str]) -> 前端: arrivalAirportName (可选字符串)
    arrivalCityName?: string; // 后端: arrival_city (Optional[str]) -> 前端: arrivalCityName (可选字符串)
    departureTime: string; // 后端: departure_time (datetime) -> 前端: departureTime (ISO 8601 字符串)
    arrivalTime: string; // 后端: arrival_time (datetime) -> 前端: arrivalTime (ISO 8601 字符串)
    departureTimeUtc?: string; // 后端: departure_time_utc (Optional[datetime]) -> 前端: departureTimeUtc (可选 ISO 8601 字符串)
    arrivalTimeUtc?: string; // 后端: arrival_time_utc (Optional[datetime]) -> 前端: arrivalTimeUtc (可选 ISO 8601 字符串)
    durationMinutes: number; // 后端: duration_minutes (int) -> 前端: durationMinutes (数字)
    airlineCode: string; // 后端: carrier_code (str) -> 前端: airlineCode (字符串)
    airlineName?: string; // 后端: carrier_name (Optional[str]) -> 前端: airlineName (可选字符串)
    operatingCarrierCode?: string; // 后端: operating_carrier_code (Optional[str]) -> 前端: operatingCarrierCode (可选字符串)
    operatingCarrierName?: string; // 后端: operating_carrier_name (Optional[str]) -> 前端: operatingCarrierName (可选字符串)
    flightNumber: string; // 后端: flight_number (str) -> 前端: flightNumber (字符串)
    cabinClass?: string; // 后端: cabin_class (Optional[str]) -> 前端: cabinClass (可选字符串)
    aircraft?: string; // 后端: aircraft (Optional[str]) -> 前端: aircraft (可选字符串) // 注意：前端之前可能用 equipment
    layoverDurationMinutes?: number; // 后端: layover_duration_minutes (Optional[int]) -> 前端: layoverDurationMinutes (可选数字)
    isBaggageRecheck?: boolean; // 后端: is_baggage_recheck (Optional[bool]) -> 前端: isBaggageRecheck (可选布尔值)
    departureTerminal?: string; // 后端: departure_terminal (Optional[str]) -> 前端: departureTerminal (可选字符串)
    arrivalTerminal?: string; // 后端: arrival_terminal (Optional[str]) -> 前端: arrivalTerminal (可选字符串)
    nextSegmentRequiresAirportChange?: boolean; // 后端: next_segment_requires_airport_change (Optional[bool]) -> 前端: nextSegmentRequiresAirportChange (可选布尔值)

    // 此字段需要在映射函数中根据 airlineCode 构建, 类型定义中保留
    airlineLogoUrl?: string;
}

// This is the structure for items in `direct_flights` and `combo_deals` arrays from the API
export interface ApiFlightItinerary {
    id: string; // 后端: id (str) -> 前端: id (字符串)
    priceEur: number; // 后端: price_eur (float) -> 前端: priceEur (数字)
    priceCurrency?: string; // 后端: price_currency (Optional[str]) -> 前端: priceCurrency (可选字符串)
    bookingToken: string; // 后端: booking_token (str) -> 前端: bookingToken (字符串)
    deepLink: string; // 后端: deep_link (str) -> 前端: deepLink (字符串)
    segments: ApiFlightSegment[]; // 将由后端 outbound_segments 和 inbound_segments 合并映射而来
    totalDurationMinutes: number; // 后端: total_duration_minutes (int) -> 前端: totalDurationMinutes (数字)
    isSelfTransfer: boolean; // 后端: is_self_transfer (bool) -> 前端: isSelfTransfer (布尔值)
    isHiddenCity: boolean; // 后端: is_hidden_city (bool) -> 前端: isHiddenCity (布尔值)
    dataSource: string; // 后端: data_source (str) -> 前端: dataSource (字符串)
    isThrowawayDeal?: boolean; // 后端: is_throwaway_deal (Optional[bool]) -> 前端: isThrowawayDeal (可选布尔值)

    // 探测结果相关字段
    isProbeSuggestion?: boolean; // 后端: is_probe_suggestion (Optional[bool]) -> 前端: isProbeSuggestion (可选布尔值)
    probeHub?: string; // 后端: probe_hub (Optional[str]) -> 前端: probeHub (可选字符串)
    probeHubCity?: string; // 后端: probe_hub_city (Optional[str]) -> 前端: probeHubCity (可选字符串)
    probeDisclaimer?: string; // 后端: probe_disclaimer (Optional[str]) -> 前端: probeDisclaimer (可选字符串)
    probeStrategy?: string; // 后端: probe_strategy (Optional[str]) -> 前端: probeStrategy (可选字符串)

    rawData?: Record<string, unknown>; // 后端: raw_data (Optional[Dict[str, Any]]) -> 前端: rawData (可选对象)
    airlines?: Array<{ // 参与该行程的所有航司信息
        code: string;
        name: string;
        logoUrl?: string;
    }>;

    // 以下字段需要在映射函数中计算或逻辑处理, 类型定义中保留
    isDirectFlight: boolean;
    numberOfStops?: number;

    [key: string]: unknown; // 允许 API 可能返回的其他未明确定义的属性
}

export interface TaskResultData { // This is the 'result' field in TaskResultResponse
  search_id?: string; // As per API_Documentation.md line 380
  direct_flights?: ApiFlightItinerary[]; // Updated type
  combo_deals?: ApiFlightItinerary[];    // Updated type
  disclaimers?: string[]; // Updated to string array based on API_Documentation.md line 387
  probe_details?: Record<string, unknown>; // As per API_Documentation.md line 388
  // Add other fields from the API response as needed
  [key: string]: unknown;
}

export interface TaskResultResponse {
  task_id: string;
  status: 'PENDING' | 'STARTED' | 'SUCCESS' | 'FAILURE' | string; // Add other potential statuses
  result?: TaskResultData | null;
  error?: string | null;
}

// V2 API 统一搜索响应
export interface UnifiedSearchResponse {
  search_id: string;
  direct_flights: ApiFlightItinerary[];
  combo_deals: ApiFlightItinerary[];
  disclaimers: string[];
  probe_details?: Record<string, unknown>;
  phase_metrics: Record<string, unknown>;
  total_results: number;
}

/**
 * Fetches the result of a flight search task.
 * @param taskId - The ID of the task.
 * @returns A promise that resolves to the task result response.
 */
export const getTaskResult = async (taskId: string): Promise<TaskResultResponse> => {
  try {
    const response = await apiClient.get<TaskResultResponse>(`/api/v1/tasks/results/${taskId}`);
    return response.data;
  } catch (error) {
    // 错误已在拦截器中处理并显示提示
    throw error;
  }
};

// Types for Admin API responses
export interface CreateInvitationResponse {
  invitation_code: string;
}

export interface PopulateHubsResponse {
  message: string;
}

/**
 * Creates a new invitation code. (Admin only)
 * @returns A promise that resolves to the new invitation code.
 */
export const createInvitationCode = async (): Promise<CreateInvitationResponse> => {
  try {
    const response = await apiClient.post<CreateInvitationResponse>('/api/v1/admin/invitations');
    return response.data;
  } catch (error) {
    // 错误已在拦截器中处理并显示提示
    throw error;
  }
};

/**
 * Populates hub cities from configuration. (Admin only)
 * @returns A promise that resolves to the operation result message.
 */
export const populateHubs = async (): Promise<PopulateHubsResponse> => {
  try {
    const response = await apiClient.post<PopulateHubsResponse>('/api/v1/admin/populate-hubs');
    return response.data;
  } catch (error) {
    // 错误已在拦截器中处理并显示提示
    throw error;
  }
};

// Dashboard API 接口类型定义
export interface RecentSearchResponse {
  data: Array<{
    id: string;
    from_location: string;
    to_location: string;
    date: string;
    searched_at: string;
    passengers: number;
    is_favorite: boolean;
  }>;
  message: string;
  success: boolean;
}

export interface ApiUsageStatsResponse {
  data: {
    poi_calls_today: number;
    flight_calls_today: number;
    poi_daily_limit: number;
    flight_daily_limit: number;
    reset_date: string;
    usage_percentage: number;
    is_near_limit: boolean;
  };
  message: string;
  success: boolean;
}

export interface DailyApiUsageData {
  date: string;
  poi_calls: number;
  flight_calls: number;
  total_calls: number;
}

export interface ApiUsageHistoryResponse {
  data: DailyApiUsageData[];
  message: string;
  success: boolean;
}

export interface SearchOperationResponse {
  success: boolean;
  message: string;
  search_id: string;
}

export interface SearchFavoriteResponse extends SearchOperationResponse {
  is_favorite: boolean;
}

export interface InvitationCodeResponse {
  data: Array<{
    id: number;
    code: string;
    is_used: boolean;
    created_at: string;
    used_at: string | null;
  }>;
  message: string;
  success: boolean;
}

/**
 * 获取用户最近搜索记录
 * @param limit - 返回记录的最大数量，默认10条
 * @returns 用户最近搜索记录
 */
export const getUserRecentSearches = async (limit: number = 10): Promise<RecentSearchResponse> => {
  try {
    const response = await apiClient.get<RecentSearchResponse>(`/api/v1/users/me/recent-searches?limit=${limit}`);
    return response.data;
  } catch (error) {
    // 错误已在拦截器中处理并显示提示
    throw error;
  }
};

/**
 * 获取用户API使用统计
 * @returns 用户API使用统计信息
 */
export const getUserApiUsageStats = async (): Promise<ApiUsageStatsResponse> => {
  try {
    const response = await apiClient.get<ApiUsageStatsResponse>('/users/me/usage-stats');
    return response.data;
  } catch (error) {
    // 错误已在拦截器中处理并显示提示
    throw error;
  }
};

/**
 * 获取用户邀请码列表
 * @returns 用户邀请码列表
 */
export const getUserInvitationCodes = async (): Promise<InvitationCodeResponse> => {
  try {
    const response = await apiClient.get<InvitationCodeResponse>('/users/me/invitation-codes');
    return response.data;
  } catch (error) {
    // 错误已在拦截器中处理并显示提示
    throw error;
  }
};

/**
 * 获取用户API使用历史（过去N天）
 * @param days - 要获取的天数，默认7天
 * @returns API使用历史数据
 */
export const getUserApiUsageHistory = async (days: number = 7): Promise<ApiUsageHistoryResponse> => {
  try {
    const response = await apiClient.get<ApiUsageHistoryResponse>(`/users/me/usage-history?days=${days}`);
    return response.data;
  } catch (error) {
    // 错误已在拦截器中处理并显示提示
    throw error;
  }
};

/**
 * 删除单条搜索记录
 * @param searchId - 搜索记录ID
 * @returns 操作结果
 */
export const deleteSearchRecord = async (searchId: string): Promise<SearchOperationResponse> => {
  try {
    const response = await apiClient.delete<SearchOperationResponse>(`/users/me/recent-searches/${searchId}`);
    return response.data;
  } catch (error) {
    // 错误已在拦截器中处理并显示提示
    throw error;
  }
};

/**
 * 收藏/取消收藏搜索记录
 * @param searchId - 搜索记录ID
 * @param isFavorite - 是否收藏
 * @returns 操作结果
 */
export const toggleSearchFavorite = async (searchId: string, isFavorite: boolean): Promise<SearchFavoriteResponse> => {
  try {
    if (isFavorite) {
      const response = await apiClient.post<SearchFavoriteResponse>(`/users/me/favorite-searches/${searchId}`);
      return response.data;
    } else {
      const response = await apiClient.delete<SearchFavoriteResponse>(`/users/me/favorite-searches/${searchId}`);
      return response.data;
    }
  } catch (error) {
    // 错误已在拦截器中处理并显示提示
    throw error;
  }
};

// 航班搜索相关接口
export interface FlightSearchRequestV2 {
  origin_iata: string;
  destination_iata: string;
  departure_date_from: string;
  departure_date_to: string;
  return_date_from?: string;
  return_date_to?: string;
  adults: number;
  children?: number;
  infants?: number;
  cabin_class: string;
  direct_flights_only_for_primary: boolean;
  enable_hub_probe: boolean;
  is_one_way: boolean;
  market?: string;
  // 添加额外的搜索配置字段
  include_hidden_city?: boolean;
  max_stopover_count?: number;
  direct_flights_only?: boolean;
  max_results?: number;
  enable_cache?: boolean;
  sort_strategy?: string;
}

// 新的简化搜索API响应类型定义
export interface SimplifiedSearchResponse {
  search_id: string;
  direct_flights: SimplifiedFlightItinerary[];
  hidden_city_flights: SimplifiedFlightItinerary[];
  search_time_ms: number;
  disclaimers?: {
    show_direct_flight_disclaimer_key?: boolean;
    show_hidden_city_disclaimer_key?: boolean;
  };
  user_id?: string | null;
  search_params: Record<string, any>;
}

export interface SimplifiedFlightItinerary {
  id: string;
  price: {
    amount: number;
    currency: string;
  };
  display_flight_type: string;
  user_perceived_destination_airport: {
    code: string;
    name: string;
    city: string;
    country_code: string;
    country_name: string;
  };
  user_journey_segments_to_display: SimplifiedFlightSegment[];
  user_journey_layovers_to_display: SimplifiedLayover[];
  user_journey_duration_minutes: number;
  user_journey_arrival_datetime_local: string;
  user_alert_notes: string[];
  ticketed_origin_airport: {
    code: string;
    name: string;
    city: string;
    country_code: string;
    country_name: string;
  };
  ticketed_final_destination_airport: {
    code: string;
    name: string;
    city: string;
    country_code: string;
    country_name: string;
  };
  ticketed_departure_datetime_local: string;
  ticketed_arrival_datetime_local: string;
  ticketed_stops_count: number;
  booking_options: BookingOption[];
  default_booking_url: string;
  api_travel_hack_info?: {
    is_true_hidden_city: boolean;
    is_virtual_interlining: boolean;
    is_throwaway_ticket: boolean;
  };
}

export interface SimplifiedFlightSegment {
  flight_number: string;
  marketing_carrier: {
    code: string;
    name: string;
  };
  operating_carrier?: {
    code: string;
    name: string;
  };
  origin: {
    code: string;
    name: string;
    city: string;
    country_code: string;
    country_name: string;
  };
  ticketed_destination: {
    code: string;
    name: string;
    city: string;
    country_code: string;
    country_name: string;
  };
  departure: {
    local_time: string;
    utc_time: string;
  };
  arrival: {
    local_time: string;
    utc_time: string;
  };
  duration_minutes: number;
}

export interface SimplifiedLayover {
  duration_minutes: number;
  airport_code: string;
  airport_name: string;
  city: string;
  arrival_at_layover_local: string;
  departure_from_layover_local: string;
}

export interface BookingOption {
  token: string;
  url: string;
  price_amount: number;
}

/**
 * 执行航班搜索 (V2 API - 同步搜索)
 * @param searchData - 搜索参数
 * @returns 搜索结果
 */
export const searchFlightsV2 = async (searchData: FlightSearchRequestV2): Promise<SimplifiedSearchResponse> => {
  try {
    // 转换为简化搜索API格式
    const requestData = {
      origin_iata: searchData.origin_iata,
      destination_iata: searchData.destination_iata,
      departure_date_from: searchData.departure_date_from,
      departure_date_to: searchData.departure_date_to,
      return_date_from: searchData.return_date_from,
      return_date_to: searchData.return_date_to,
      adults: searchData.adults,
      cabin_class: searchData.cabin_class,
      preferred_currency: 'CNY',
      max_results_per_type: 50,
      max_pages_per_search: 3,
      direct_flights_only_for_primary: searchData.direct_flights_only_for_primary
    };

    // 使用V2 simplified flights端点
    const response = await apiClient.post<SimplifiedSearchResponse>('/v2/flights/search-simple', requestData, {
      params: {
        include_direct: true,
        include_hidden_city: true
      }
    });

    // 直接返回新的API响应格式
    return response.data;
  } catch (error) {
    // 错误已在拦截器中处理并显示提示
    throw error;
  }
};


