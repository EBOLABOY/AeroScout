/**
 * V2 API响应格式适配器
 * 将V2的UnifiedSearchResponse转换为V1兼容的FlightSearchResponse格式
 */

// V1兼容的航班接口
export interface V1Flight {
  id: string;
  price: {
    amount: number;
    currency: string;
  };
  booking_token?: string;
  deep_link?: string;
  segments?: V1FlightSegment[];
  outbound_segments?: V1FlightSegment[];
  inbound_segments?: V1FlightSegment[];
  total_duration_minutes?: number;
  is_self_transfer?: boolean;
  is_hidden_city?: boolean;
  is_throwaway_deal?: boolean;
  data_source?: string;
  raw_data?: Record<string, unknown>;
}

export interface V1FlightSegment {
  id?: string;
  departure_airport: string;
  departure_airport_name?: string;
  departure_city?: string;
  arrival_airport: string;
  arrival_airport_name?: string;
  arrival_city?: string;
  departure_time: string;
  arrival_time: string;
  departure_time_utc?: string;
  arrival_time_utc?: string;
  duration_minutes: number;
  carrier_code: string;
  carrier_name?: string;
  operating_carrier_code?: string;
  operating_carrier_name?: string;
  flight_number?: string;
  cabin_class?: string;
  hidden_destination?: Record<string, unknown>;
}

// V2 API实际响应接口 (匹配backend UnifiedSearchResponse)
export interface V2Price {
  amount: number;
  currency: string;
}

export interface V2FlightSegment {
  id?: string;
  departure: {
    airport_code: string;
    airport_name?: string;
    city_name?: string;
    local_time: string;
    utc_time?: string;
  };
  arrival: {
    airport_code: string;
    airport_name?: string;
    city_name?: string;
    local_time: string;
    utc_time?: string;
  };
  duration_minutes: number;
  carrier: {
    code: string;
    name?: string;
  };
  operating_carrier?: {
    code: string;
    name?: string;
  };
  flight_number?: string;
  cabin_class?: string;
  hidden_destination?: Record<string, unknown>;
}

export interface V2EnhancedFlightItinerary {
  id: string;
  price: V2Price;
  booking_token?: string;
  deep_link?: string;
  segments?: V2FlightSegment[];
  outbound_segments?: V2FlightSegment[];
  inbound_segments?: V2FlightSegment[];
  total_duration_minutes?: number;
  is_self_transfer?: boolean;
  is_hidden_city?: boolean;
  is_throwaway_deal?: boolean;
  data_source?: string;
  raw_data?: Record<string, unknown>;
  
  // V2 增强字段
  quality_score?: number;
  hub_info?: {
    hub_city?: string;
    hub_airport?: string;
    routing_type?: string;
  };
  risk_factors: string[];
  recommendation_reason?: string;
  disclaimers?: string[];
}

// V2 API实际响应格式 (UnifiedSearchResponse)
export interface V2UnifiedSearchResponse {
  search_id: string;
  direct_flights: V2EnhancedFlightItinerary[];
  combo_deals: V2EnhancedFlightItinerary[];
  disclaimers: string[];
  probe_details?: Record<string, unknown>;
  phase_metrics?: Record<string, unknown>;
  total_results?: number;
}

// V1兼容的响应格式
export interface V1CompatibleResponse {
  search_id: string;
  direct_flights: V1Flight[];
  combo_deals: V1Flight[];
  disclaimers: string[];
  probe_details?: Record<string, unknown>;
}

/**
 * 将V2航段转换为V1格式
 */
function convertV2SegmentToV1(v2Segment: V2FlightSegment): V1FlightSegment {
  return {
    id: v2Segment.id,
    departure_airport: v2Segment.departure.airport_code,
    departure_airport_name: v2Segment.departure.airport_name,
    departure_city: v2Segment.departure.city_name,
    arrival_airport: v2Segment.arrival.airport_code,
    arrival_airport_name: v2Segment.arrival.airport_name,
    arrival_city: v2Segment.arrival.city_name,
    departure_time: v2Segment.departure.local_time,
    arrival_time: v2Segment.arrival.local_time,
    departure_time_utc: v2Segment.departure.utc_time,
    arrival_time_utc: v2Segment.arrival.utc_time,
    duration_minutes: v2Segment.duration_minutes,
    carrier_code: v2Segment.carrier.code,
    carrier_name: v2Segment.carrier.name,
    operating_carrier_code: v2Segment.operating_carrier?.code,
    operating_carrier_name: v2Segment.operating_carrier?.name,
    flight_number: v2Segment.flight_number,
    cabin_class: v2Segment.cabin_class,
    hidden_destination: v2Segment.hidden_destination
  };
}

/**
 * 将V2航班转换为V1格式
 */
