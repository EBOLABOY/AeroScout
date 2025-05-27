/**
 * 修复后的V2 API响应格式适配器
 * 基于实际的V2后端响应格式
 */

// V1兼容格式（前端期望的格式）
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
}

export interface V1Flight {
  id: string;
  price: number;  // 修改为平级格式，匹配后端返回和Store期望
  currency: string;  // 添加currency字段
  booking_token?: string;
  deep_link?: string;
  segments?: V1FlightSegment[];
  outbound_segments?: V1FlightSegment[];
  inbound_segments?: V1FlightSegment[];
  total_duration_minutes?: number;
  is_self_transfer?: boolean;
  is_hidden_city?: boolean;
  hidden_destination?: {  // 修改为对象类型，匹配后端返回格式
    code: string;
    name: string;
    city: string;
    country: string;
  };
  is_throwaway_deal?: boolean;
  data_source?: string;
  raw_data?: Record<string, unknown>;
}

// V2实际响应格式（基于测试结果）
export interface V2ActualFlightSegment {
  segment_id?: string | null;
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
  flight_number: string;
  cabin_class?: string;
  aircraft?: string | null;
  layover_duration_minutes?: number | null;
  is_baggage_recheck?: boolean | null;
  departure_terminal?: string | null;
  arrival_terminal?: string | null;
  next_segment_requires_airport_change?: boolean | null;
}

export interface V2ActualFlightItinerary {
  id: string;
  price: number;  // 直接是数字，不是对象
  currency: string;  // 单独的字段
  booking_token?: string;
  deep_link?: string;
  segments?: V2ActualFlightSegment[];
  outbound_segments?: V2ActualFlightSegment[];
  inbound_segments?: V2ActualFlightSegment[] | null;
  total_duration_minutes: number;
  is_self_transfer: boolean;
  is_hidden_city: boolean;
  hidden_destination?: {  // 修改为对象类型，匹配后端返回格式
    code: string;
    name: string;
    city: string;
    country: string;
  };
  is_throwaway_deal: boolean;
  data_source: string;
  raw_data?: Record<string, unknown>;
  
  // V2增强字段
  isProbeSuggestion?: boolean;
  probeHub?: string | null;
  probeDisclaimer?: string | null;
  search_phase?: string;
  quality_score?: number;
  hub_info?: Record<string, unknown> | null;
  risk_factors?: string[];
  recommendation_reason?: string;
}

export interface V2ActualResponse {
  search_id: string;
  direct_flights: V2ActualFlightItinerary[];
  combo_deals: V2ActualFlightItinerary[];
  disclaimers: string[];
  probe_details?: Record<string, unknown>;
  phase_metrics?: Record<string, unknown>;
  total_results?: number;
}

export interface V1CompatibleResponse {
  search_id: string;
  direct_flights: V1Flight[];
  combo_deals: V1Flight[];
  disclaimers: string[];
  probe_details?: Record<string, unknown>;
}

/**
 * 将V2实际航段转换为V1格式
 */
function convertV2ActualSegmentToV1(v2Segment: V2ActualFlightSegment): V1FlightSegment {
  return {
    id: v2Segment.segment_id || undefined,
    departure_airport: v2Segment.departure_airport,
    departure_airport_name: v2Segment.departure_airport_name,
    departure_city: v2Segment.departure_city,
    arrival_airport: v2Segment.arrival_airport,
    arrival_airport_name: v2Segment.arrival_airport_name,
    arrival_city: v2Segment.arrival_city,
    departure_time: v2Segment.departure_time,
    arrival_time: v2Segment.arrival_time,
    departure_time_utc: v2Segment.departure_time_utc,
    arrival_time_utc: v2Segment.arrival_time_utc,
    duration_minutes: v2Segment.duration_minutes,
    carrier_code: v2Segment.carrier_code,
    carrier_name: v2Segment.carrier_name,
    operating_carrier_code: v2Segment.operating_carrier_code,
    operating_carrier_name: v2Segment.operating_carrier_name,
    flight_number: v2Segment.flight_number,
    cabin_class: v2Segment.cabin_class
  };
}

/**
 * 将V2实际航班转换为V1格式
 */
