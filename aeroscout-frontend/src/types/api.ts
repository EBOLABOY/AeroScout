/**
 * API请求和响应类型定义
 */

export interface FlightSearchRequest {
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
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface AsyncTaskResponse {
  task_id: string;
  status: string;
  message?: string;
}

export interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}

export interface ApiError {
  detail: string | ValidationError[];
  status_code?: number;
}

// ===== 简化航班搜索API类型定义 =====

export interface SimplifiedFlightSearchRequest {
  origin_iata: string;
  destination_iata: string;
  departure_date_from: string;
  departure_date_to: string;
  return_date_from?: string;
  return_date_to?: string;
  adults: number;
  cabin_class: string;
  preferred_currency?: string;
  max_results_per_type?: number;
  max_pages_per_search?: number;
  direct_flights_only_for_primary?: boolean;
}

export interface SimplifiedFlightPrice {
  amount: number;
  currency: string;
  price_eur: number;
}

export interface SimplifiedFlightCarrier {
  code: string;
  name: string;
}

export interface SimplifiedFlightLocation {
  code: string;
  name: string;
  city: string;
  country?: string; // 添加country字段以匹配后端数据
}

export interface SimplifiedFlightTime {
  local_time: string;
  utc_time: string;
}

export interface SimplifiedFlightSegment {
  id: string;
  flight_number: string;
  carrier: SimplifiedFlightCarrier;
  origin: SimplifiedFlightLocation;
  destination: SimplifiedFlightLocation;
  departure: SimplifiedFlightTime;
  arrival: SimplifiedFlightTime;
  duration_minutes: number;
  cabin_class: string;
}

export interface SimplifiedTravelHack {
  is_true_hidden_city: boolean;
  is_virtual_interlining: boolean;
  is_throwaway_ticket: boolean;
}

export interface SimplifiedFlightItinerary {
  id: string;
  price: SimplifiedFlightPrice;
  duration_minutes: number;
  segments: SimplifiedFlightSegment[];
  travel_hack: SimplifiedTravelHack;
  booking_url: string;
  stops_count: number;
  departure_time: string;
  arrival_time: string;
  origin: SimplifiedFlightLocation;
  destination: SimplifiedFlightLocation;
  is_hidden_city: boolean;
  flight_type: 'direct' | 'hidden_city';
  hidden_destination?: SimplifiedFlightLocation;
  throwaway_destination?: SimplifiedFlightLocation | string;
  // 后端实际返回的数据结构
  hidden_destinations?: SimplifiedFlightLocation[];
}

export interface SimplifiedFlightSearchResponse {
  search_id: string;
  direct_flights: SimplifiedFlightItinerary[];
  hidden_city_flights: SimplifiedFlightItinerary[];
  search_time_ms: number;
  disclaimers: string[];
  user_id: number;
  search_params: {
    origin: string;
    destination: string;
    departure_date: string;
    return_date?: string;
    adults: number;
    cabin_class: string;
    preferred_currency: string;
  };
}