function convertV2FlightToV1(v2Flight: V2EnhancedFlightItinerary): V1Flight {
  return {
    id: v2Flight.id,
    price: {
      amount: v2Flight.price.amount,
      currency: v2Flight.price.currency
    },
    booking_token: v2Flight.booking_token,
    deep_link: v2Flight.deep_link,
    segments: v2Flight.segments?.map(convertV2SegmentToV1) || [],
    outbound_segments: v2Flight.outbound_segments?.map(convertV2SegmentToV1),
    inbound_segments: v2Flight.inbound_segments?.map(convertV2SegmentToV1),
    total_duration_minutes: v2Flight.total_duration_minutes,
    is_self_transfer: v2Flight.is_self_transfer,
    is_hidden_city: v2Flight.is_hidden_city,
    is_throwaway_deal: v2Flight.is_throwaway_deal,
    data_source: v2Flight.data_source,
    raw_data: {
      ...v2Flight.raw_data,
      // 添加V2增强信息
      v2_enhanced: {
        quality_score: v2Flight.quality_score,
        risk_factors: v2Flight.risk_factors,
        recommendation_reason: v2Flight.recommendation_reason,
        hub_info: v2Flight.hub_info,
        disclaimers: v2Flight.disclaimers
      }
    }
  };
}

/**
 * 主适配器函数：将V2响应转换为V1兼容格式
 */
export function adaptV2ResponseToV1(v2Response: V2UnifiedSearchResponse): V1CompatibleResponse {
  console.log('🔄 适配V2响应格式到V1兼容格式');
  console.log('V2响应数据:', v2Response);

  // 转换直飞航班
  const directFlights = v2Response.direct_flights.map(convertV2FlightToV1);
  
  // 转换组合/甩尾航班
  const comboDeals = v2Response.combo_deals.map(convertV2FlightToV1);

  const adaptedResponse: V1CompatibleResponse = {
    search_id: v2Response.search_id,
    direct_flights: directFlights,
    combo_deals: comboDeals,
    disclaimers: v2Response.disclaimers,
    probe_details: v2Response.probe_details
  };

  console.log('✅ V2到V1适配完成');
  console.log('适配后数据:', {
    search_id: adaptedResponse.search_id,
    direct_flights_count: adaptedResponse.direct_flights.length,
    combo_deals_count: adaptedResponse.combo_deals.length,
    disclaimers_count: adaptedResponse.disclaimers.length
  });

  return adaptedResponse;
}

/**
 * V2 API调用包装器
 */
export async function callV2SearchAPI(payload: Record<string, unknown>): Promise<V1CompatibleResponse> {
  console.log('🚀 调用V2航班搜索API');
  console.log('请求payload:', payload);
  
  try {
    // 修复URL配置 - 添加完整的后端地址
    const apiUrl = 'http://localhost:8000/api/v2/flights/search-sync';
    console.log('🔗 V2 API URL:', apiUrl);
    
    // 调用V2的统一搜索接口
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    });

    console.log('📡 V2 API响应状态:', response.status, response.statusText);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ V2 API错误响应:', errorText);
      throw new Error(`V2 API调用失败: ${response.status} ${response.statusText}`);
    }

    const v2Response: V2UnifiedSearchResponse = await response.json();
    console.log('✅ V2 API响应成功:', v2Response);
    console.log('📊 V2响应数据结构:');
    console.log('  - search_id:', v2Response.search_id);
    console.log('  - direct_flights数量:', v2Response.direct_flights?.length || 0);
    console.log('  - combo_deals数量:', v2Response.combo_deals?.length || 0);
    console.log('  - disclaimers数量:', v2Response.disclaimers?.length || 0);
    
    // 检查第一个航班的数据结构
    if (v2Response.direct_flights?.length > 0) {
      console.log('🔍 第一个直飞航班数据结构:', v2Response.direct_flights[0]);
    }
    if (v2Response.combo_deals?.length > 0) {
      console.log('🔍 第一个组合航班数据结构:', v2Response.combo_deals[0]);
    }
    
    // 适配为V1格式
    const adaptedResponse = adaptV2ResponseToV1(v2Response);
    console.log('🔄 适配后的响应:', adaptedResponse);
    
    return adaptedResponse;
    
  } catch (error) {
    console.error('❌ V2 API调用失败:', error);
    console.error('❌ 错误详情:', {
      message: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined
    });
    throw error;
  }
}

/**
 * 增强的航班信息提取器（利用V2的额外信息）
 */
export function extractV2EnhancedInfo(flight: V1Flight): {
  quality_score?: number;
  risk_factors: string[];
  recommendation_reason?: string;
  hub_info?: Record<string, unknown>;
  disclaimers?: string[];
} {
  const v2Enhanced = (flight.raw_data as Record<string, unknown>)?.v2_enhanced as Record<string, unknown>;
  
  if (!v2Enhanced) {
    return { risk_factors: [] };
  }

  return {
    quality_score: v2Enhanced.quality_score as number | undefined,
    risk_factors: (v2Enhanced.risk_factors as string[]) || [],
    recommendation_reason: v2Enhanced.recommendation_reason as string | undefined,
    hub_info: v2Enhanced.hub_info as Record<string, unknown> | undefined,
    disclaimers: (v2Enhanced.disclaimers as string[]) || []
  };
} 