function convertV2ActualFlightToV1(v2Flight: V2ActualFlightItinerary): V1Flight {
  console.log('🔄 转换V2航班到V1格式:', v2Flight);
  console.log('📊 原始价格信息 - price:', v2Flight.price, '(类型:', typeof v2Flight.price, '), currency:', v2Flight.currency);
  console.log('🎯 甩尾票标记 - is_hidden_city:', v2Flight.is_hidden_city, ', is_throwaway_deal:', v2Flight.is_throwaway_deal);
  
  // 增强价格验证和调试
  let validatedPrice = v2Flight.price;
  const validatedCurrency = v2Flight.currency || 'CNY';
  
  // 价格验证和修复
  if (validatedPrice === null || validatedPrice === undefined) {
    console.error('❌ 价格为null/undefined:', validatedPrice);
    validatedPrice = 0; // 这会导致显示"价格待定"
  } else if (typeof validatedPrice === 'string') {
    console.warn('⚠️ 价格为字符串类型，尝试转换:', validatedPrice);
    const parsed = parseFloat(validatedPrice);
    if (isNaN(parsed)) {
      console.error('❌ 价格字符串无法转换为数字:', validatedPrice);
      validatedPrice = 0;
    } else {
      validatedPrice = parsed;
      console.log('✅ 价格字符串转换成功:', validatedPrice);
    }
  } else if (typeof validatedPrice !== 'number') {
    console.error('❌ 价格类型无效:', typeof validatedPrice, validatedPrice);
    validatedPrice = 0;
  } else if (validatedPrice <= 0) {
    console.error('❌ 价格为零或负数:', validatedPrice);
    // 保持原值，让FlightCard处理显示"价格待定"
  }
  
  console.log('📊 验证后价格信息 - price:', validatedPrice, '(类型:', typeof validatedPrice, '), currency:', validatedCurrency);
  
  // 后端已经正确处理了价格转换，直接使用返回的平级格式
  const result = {
    id: v2Flight.id,
    price: validatedPrice,
    currency: validatedCurrency,
    booking_token: v2Flight.booking_token,
    deep_link: v2Flight.deep_link,
    segments: v2Flight.segments?.map(convertV2ActualSegmentToV1) || [],
    outbound_segments: v2Flight.outbound_segments?.map(convertV2ActualSegmentToV1),
    inbound_segments: v2Flight.inbound_segments?.map(convertV2ActualSegmentToV1),
    total_duration_minutes: v2Flight.total_duration_minutes,
    is_self_transfer: v2Flight.is_self_transfer,
    is_hidden_city: v2Flight.is_hidden_city,
    hidden_destination: v2Flight.hidden_destination,  // 添加隐藏目的地映射
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
        isProbeSuggestion: v2Flight.isProbeSuggestion,
        probeHub: v2Flight.probeHub,
        probeDisclaimer: v2Flight.probeDisclaimer
      }
    }
  };
  
  console.log('✅ 转换完成，最终价格:', result.price);
  return result;
}

/**
 * 航班过滤函数：只保留直飞航班和相关甩尾航班
 */
function filterRelevantFlights(flights: V1Flight[], origin: string, destination: string): V1Flight[] {
  console.log('🔍 开始过滤航班，保留直飞和甩尾票');
  
  return flights.filter(flight => {
    // 获取航班的起始和最终目的地
    const segments = flight.outbound_segments || flight.segments || [];
    if (segments.length === 0) return false;
    
    const firstSegment = segments[0];
    const lastSegment = segments[segments.length - 1];
    
    const flightOrigin = firstSegment.departure_airport;
    const flightDestination = lastSegment.arrival_airport;
    
    // 特殊处理：如果航班被标记为隐藏城市或甩尾票，始终保留
    if (flight.is_hidden_city || flight.is_throwaway_deal) {
      console.log('✅ 保留甩尾票/隐藏城市航班:', flight.id,
        `${flightOrigin} → ${flightDestination}`,
        `[隐藏城市: ${flight.is_hidden_city}, 甩尾票: ${flight.is_throwaway_deal}]`);
      return true;
    }
    
    // 情况1：直飞航班 (起点到终点)
    if (segments.length === 1 &&
        flightOrigin === origin &&
        flightDestination === destination) {
      console.log('✅ 保留直飞航班:', flight.id, `${flightOrigin} → ${flightDestination}`);
      return true;
    }
    
    // 情况2：甩尾航班 (起点到终点，但中转机场为目的地机场)
    if (segments.length > 1) {
      // 检查是否有任何中转点是我们的目的地
      const hasDestinationAsTransfer = segments.some((segment, index) => {
        // 不检查最后一个航段的到达地（那是最终目的地）
        if (index === segments.length - 1) return false;
        return segment.arrival_airport === destination;
      });
      
      if (flightOrigin === origin && hasDestinationAsTransfer) {
        console.log('✅ 保留甩尾航班:', flight.id, `${flightOrigin} → ${flightDestination} (经停 ${destination})`);
        return true;
      }
    }
    
    console.log('❌ 过滤掉不相关航班:', flight.id, `${flightOrigin} → ${flightDestination}`);
    return false;
  });
}

