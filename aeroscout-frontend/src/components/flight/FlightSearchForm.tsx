'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useForm, Controller, SubmitHandler } from 'react-hook-form';
import { useRouter } from 'next/navigation';
import AirportSelector from '@/components/airport/AirportSelector';
import { searchSimplifiedFlights, SimplifiedFlightSearchRequest } from '@/lib/apiService';
import { useFlightResultsStore, FlightData } from '@/store/flightResultsStore';
// 导入自定义组件
import Button from '@/components/common/Button';
import Input from '@/components/common/Input';
import FlightSearchLoader from '@/components/common/FlightSearchLoader';
import { adaptSimplifiedFlightResponse } from '@/lib/simplifiedApiAdapter';

// 定义简化的表单数据类型
interface SimplifiedFlightSearchFormData {
  originIata: string;
  destinationIata: string;
  departureDate: string;
  returnDate?: string;
  tripType: 'one-way' | 'round-trip';
  adults: number;
  children: number;
  infants: number;
  cabinClass: 'ECONOMY' | 'PREMIUM_ECONOMY' | 'BUSINESS' | 'FIRST';
  directFlightsOnly: boolean;
  enableHubProbe: boolean;
}

// 定义机场信息接口（兼容AirportSelector）
interface AirportInfo {
  code: string;
  name: string;
  city: string;
  country: string;
  type: string; // 必需字段以兼容apiService的AirportInfo
}