/**
 * 主适配器函数：将V2实际响应转换为V1兼容格式
 */
export function adaptV2ActualResponseToV1(v2Response: V2ActualResponse, searchParams?: { origin?: string, destination?: string }): V1CompatibleResponse {
  console.log('🔄 适配V2实际响应格式到V1兼容格式');
  console.log('V2实际响应数据:', v2Response);
  console.log('搜索参数:', searchParams);

  // 诊断：检查原始数据中的甩尾票
  console.log('🎯 诊断：检查原始V2响应中的甩尾票');
  const allV2Flights = [...v2Response.direct_flights, ...v2Response.combo_deals];
  const throwawayFlights = allV2Flights.filter(f => f.is_hidden_city || f.is_throwaway_deal);
  console.log(`  总航班数: ${allV2Flights.length}`);
  console.log(`  甩尾票数: ${throwawayFlights.length}`);
  if (throwawayFlights.length > 0) {
    console.log('  甩尾票详情:', throwawayFlights.map(f => ({
      id: f.id,
      is_hidden_city: f.is_hidden_city,
      is_throwaway_deal: f.is_throwaway_deal,
      route: f.segments ? `${f.segments[0].departure_airport} → ${f.segments[f.segments.length - 1].arrival_airport}` : 'N/A'
    })));
  }

  // 转换直飞航班
  let directFlights = v2Response.direct_flights.map(convertV2ActualFlightToV1);

  // 转换组合/甩尾航班
  let comboDeals = v2Response.combo_deals.map(convertV2ActualFlightToV1);

  // 诊断：检查转换后的甩尾票
  console.log('🎯 诊断：检查转换后的甩尾票');
  const allConvertedFlights = [...directFlights, ...comboDeals];
  const convertedThrowawayFlights = allConvertedFlights.filter(f => f.is_hidden_city || f.is_throwaway_deal);
  console.log(`  转换后总航班数: ${allConvertedFlights.length}`);
  console.log(`  转换后甩尾票数: ${convertedThrowawayFlights.length}`);

  // 应用航班过滤（如果提供了搜索参数）
  if (searchParams?.origin && searchParams?.destination) {
    console.log('🔍 开始过滤航班，只保留相关的直飞和甩尾航班');
    console.log(`搜索路线: ${searchParams.origin} → ${searchParams.destination}`);
    
    const originalDirectCount = directFlights.length;
    const originalComboCount = comboDeals.length;
    
    directFlights = filterRelevantFlights(directFlights, searchParams.origin, searchParams.destination);
    comboDeals = filterRelevantFlights(comboDeals, searchParams.origin, searchParams.destination);
    
    console.log('📊 过滤结果:');
    console.log(`  直飞航班: ${originalDirectCount} → ${directFlights.length}`);
    console.log(`  组合航班: ${originalComboCount} → ${comboDeals.length}`);
    console.log(`  总计: ${originalDirectCount + originalComboCount} → ${directFlights.length + comboDeals.length}`);
    
    // 诊断：检查过滤后的甩尾票
    const filteredThrowawayFlights = [...directFlights, ...comboDeals].filter(f => f.is_hidden_city || f.is_throwaway_deal);
    console.log(`  过滤后甩尾票数: ${filteredThrowawayFlights.length}`);
  }

  const adaptedResponse: V1CompatibleResponse = {
    search_id: v2Response.search_id,
    direct_flights: directFlights,
    combo_deals: comboDeals,
    disclaimers: v2Response.disclaimers,
    probe_details: v2Response.probe_details
  };

  console.log('✅ V2实际到V1适配完成');
  console.log('适配后数据:', {
    search_id: adaptedResponse.search_id,
    direct_flights_count: adaptedResponse.direct_flights.length,
    combo_deals_count: adaptedResponse.combo_deals.length,
    disclaimers_count: adaptedResponse.disclaimers.length
  });

  return adaptedResponse;
}

/**
 * 修复后的V2 API调用包装器
 */
export async function callV2SearchAPIFixed(payload: Record<string, unknown>): Promise<V1CompatibleResponse> {
  console.log('🚀 调用修复后的V2航班搜索API');
  console.log('请求payload:', payload);
  
  try {
    // 使用正确的后端地址
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

    const v2Response: V2ActualResponse = await response.json();
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
    
    // 提取搜索参数用于过滤
    const searchParams = {
      origin: payload.origin_iata as string,
      destination: payload.destination_iata as string
    };
    
    // 适配为V1格式，并应用过滤
    const adaptedResponse = adaptV2ActualResponseToV1(v2Response, searchParams);
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