const FlightSearchForm: React.FC = () => {
  // 获取当前日期和一年后的日期，用于日期选择器的限制
  const today = new Date().toISOString().split('T')[0];
  const oneYearLater = new Date();
  oneYearLater.setFullYear(oneYearLater.getFullYear() + 1);
  const maxDate = oneYearLater.toISOString().split('T')[0];

  // 使用react-hook-form管理表单状态
  const {
    control,
    handleSubmit,
    setValue,
    watch,
    clearErrors,
    formState: { errors },
  } = useForm<SimplifiedFlightSearchFormData>({
    defaultValues: {
      originIata: '',
      destinationIata: '',
      departureDate: today,
      returnDate: '',
      tripType: 'one-way',
      adults: 1,
      children: 0,
      infants: 0,
      cabinClass: 'ECONOMY',
      directFlightsOnly: false,
      enableHubProbe: true,
    },
  });

  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);
  const tripType = watch('tripType');
  const departureDate = watch('departureDate');
  const originIata = watch('originIata');
  const destinationIata = watch('destinationIata');

  // 从 Zustand store 获取状态和 actions
  const {
    searchStatus,
    setSearchSuccess,
    setSearchError,
    setSearchLoading,
  } = useFlightResultsStore();

  const router = useRouter();
  const [formSubmitError, setFormSubmitError] = useState<string | null>(null);

  // 使用useState来存储完整的机场信息对象
  const [selectedOriginAirportInfo, setSelectedOriginAirportInfo] = useState<AirportInfo | null>(null);
  const [selectedDestinationAirportInfo, setSelectedDestinationAirportInfo] = useState<AirportInfo | null>(null);

  // 监听表单渲染，记录状态变化，用于调试
  useEffect(() => {
    console.log("FlightSearchForm RENDER: originIata =", originIata, "selectedOriginAirportInfo =", selectedOriginAirportInfo);
    console.log("FlightSearchForm RENDER: destinationIata =", destinationIata, "selectedDestinationAirportInfo =", selectedDestinationAirportInfo);
  });

  // 出发地机场选择处理函数
  const handleOriginAirportSelected = useCallback((airport: AirportInfo | null) => {
    console.log('[FlightSearchForm] handleOriginAirportSelected - airport:', airport);
    console.log("出发地机场选择:", airport);

    setSelectedOriginAirportInfo(airport);

    if (airport && airport.code) {
      console.log("设置出发地IATA:", airport.code);
      setValue('originIata', airport.code, {
        shouldValidate: true,
        shouldDirty: true,
        shouldTouch: true
      });
      clearErrors('originIata');
    } else {
      console.log("清空出发地IATA");
      setValue('originIata', '', { shouldValidate: true });
    }
  }, [setValue, clearErrors]);

  // 目的地机场选择处理函数
  const handleDestinationAirportSelected = useCallback((airport: AirportInfo | null) => {
    console.log('[FlightSearchForm] handleDestinationAirportSelected - airport:', airport);
    console.log("目的地机场选择:", airport);

    setSelectedDestinationAirportInfo(airport);

    if (airport && airport.code) {
      console.log("设置目的地IATA:", airport.code);
      setValue('destinationIata', airport.code, {
        shouldValidate: true,
        shouldDirty: true,
        shouldTouch: true
      });
      clearErrors('destinationIata');
    } else {
      console.log("清空目的地IATA");
      setValue('destinationIata', '', { shouldValidate: true });
    }
  }, [setValue, clearErrors]);

  const onSubmit: SubmitHandler<SimplifiedFlightSearchFormData> = async (data) => {
    console.log('🚀 [DEBUG] 开始搜索 - 立即设置loading状态');
    setFormSubmitError(null);

    // 立即设置loading状态，确保加载动画立即显示
    setSearchLoading();

    // 映射 cabinClass 到 GraphQL API 期望的值
    let apiCabinClass = data.cabinClass;
    switch (data.cabinClass) {
      case 'BUSINESS':
        apiCabinClass = 'BUSINESS';  // API期望BUSINESS而不是BUSINESS_CLASS
        break;
      case 'FIRST':
        apiCabinClass = 'FIRST';  // API期望FIRST而不是FIRST_CLASS
        break;
      // ECONOMY 和 PREMIUM_ECONOMY 通常保持不变，但需根据API确认
      // case 'PREMIUM_ECONOMY':
      //   apiCabinClass = 'PREMIUM_ECONOMY'; // 假设API使用此值
      //   break;
      default:
        apiCabinClass = data.cabinClass; // 保持原样或默认为 ECONOMY
    }
    console.log(`[FlightSearchForm] Mapped cabinClass from ${data.cabinClass} to ${apiCabinClass}`);

    const payload: SimplifiedFlightSearchRequest = {
      origin_iata: data.originIata,
      destination_iata: data.destinationIata,
      departure_date_from: data.departureDate,
      departure_date_to: data.departureDate,
      return_date_from: data.returnDate || undefined,
      return_date_to: data.returnDate || undefined,
      adults: data.adults,
      cabin_class: apiCabinClass, // 使用映射后的值
      preferred_currency: 'CNY',
      max_results_per_type: 10,
      max_pages_per_search: 1,
      direct_flights_only_for_primary: data.directFlightsOnly,
    };

    try {
      console.log('🚀 提交简化航班搜索请求:', payload);
      console.log('🔄 [DEBUG] 当前搜索状态:', searchStatus);

      // 调用简化航班搜索API
      const response = await searchSimplifiedFlights(
        payload,
        true, // 包含直飞航班
        data.enableHubProbe // 根据用户设置决定是否包含隐藏城市航班
      );

      console.log('✅ 简化API响应:', response);
      console.log('🔍 [DEBUG] 隐藏城市航班原始数据:', response.hidden_city_flights);

      if (response) {
        // 使用适配器转换响应数据
        const flightData: FlightData = adaptSimplifiedFlightResponse(response);

        console.log('=== 🎯 简化航班搜索成功 ===');
        console.log('📋 原始响应:', response);
        console.log('✈️ 处理后数据:', flightData);
        console.log('🔢 直飞航班数量:', flightData.directFlights?.length || 0);
        console.log('🔢 隐藏城市航班数量:', flightData.comboDeals?.length || 0);
        console.log('📝 免责声明数量:', flightData.disclaimers?.length || 0);
        console.log('⏱️ 搜索耗时:', response.search_time_ms, 'ms');

        // 详细检查隐藏城市航班数据
        if (response.hidden_city_flights && response.hidden_city_flights.length > 0) {
          console.log('🎯 [DEBUG] 第一个隐藏城市航班详情:');
          console.log('- ID:', response.hidden_city_flights[0].id);
          console.log('- 价格:', response.hidden_city_flights[0].price);
          console.log('- 隐藏目的地:', response.hidden_city_flights[0].hidden_destination);
          console.log('- 是否隐藏城市:', response.hidden_city_flights[0].is_hidden_city);
        }

        // 检查适配后的数据
        if (flightData.comboDeals && flightData.comboDeals.length > 0) {
          console.log('🎯 [DEBUG] 适配后第一个组合航班详情:');
          console.log('- ID:', flightData.comboDeals[0].id);
          console.log('- 价格:', flightData.comboDeals[0].price);
          console.log('- 隐藏目的地:', flightData.comboDeals[0].hiddenDestination);
          console.log('- 是否隐藏城市:', flightData.comboDeals[0].isHiddenCity);
        }

        setSearchSuccess(flightData, true);

        console.log('🧭 导航到结果页面:', flightData);
        router.push('/search/results');
      } else {
        setFormSubmitError('未能获取搜索结果，响应格式不正确。');
        setSearchError('未能获取搜索结果，响应格式不正确。');
      }
    } catch (error) {
      console.error('❌ 简化航班搜索错误:', error);
      console.log('🔄 [DEBUG] 错误后的搜索状态:', searchStatus);
      setFormSubmitError(`搜索失败: ${error instanceof Error ? error.message : '未知错误'}`);
      setSearchError(`搜索失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  };

  // 记录组件挂载和卸载
  useEffect(() => {
    console.log('🚀 FlightSearchForm组件挂载 (简化搜索版本)');

    return () => {
      console.log('👋 FlightSearchForm组件卸载');
    };
  }, []);

  return (
    <div className="w-full bg-white rounded-lg shadow-lg overflow-visible animate-fadeIn">
      {/* 顶部简化搜索提示 */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-blue-600 text-sm font-medium">
              🚀 AeroScout 简化搜索
            </span>
            <span className="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full">
              直飞 + 隐藏城市
            </span>
          </div>
          <div className="text-xs text-blue-600">
            快速搜索 • 智能推荐 • 风险提示
          </div>
        </div>
      </div>

      {/* 单程/往返选择 */}
      <div className="bg-gradient-to-r from-orange-50 to-white px-6 py-3">
        <div className="flex space-x-4">
          <Controller
            name="tripType"
            control={control}
            render={({ field }) => (
              <div className="flex space-x-8">
                <label className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    className="sr-only"
                    checked={field.value === 'one-way'}
                    onChange={() => field.onChange('one-way')}
                  />
                  <div className={`text-sm font-medium pb-2 border-b-2 transition-all ${field.value === 'one-way' ? 'text-orange-500 border-orange-500' : 'text-gray-400 border-transparent'}`}>
                    单程
                  </div>
                </label>
                <label className="flex items-center cursor-pointer">
                  <input
                    type="radio"
                    className="sr-only"
                    checked={field.value === 'round-trip'}
                    onChange={() => field.onChange('round-trip')}
                  />
                  <div className={`text-sm font-medium pb-2 border-b-2 transition-all ${field.value === 'round-trip' ? 'text-orange-500 border-orange-500' : 'text-gray-400 border-transparent'}`}>
                    往返
                  </div>
                </label>
              </div>
            )}
          />
        </div>
      </div>

      {/* 主搜索表单 */}
      <form onSubmit={handleSubmit(onSubmit)} className="p-6 overflow-visible">
        {formSubmitError && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            <strong>错误：</strong> {formSubmitError}
          </div>
        )}

        <div className="flex flex-col lg:flex-row lg:items-end lg:space-x-4 overflow-visible">
          {/* 出发地/目的地 */}
          <div className="flex-1 mb-4 lg:mb-0 overflow-visible">
            <Controller
              name="originIata"
              control={control}
              rules={{ required: '出发地不能为空' }}
              render={({ fieldState }) => (
                <AirportSelector
                  label="出发地"
                  placeholder="搜索出发机场或城市..."
                  value={selectedOriginAirportInfo}
                  onAirportSelected={handleOriginAirportSelected}
                  error={fieldState.error?.message}
                />
              )}
            />
          </div>

          <div className="hidden lg:block flex-none">
            <div className="w-8 h-8 flex items-center justify-center mb-1.5">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" className="w-5 h-5 text-gray-400">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </div>
          </div>

          <div className="flex-1 mb-4 lg:mb-0 overflow-visible">
            <Controller
              name="destinationIata"
              control={control}
              rules={{ required: '目的地不能为空' }}
              render={({ fieldState }) => (
                <AirportSelector
                  label="目的地"
                  placeholder="搜索目的地机场或城市..."
                  value={selectedDestinationAirportInfo}
                  onAirportSelected={handleDestinationAirportSelected}
                  error={fieldState.error?.message}
                />
              )}
            />
          </div>

          {/* 日期选择 */}
          <div className="flex-1 mb-4 lg:mb-0">
            <Controller
              name="departureDate"
              control={control}
              render={({ field }) => (
                <Input
                  type="date"
                  id="departureDate"
                  label="出发日期"
                  variant="filled"
                  min={today}
                  max={maxDate}
                  {...field}
                  error={errors.departureDate?.message}
                  className="rounded-lg"
                  onChange={(e) => {
                    field.onChange(e);
                    const returnDate = watch('returnDate');
                    if (tripType === 'round-trip' && returnDate && new Date(e.target.value) > new Date(returnDate)) {
                      setValue('returnDate', e.target.value, { shouldValidate: true });
                    }
                  }}
                />
              )}
            />
          </div>

          {tripType === 'round-trip' && (
            <div className="flex-1 mb-4 lg:mb-0 animate-fadeIn">
              <Controller
                name="returnDate"
                control={control}
                render={({ field }) => (
                  <Input
                    type="date"
                    id="returnDate"
                    label="返程日期"
                    variant="filled"
                    min={departureDate || today}
                    max={maxDate}
                    {...field}
                    error={errors.returnDate?.message}
                    className="rounded-lg"
                  />
                )}
              />
            </div>
          )}

          {/* 乘客数量选择 */}
          <div className="flex-1 mb-4 lg:mb-0">
            <Controller
              name="adults"
              control={control}
              render={({ field }) => (
                <div>
                  <label htmlFor="adults" className="block text-sm font-medium text-gray-700 mb-1.5">
                    乘客
                  </label>
                  <div className="flex items-center px-4 py-2.5 bg-gray-50 rounded-lg">
                    <button
                      type="button"
                      onClick={() => field.value > 1 && field.onChange(field.value - 1)}
                      className="w-8 h-8 flex items-center justify-center text-gray-600 hover:bg-gray-200 rounded-full transition-colors"
                      disabled={field.value <= 1}
                      aria-label="减少乘客数量"
                    >
                      <svg className="w-5 h-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                      </svg>
                    </button>
                    <span className="flex-1 text-center text-sm text-gray-900 font-medium mx-2">
                      {field.value}位成人
                    </span>
                    <button
                      type="button"
                      onClick={() => field.value < 9 && field.onChange(field.value + 1)}
                      className="w-8 h-8 flex items-center justify-center text-gray-600 hover:bg-gray-200 rounded-full transition-colors"
                      disabled={field.value >= 9}
                      aria-label="增加乘客数量"
                    >
                      <svg className="w-5 h-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                      </svg>
                    </button>
                    <input
                      type="hidden"
                      id="adults"
                      {...field}
                    />
                  </div>
                  {errors.adults && <p className="text-red-500 text-xs mt-1">{errors.adults.message}</p>}
                </div>
              )}
            />
          </div>

          {/* 搜索按钮 */}
          <div className="flex-none">
            <Button
              type="submit"
              disabled={searchStatus === 'loading'}
              isLoading={searchStatus === 'loading'}
              size="lg"
              className="w-full lg:w-auto mt-6 lg:mt-0 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg px-8 shadow-lg"
            >
              {searchStatus === 'loading' ? '🔍 搜索中...' : '🚀 开始搜索'}
            </Button>
          </div>
        </div>

        {/* 高级选项 */}
        <div className="mt-6 border-t border-gray-200 pt-4">
          <div className="flex justify-between items-center">
            <div className="flex space-x-6">
              <Controller
                name="cabinClass"
                control={control}
                render={({ field }) => (
                  <div className="flex items-center space-x-2">
                    <label htmlFor="cabinClass" className="text-sm font-medium text-gray-700">
                      舱位等级
                    </label>
                    <select
                      id="cabinClass"
                      {...field}
                      className="text-sm border border-gray-300 rounded-md px-3 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="ECONOMY">经济舱</option>
                      <option value="PREMIUM_ECONOMY">超级经济舱</option>
                      <option value="BUSINESS">商务舱</option>
                      <option value="FIRST">头等舱</option>
                    </select>
                  </div>
                )}
              />
              <label className="flex items-center space-x-2 cursor-pointer">
                <Controller
                  name="directFlightsOnly"
                  control={control}
                  render={({ field: { onChange, value } }) => (
                    <input
                      type="checkbox"
                      checked={value}
                      onChange={onChange}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                  )}
                />
                <span className="text-sm text-gray-700">仅直飞</span>
              </label>
            </div>
            <Button
              type="button"
              variant="link"
              size="sm"
              onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}
              className="text-blue-600 hover:text-blue-700"
            >
              {showAdvancedOptions ? '收起选项' : '更多选项'}
            </Button>
          </div>

          {showAdvancedOptions && (
            <div className="mt-4 p-4 bg-blue-50 rounded-lg animate-fadeIn">
              <label className="flex items-center space-x-3 cursor-pointer">
                <Controller
                  name="enableHubProbe"
                  control={control}
                  render={({ field: { onChange, value } }) => (
                    <input
                      type="checkbox"
                      checked={value}
                      onChange={onChange}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                  )}
                />
                <div>
                  <span className="text-sm font-medium text-gray-900">启用隐藏城市航班搜索</span>
                  <p className="text-xs text-gray-600 mt-1">
                    搜索可能更便宜的隐藏城市航班（甩尾票），但存在一定风险
                  </p>
                </div>
              </label>
            </div>
          )}
        </div>

        {/* 搜索状态指示器 */}
        {searchStatus === 'loading' && (
          <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200 animate-fadeIn">
            <div className="flex items-center">
              <div className="w-10 h-10 mr-4 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center shadow-sm">
                <svg className="animate-spin w-5 h-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
              <div>
                <p className="text-blue-800 font-medium">正在搜索航班...</p>
                <p className="text-blue-600 text-sm">使用简化搜索引擎，为您快速查找最优航班</p>
              </div>
            </div>
          </div>
        )}
      </form>

      {/* 全屏加载遮罩 */}
      <FlightSearchLoader
        isVisible={searchStatus === 'loading'}
        searchParams={{
          origin: selectedOriginAirportInfo?.name || originIata,
          destination: selectedDestinationAirportInfo?.name || destinationIata,
          departureDate: departureDate,
        }}
      />
    </div>
  );
};

export default FlightSearchForm;