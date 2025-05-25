'use client';

import React, { useState } from 'react';
import Image from 'next/image';
import { FlightItinerary } from '@/store/flightResultsStore';
import { Card } from '@/components/common/Card';
import RiskConfirmationModal from '@/components/common/RiskConfirmationModal';

// FlightCard Component - Enhanced for UI/UX
const FlightCard: React.FC<{ itinerary: FlightItinerary, isComboDeal?: boolean }> = ({ itinerary, isComboDeal }) => {
  const [showDetails, setShowDetails] = useState(false);
  const [showRiskModal, setShowRiskModal] = useState(false);
  const firstSegment = itinerary.segments?.[0];
  const airlineLogoUrl = firstSegment?.airlineLogoUrl;
  const lastSegment = itinerary.segments?.[itinerary.segments.length - 1];

  const airlineName = firstSegment?.airlineName || '航空公司';
  const airlinesList = itinerary.airlines?.map(a => a.name).join(', ') || airlineName; // Display list or fallback to first segment airline

  const formatTime = (timeStr: string | undefined) => {
    if (!timeStr) return 'N/A';
    return new Date(timeStr).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', hour12: false });
  };

  const formatDate = (timeStr: string | undefined) => {
    if (!timeStr) return '';
    return new Date(timeStr).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
  };

  const departureTime = formatTime(firstSegment?.departureTime);
  const departureDate = formatDate(firstSegment?.departureTime);
  const arrivalTime = formatTime(lastSegment?.arrivalTime);
  const arrivalDate = formatDate(lastSegment?.arrivalTime);

  const formatDuration = (minutes: number | undefined): string => {
    if (minutes === undefined || minutes === null || isNaN(minutes) || minutes <= 0) {
      return 'N/A';
    }
    const h = Math.floor(minutes / 60);
    const m = minutes % 60;
    return `${h}小时${m > 0 ? ` ${m}分钟` : ''}`;
  };

  // Use itinerary.totalTravelTime if available, otherwise fallback to totalDurationMinutes
  const totalTravelTimeDisplay = itinerary.totalTravelTime || formatDuration(itinerary.totalDurationMinutes);

  const departureAirportCode = firstSegment?.departureAirportCode || 'N/A';
  const departureAirportFull = firstSegment?.departureAirportFull || firstSegment?.departureAirportName || '出发机场';
  const departureCityName = firstSegment?.departureCityName || '';

  const arrivalAirportCode = lastSegment?.arrivalAirportCode || 'N/A';
  const arrivalAirportFull = lastSegment?.arrivalAirportFull || lastSegment?.arrivalAirportName || '到达机场';
  const arrivalCityName = lastSegment?.arrivalCityName || '';

  // 根据货币代码获取货币符号和格式化规则
  const formatPrice = (amount: number | undefined, currency: string): string => {
    console.log('💰 格式化价格 - amount:', amount, '(类型:', typeof amount, '), currency:', currency);

    // 增强价格验证
    if (amount === null || amount === undefined) {
      console.warn('⚠️ 价格为null/undefined，显示默认文本');
      return '价格待定';
    }

    if (typeof amount !== 'number') {
      console.warn('⚠️ 价格类型不是number:', typeof amount, amount, '显示默认文本');
      return '价格待定';
    }

    if (isNaN(amount)) {
      console.warn('⚠️ 价格为NaN，显示默认文本');
      return '价格待定';
    }

    if (amount <= 0) {
      console.warn('⚠️ 价格为零或负数:', amount, '显示默认文本');
      return '价格待定';
    }

    // 针对不同货币的格式化规则
    const normalizedCurrency = currency.toUpperCase();
    let formattedPrice: string;

    switch (normalizedCurrency) {
      case 'CNY':
        // 人民币：使用中文数字格式，千位分隔符
        formattedPrice = `¥${amount.toLocaleString('zh-CN', {
          minimumFractionDigits: 0,
          maximumFractionDigits: 0
        })}`;
        break;
      case 'USD':
        formattedPrice = `$${amount.toLocaleString('en-US', {
          minimumFractionDigits: 0,
          maximumFractionDigits: 0
        })}`;
        break;
      case 'EUR':
        formattedPrice = `€${amount.toLocaleString('de-DE', {
          minimumFractionDigits: 0,
          maximumFractionDigits: 0
        })}`;
        break;
      case 'GBP':
        formattedPrice = `£${amount.toLocaleString('en-GB', {
          minimumFractionDigits: 0,
          maximumFractionDigits: 0
        })}`;
        break;
      case 'JPY':
        formattedPrice = `¥${amount.toLocaleString('ja-JP', {
          minimumFractionDigits: 0,
          maximumFractionDigits: 0
        })}`;
        break;
      default:
        formattedPrice = `${normalizedCurrency} ${amount.toLocaleString()}`;
        break;
    }

    console.log('✅ 价格格式化完成:', formattedPrice);
    return formattedPrice;
  };

  // 获取货币名称用于无障碍访问
  const getCurrencyName = (currency: string): string => {
    switch (currency.toUpperCase()) {
      case 'CNY': return '人民币';
      case 'USD': return '美元';
      case 'EUR': return '欧元';
      case 'GBP': return '英镑';
      case 'JPY': return '日元';
      default: return currency.toUpperCase();
    }
  };

  // 添加价格调试信息
  console.log('🎯 FlightCard价格调试 - itinerary.price:', itinerary.price);
  console.log('🎯 价格金额:', itinerary.price?.amount);
  console.log('🎯 价格货币:', itinerary.price?.currency);

  const price = formatPrice(itinerary.price?.amount, itinerary.price?.currency || 'CNY');
  const currencyName = getCurrencyName(itinerary.price?.currency || 'CNY');

  console.log('🎯 最终显示价格:', price);
  console.log('🎯 货币名称:', currencyName);
  const numStops = itinerary.segments?.length ? itinerary.segments.length - 1 : 0;

  // 🔍 添加调试日志来诊断中转显示问题
  console.log('🔍 FlightCard中转诊断 - 航班ID:', itinerary.id);
  console.log('🔍 航段数量:', itinerary.segments?.length);
  console.log('🔍 计算的中转次数:', numStops);
  console.log('🔍 isDirectFlight字段:', itinerary.isDirectFlight);
  console.log('🔍 isHiddenCity字段:', itinerary.isHiddenCity);
  console.log('🔍 hiddenDestination:', itinerary.hiddenDestination);
  console.log('🔍 航段详情:', itinerary.segments?.map(s => ({
    from: `${s.departureCityName}(${s.departureAirportCode})`,
    to: `${s.arrivalCityName}(${s.arrivalAirportCode})`,
    flight: s.flightNumber
  })));
  console.log('🔍 中转信息:', itinerary.transfers);

  // 🔧 修复中转显示逻辑，正确处理隐藏城市航班
  let stopsDisplay: string;
  if (itinerary.isHiddenCity && itinerary.hiddenDestination) {
    // 隐藏城市航班：显示中转城市信息
    const transferCity = itinerary.segments?.[0]?.arrivalCityName || '未知城市';
    stopsDisplay = `中转${transferCity}`;
  } else if (itinerary.isDirectFlight || numStops === 0) {
    stopsDisplay = '直飞';
  } else {
    stopsDisplay = `${numStops}次中转`;
  }

  // 🔍 添加最终显示结果的日志
  console.log('🔍 最终显示的中转信息:', stopsDisplay);

  // Stop cities for display, now using segment.arrivalCityName
  const stopCities = numStops > 0
    ? itinerary.segments?.slice(0, -1).map(seg => seg.arrivalCityName || '未知中转城市').join(', ')
    : '';

  // Handle booking click
  const handleBookingClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    // 记录点击事件
    console.log(`预订点击: ${itinerary.id || '未知ID'}`);

    // 如果是探测特惠，显示风险确认模态框
    if (itinerary.isProbeSuggestion) {
      e.preventDefault();
      setShowRiskModal(true);
      return false;
    }
  };

  // Handle risk confirmation
  const handleRiskConfirm = () => {
    setShowRiskModal(false);
    // 打开预订链接
    if (itinerary.deepLink) {
      window.open(itinerary.deepLink, '_blank');
    }
  };

  return (
    <>
      <Card
        className={`mb-5 hover:shadow-apple transition-apple group ${
          itinerary.isProbeSuggestion
            ? 'border-2 border-[#FF9500] bg-[#FFF8E6] shadow-[0_0_0_1px_rgba(255,149,0,0.2)]'
            : isComboDeal
              ? 'border-2 border-[#AF52DE] bg-[#F2E8FF] shadow-[0_0_0_1px_rgba(175,82,222,0.2)]'
              : ''
        }`}
        hoverable
        role="article"
        aria-label={`${firstSegment?.airlineName || '航空公司'} 航班，从 ${departureCityName || departureAirportCode} 到 ${arrivalCityName || arrivalAirportCode}，${price} ${currencyName}`}
      >
      {/* Header: Airline Info & Price */}
      <div className="flex justify-between items-start mb-6">
        <div className="flex items-center">
          {airlineLogoUrl ? (
            <Image
              src={airlineLogoUrl}
              alt={`${firstSegment?.airlineName || '航空公司'} 标志`}
              width={48}
              height={48}
              className="mr-3 rounded-lg object-contain border border-[#E6E6E6]"
              unoptimized={true} // 外部 URL，不进行优化
            />
          ) : (
            <div className="h-12 w-12 mr-3 bg-[#F5F5F7] rounded-lg flex items-center justify-center text-lg font-medium text-[#86868B] border border-[#E6E6E6]" aria-hidden="true">
              {(firstSegment?.airlineName || 'A').substring(0, 1)}
            </div>
          )}
          <div>
            <span className="font-semibold text-lg text-[#1D1D1F] block" title={airlinesList}>
              {itinerary.airlines && itinerary.airlines.length > 1 ? `${firstSegment?.airlineName} 等多家` : firstSegment?.airlineName || '航空公司'}
            </span>
            <span className="text-xs text-[#86868B]">{firstSegment?.flightNumber} {firstSegment?.equipment && `(${firstSegment.equipment})`}</span>
            {itinerary.airlines && itinerary.airlines.length > 1 && (
              <div className="flex items-center mt-1">
                <div className="flex -space-x-2" title={airlinesList}>
                  {itinerary.airlines.slice(0, 4).map((airline, index) => (
                    <div
                      key={`airline-logo-${airline.code}-${index}`}
                      className="w-6 h-6 rounded-full border border-white overflow-hidden bg-white shadow-sm"
                      title={`${airline.name} (${airline.code})`}
                    >
                      {airline.logoUrl ? (
                        <Image
                          src={airline.logoUrl}
                          alt={`${airline.name} logo`}
                          width={24}
                          height={24}
                          className="object-contain"
                          unoptimized={true}
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center bg-[#F5F5F7] text-[9px] font-medium">
                          {airline.code}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
                {itinerary.airlines.length > 4 && (
                  <span className="text-xs text-[#86868B] ml-2" title={`其他航司: ${itinerary.airlines.slice(4).map(a => a.name).join(', ')}`}>
                    +{itinerary.airlines.length - 4}
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
        <div className="text-right">
          <div className="flex items-center justify-end gap-2">
            <span className="text-2xl font-bold text-[#2997FF] group-hover:text-[#0077ED] transition-colors" aria-label={`价格: ${price} ${currencyName}`}>{price}</span>
            {/* 货币标识 */}
            <div className="flex flex-col items-center">
              <span className="text-xs text-[#86868B] bg-[#F5F5F7] px-1.5 py-0.5 rounded-full font-medium">
                {currencyName}
              </span>
            </div>
          </div>
          {itinerary.isProbeSuggestion && (
            <>
              <span className="block text-xs bg-[#FFF8E6] text-[#FF9500] px-2 py-1 rounded-full mt-1 font-medium flex items-center justify-center" role="status">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                探测特惠
              </span>
              {itinerary.probeHub && (
                <span className="block text-xs text-[#FF9500] mt-0.5">
                  经 {itinerary.probeHub} 探测
                </span>
              )}
            </>
          )}
          {!itinerary.isProbeSuggestion && isComboDeal && (
            <span className="block text-xs bg-[#F2E8FF] text-[#9747FF] px-2 py-1 rounded-full mt-1 font-medium flex items-center justify-center" role="status">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              组合推荐
            </span>
          )}
          {/* 隐藏城市航班标识 */}
          {(itinerary.isHiddenCity || itinerary.isThrowawayDeal || itinerary.isTrueHiddenCity) && (
            <div className="mt-1">
              <span className="block text-xs bg-[#FFE5E5] text-[#FF3B30] px-2 py-1 rounded-full font-medium flex items-center justify-center" role="status">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                {itinerary.isTrueHiddenCity ? '隐藏城市航班' : '甩尾票'}
              </span>
              {itinerary.isTrueHiddenCity && (
                <span className="block text-xs text-[#FF3B30] mt-0.5">
                  请在目标城市下机，勿乘坐后续航段
                </span>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Body: Flight Details */}
      <div className="flex flex-col sm:flex-row items-center justify-between mb-4 gap-4">
        {/* Mobile View: Departure & Arrival Side by Side */}
        <div className="flex justify-between w-full sm:hidden mb-2">
          {/* Departure - Mobile */}
          <div className="flex flex-col items-start">
            <p className="text-xl font-medium text-[#1D1D1F]">{departureTime}</p>
            <div className="flex items-center">
              <p className="text-sm font-medium text-[#1D1D1F]" title={departureAirportFull}>{departureAirportCode}</p>
              <p className="text-xs text-[#86868B] ml-1">({departureCityName})</p>
            </div>
            <p className="text-xs text-[#86868B]">{departureDate}</p>
          </div>

          {/* Duration & Stops - Mobile */}
          <div className="flex flex-col items-center justify-center px-2">
            <p className="text-xs text-[#86868B]">{totalTravelTimeDisplay}</p>
            <div className="w-16 sm:w-24 border-t border-[#D1D1D6] my-1"></div>
            <span className={`text-xs font-medium ${
              numStops === 0
                ? 'text-[#34C759]'
                : numStops === 1
                  ? 'text-[#FF9500]'
                  : 'text-[#FF3B30]'
            }`}>
              {stopsDisplay}
            </span>
          </div>

          {/* Arrival - Mobile */}
          <div className="flex flex-col items-end">
            <p className="text-xl font-medium text-[#1D1D1F]">{arrivalTime}</p>
            <div className="flex items-center">
              <p className="text-xs text-[#86868B] mr-1">({arrivalCityName})</p>
              <p className="text-sm font-medium text-[#1D1D1F]" title={arrivalAirportFull}>{arrivalAirportCode}</p>
            </div>
            <p className="text-xs text-[#86868B]">{arrivalDate}</p>
            {/* 隐藏目的地信息显示在到达时间下方 - 移动端 */}
            {(itinerary.isHiddenCity || itinerary.isThrowawayDeal || itinerary.isTrueHiddenCity) && itinerary.hiddenDestination && (
              <p className="text-xs text-[#FF3B30] mt-1 font-medium text-right">
                {itinerary.hiddenDestination.cityName}
              </p>
            )}
          </div>
        </div>

        {/* Desktop View: Departure */}
        <div className="hidden sm:flex sm:flex-col sm:items-start w-full sm:w-auto">
          <p className="text-3xl font-medium text-[#1D1D1F]">{departureTime}</p>
          <p className="text-sm text-[#86868B]" title={departureAirportFull}>{departureAirportCode}</p>
          <p className="text-xs text-[#86868B]">{departureDate}</p>
          <p className="text-xs text-[#86868B] mt-1">{departureCityName}</p>
        </div>

        {/* Journey Info: Duration & Stops - Desktop */}
        <div className="flex-grow text-center w-full sm:w-auto px-2 sm:px-6 order-first sm:order-none">
          {/* Only show on desktop */}
          <p className="hidden sm:block text-sm text-[#86868B] mb-1">{totalTravelTimeDisplay}</p>
          <div className="hidden sm:block relative my-2">
            <div className="absolute inset-0 flex items-center" aria-hidden="true">
              <div className="w-full border-t border-[#D1D1D6] group-hover:border-[#A1A1A6] transition-apple"></div>
            </div>
            <div className="relative flex justify-center">
              <span className={`bg-white px-3 text-sm font-medium ${
                numStops === 0
                  ? 'text-[#34C759]'
                  : numStops === 1
                    ? 'text-[#FF9500]'
                    : 'text-[#FF3B30]'
              }`}>
                {stopsDisplay}
              </span>
            </div>
          </div>

          {/* Enhanced Transfer Details from segments - Both Mobile & Desktop */}
          {itinerary.segments && itinerary.segments.length > 1 && (
            <div className="text-xs text-[#86868B] mt-1 space-y-0.5 w-full">
              {itinerary.transfers?.map((transfer, idx) => {
                const segment = itinerary.segments[idx];
                const layoverDurationMinutes = transfer.durationMinutes;

                return (
                <div key={`layover-${segment?.id || idx}`}
                  className="flex flex-col mb-2 bg-[#F5F5F7] p-2 rounded-apple"
                  title={`中转于 ${transfer.city || '未知城市'}, 时长 ${formatDuration(layoverDurationMinutes)}${
                    transfer.isDifferentAirport ? ', 需换机场' : ''}${
                    transfer.isBaggageRecheck ? ', 需重新托运行李' : ''}${
                    transfer.isAirlineChange ? ', 需换航司' : ''}`}>

                  {/* 中转城市和时长 */}
                  <div className="flex flex-wrap items-center gap-1 mb-1">
                    <span className="inline-flex items-center">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 text-[#1D1D1F] mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      <span className="font-medium truncate max-w-[120px]">{transfer.city || segment?.arrivalCityName || '未知城市'}</span>
                    </span>
                    <span className="text-[#86868B]">·</span>
                    <span className={`flex items-center ${layoverDurationMinutes && layoverDurationMinutes < 60 ? 'text-[#FF3B30] font-medium' : layoverDurationMinutes && layoverDurationMinutes > 720 ? 'text-[#34C759] font-medium' : 'text-[#86868B]'}`}>
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {transfer.layoverTime || formatDuration(layoverDurationMinutes)}
                      {layoverDurationMinutes && layoverDurationMinutes < 60 ? ' (紧张)' :
                       layoverDurationMinutes && layoverDurationMinutes > 720 ? ' (长停留)' : ''}
                    </span>
                  </div>

                  {/* 中转详情 */}
                  <div className="flex flex-wrap gap-2 text-xs">
                    {transfer.isDifferentAirport && (
                      <span className="inline-flex items-center bg-[#FFF1F0] text-[#FF3B30] px-2 py-0.5 rounded-full">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 9l3 3m0 0l-3 3m3-3H8m13 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        需换机场
                        {transfer.airportChangeDetail && (
                          <span className="ml-1 font-medium">
                            {transfer.airportChangeDetail.fromAirportCode} → {transfer.airportChangeDetail.toAirportCode}
                          </span>
                        )}
                      </span>
                    )}

                    {transfer.isBaggageRecheck && (
                      <span className="inline-flex items-center bg-[#FFF8E6] text-[#FF9500] px-2 py-0.5 rounded-full">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                        </svg>
                        需重新托运行李
                      </span>
                    )}

                    {transfer.isAirlineChange && (
                      <span className="inline-flex items-center bg-[#F2E8FF] text-[#AF52DE] px-2 py-0.5 rounded-full">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 mr-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                        </svg>
                        需换航司
                        {transfer.fromAirline && transfer.toAirline && (
                          <span className="ml-1 font-medium">
                            {transfer.fromAirline.code} → {transfer.toAirline.code}
                          </span>
                        )}
                      </span>
                    )}
                  </div>
                </div>
              );
            })}
            </div>
          )}

          {/* Fallback for stopCities if detailed segment layovers are not available */}
          {(numStops > 0 && (!itinerary.segments || itinerary.segments.length <= 1 || !itinerary.segments.some(s => s.layoverDuration !== undefined)) && stopCities) && (
             <p className="text-xs text-[#86868B] truncate" title={`经停: ${stopCities}`}>
               经停: {stopCities}
             </p>
           )}
        </div>

        {/* Desktop View: Arrival */}
        <div className="hidden sm:flex sm:flex-col sm:items-end w-full sm:w-auto">
          <p className="text-3xl font-medium text-[#1D1D1F]">{arrivalTime}</p>
          <p className="text-sm text-[#86868B]" title={arrivalAirportFull}>{arrivalAirportCode}</p>
          <p className="text-xs text-[#86868B]">{arrivalDate}</p>
          <p className="text-xs text-[#86868B] mt-1">{arrivalCityName}</p>
          {/* 隐藏目的地信息显示在到达时间下方 */}
          {(itinerary.isHiddenCity || itinerary.isThrowawayDeal || itinerary.isTrueHiddenCity) && itinerary.hiddenDestination && (
            <p className="text-xs text-[#FF3B30] mt-1 font-medium">
              {itinerary.hiddenDestination.cityName}
            </p>
          )}
        </div>
      </div>

      {/* 探测组合风险提示 - 极其醒目 */}
      {itinerary.isProbeSuggestion && (
        <div className="mt-4 p-4 bg-[#FFF1F0] border-2 border-[#FF3B30] rounded-apple shadow-apple-sm animate-pulse-subtle">
          <div className="flex flex-col sm:flex-row items-start">
            <div className="h-10 w-10 bg-[#FF3B30] rounded-full flex items-center justify-center mb-3 sm:mb-0 sm:mr-3 flex-shrink-0 mx-auto sm:mx-0">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div>
              <p className="text-xl font-bold text-[#FF3B30] text-center sm:text-left">重要法律风险警告</p>
              <div className="mt-2 p-2 bg-white rounded-md border border-[#FF3B30]">
                <p className="text-sm font-medium text-[#1D1D1F] leading-relaxed">
                  {itinerary.probeDisclaimer || "此优惠可能依赖于您在特定中转点放弃后续行程（俗称\"跳机\"），这可能违反航空公司的运输条款。"}
                </p>
              </div>
              <p className="text-sm font-semibold text-[#FF3B30] mt-3">请注意以下法律风险：</p>
              <ul className="list-disc pl-5 mt-2 text-sm text-[#1D1D1F] space-y-2">
                <li className="font-medium">航空公司可能取消您的回程或后续航段</li>
                <li className="font-medium">可能影响您的常旅客积分和会员状态</li>
                <li className="font-medium">在某些情况下，航空公司可能要求补缴票价差额</li>
                <li className="font-medium">可能违反航空公司运输条款，导致法律纠纷</li>
              </ul>
              {itinerary.probeHub && (
                <div className="mt-3 p-3 bg-white rounded-md border-2 border-[#FF3B30] flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-[#FF3B30] mr-2 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-sm font-bold text-[#FF3B30] truncate">
                    探测枢纽: <strong>{itinerary.probeHub}</strong>
                    {itinerary.hiddenDestination && (
                      <span className="ml-1">（需在此下机）</span>
                    )}
                  </span>
                </div>
              )}
              <div className="mt-4 p-3 bg-[#FFFBEB] border border-[#F59E0B] rounded-md">
                <p className="text-sm font-medium text-[#B45309]">
                  预订此航班即表示您已完全了解并自愿接受相关风险。AeroScout不对因&quot;跳机&quot;行为导致的任何损失负责。
                </p>
              </div>
              <div className="mt-3 flex items-center justify-center">
                <input type="checkbox" id={`risk-acknowledge-${itinerary.id}`} className="h-4 w-4 text-[#FF3B30] border-[#FF3B30] rounded focus:ring-[#FF3B30]" />
                <label htmlFor={`risk-acknowledge-${itinerary.id}`} className="ml-2 block text-sm text-[#1D1D1F] font-medium">
                  我已阅读并理解上述风险警告
                </label>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 常规组合航班风险提示 (仅当不是探测组合时显示) */}
      {isComboDeal && !itinerary.isProbeSuggestion && (
        <div className="mt-4 p-4 bg-[#F2E8FF] border border-[#AF52DE] rounded-apple shadow-apple-sm">
          <div className="flex flex-col sm:flex-row items-start">
            <div className="h-7 w-7 bg-[#AF52DE] rounded-full flex items-center justify-center mb-3 sm:mb-0 sm:mr-3 flex-shrink-0 mx-auto sm:mx-0">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <p className="text-md font-semibold text-[#1D1D1F] text-center sm:text-left">组合航班提示</p>
              <p className="text-sm text-[#86868B] mt-1 leading-relaxed">
                此为系统智能组合的多段航班，非航空公司官方联程。请注意以下事项：
              </p>
              <ul className="list-disc pl-5 mt-2 text-sm text-[#86868B] space-y-1">
                <li>各航段需<strong>单独预订</strong>，可能需要多次付款</li>
                <li>如遇航班延误或取消，可能无法获得航空公司的免费改签或赔偿</li>
                <li>请确保各航段之间预留充足的转机时间</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* 甩尾票风险提示 */}
      {(itinerary.isHiddenCity || itinerary.isThrowawayDeal) && (
        <div className="mt-4 p-4 bg-[#FFF1F0] border-2 border-[#FF3B30] rounded-apple shadow-apple-sm">
          <div className="flex flex-col sm:flex-row items-start">
            <div className="h-8 w-8 bg-[#FF3B30] rounded-full flex items-center justify-center mb-3 sm:mb-0 sm:mr-3 flex-shrink-0 mx-auto sm:mx-0">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <div>
              <p className="text-lg font-bold text-[#FF3B30] text-center sm:text-left">甩尾票风险提示</p>
              <div className="mt-2 p-2 bg-white rounded-md border border-[#FF3B30]">
                <p className="text-sm font-medium text-[#1D1D1F] leading-relaxed">
                  {itinerary.isHiddenCity
                    ? `此票价利用了隐藏城市定价策略。${itinerary.hiddenDestination
                        ? `您需要在 ${itinerary.hiddenDestination.cityName} (${itinerary.hiddenDestination.code}) 下机，放弃后续航段。`
                        : "您需要在中转城市下机，放弃后续航段。"}`
                    : "此为甩尾票，您需要放弃部分航段。"}
                </p>
              </div>
              {itinerary.hiddenDestination && (
                <div className="mt-2 p-2 bg-[#FFE5E5] rounded-md">
                  <p className="text-sm font-semibold text-[#FF3B30]">
                    实际目的地：{itinerary.hiddenDestination.cityName} ({itinerary.hiddenDestination.code})
                  </p>
                  <p className="text-xs text-[#86868B] mt-1">
                    表面目的地：{lastSegment?.arrivalCityName || arrivalCityName} ({lastSegment?.arrivalAirportCode || arrivalAirportCode})
                  </p>
                </div>
              )}
              <p className="text-sm font-semibold text-[#FF3B30] mt-3">使用此类机票的风险：</p>
              <ul className="list-disc pl-5 mt-2 text-sm text-[#1D1D1F] space-y-2">
                <li className="font-medium">违反航空公司运输条款，可能导致法律纠纷</li>
                <li className="font-medium">航空公司可能取消您的回程或后续航段</li>
                <li className="font-medium">可能影响您的常旅客积分和会员状态</li>
                <li className="font-medium">托运行李将被送至最终目的地，无法在中转站取回</li>
                <li className="font-medium">航空公司可能要求补缴票价差额</li>
              </ul>
              <div className="mt-4 p-3 bg-[#FFFBEB] border border-[#F59E0B] rounded-md">
                <p className="text-sm font-medium text-[#B45309]">
                  请谨慎考虑使用此类机票。AeroScout仅提供信息展示，不对使用此类机票产生的任何后果负责。
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 详情展开区域 */}
      {showDetails && (
        <div id="flight-details" className="mt-4 pt-4 border-t border-[#E6E6E6] animate-fadeIn">
          <h3 className="text-md font-medium text-[#1D1D1F] mb-3">航段详情</h3>
          <div className="space-y-4">
            {itinerary.segments?.map((segment, index) => (
            <React.Fragment key={segment.id || `segment-${index}`}>
              <div className="flex items-start p-3 bg-[#F5F5F7] rounded-apple">
                {/* Airline Logo in Segment Details */}
                {segment.airlineLogoUrl ? (
                  <Image
                    src={segment.airlineLogoUrl}
                    alt={`${segment.airlineName || 'Airline'} logo`}
                    width={32} // Smaller logo for segment details
                    height={32}
                    className="mr-3 rounded-md object-contain border border-[#E6E6E6]"
                    unoptimized={true} // External URL
                  />
                ) : (
                  <div className="w-8 h-8 mr-3 bg-white rounded-md flex items-center justify-center border border-[#E6E6E6] text-xs font-medium text-[#1D1D1F]">
                    {(segment.airlineName || 'A').substring(0,1)}
                  </div>
                )}
                <div className="mr-3 flex-shrink-0">
                  <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center border border-[#E6E6E6] text-xs font-medium text-[#1D1D1F]">
                    {index + 1}
                  </div>
                </div>
                <div className="flex-grow">
                  <div className="flex justify-between mb-2 items-center"> {/* Added items-center */}
                    <span className="text-sm font-medium text-[#1D1D1F]">
                      {segment.airlineName} {segment.flightNumber} {segment.equipment && <span className="text-xs text-gray-500">({segment.equipment})</span>}
                    </span>
                    <span className="text-xs text-[#86868B]">
                      {formatDuration(segment.durationMinutes)}
                    </span>
                  </div>
                  <div className="flex justify-between text-xs text-[#86868B]">
                    <div>
                      <p><strong>{formatTime(segment.departureTime)}</strong> {segment.departureAirportCode} {segment.departureTerminal && `(${segment.departureTerminal})`}</p>
                      <p title={segment.departureAirportFull || segment.departureAirportName}>{segment.departureCityName} - {segment.departureAirportName || segment.departureAirportCode}</p>
                    </div>
                    <div className="text-right">
                      <p><strong>{formatTime(segment.arrivalTime)}</strong> {segment.arrivalAirportCode} {segment.arrivalTerminal && `(${segment.arrivalTerminal})`}</p>
                      <p title={segment.arrivalAirportFull || segment.arrivalAirportName}>{segment.arrivalCityName} - {segment.arrivalAirportName || segment.arrivalAirportCode}</p>
                    </div>
                  </div>
                </div>
              </div>
              {/* Display transfer info between segments in detailed view */}
              {index < itinerary.segments.length - 1 && (
                <div className="my-2 pl-10 pr-3 text-xs">
                  <div className="border-l-2 border-dotted border-[#A1A1A6] pl-3 py-2">
                    <div className="flex items-center mb-1">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-[#86868B] mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      <span className="text-[#1D1D1F] font-medium">中转城市:</span>
                      <span className="ml-1 text-[#1D1D1F]">{segment.arrivalCityName || '未知城市'}</span>
                      {segment.arrivalAirportName && (
                        <span className="ml-1 text-[#86868B]">({segment.arrivalAirportName})</span>
                      )}
                    </div>

                    {segment.layoverDuration !== undefined && (
                      <div className="flex items-center mb-1">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-[#86868B] mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span className="text-[#1D1D1F] font-medium">中转时长:</span>
                        <span className={`ml-1 ${parseInt(segment.layoverDuration, 10) < 60 ? 'text-[#FF3B30] font-medium' : 'text-[#1D1D1F]'}`}>
                          {formatDuration(parseInt(segment.layoverDuration, 10))}
                          {parseInt(segment.layoverDuration, 10) < 60 && (
                            <span className="ml-1 text-[#FF3B30]">(中转时间较短)</span>
                          )}
                        </span>
                      </div>
                    )}

                    {segment.nextSegmentRequiresAirportChange && (
                      <div className="flex items-start mt-2 bg-[#FFF8E6] p-1.5 rounded-md">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-[#FF9500] mr-1.5 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                        <div>
                          <span className="font-medium text-[#FF9500] block">
                            注意: 此中转需要更换机场，请预留足够时间
                          </span>
                          {itinerary.transfers && itinerary.transfers[index]?.airportChangeDetail && (
                            <span className="text-[#FF9500] text-xs block mt-1">
                              从 {segment.arrivalAirportCode} ({segment.arrivalAirportName || '未知机场'})
                              到 {itinerary.segments[index + 1].departureAirportCode} ({itinerary.segments[index + 1].departureAirportName || '未知机场'})
                            </span>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Baggage recheck information */}
                    {(segment.isBaggageRecheck || (itinerary.transfers && itinerary.transfers[index]?.isBaggageRecheck)) && (
                      <div className="flex items-center mt-2 bg-[#F2E8FF] p-1.5 rounded-md">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-[#AF52DE] mr-1.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                        </svg>
                        <span className="font-medium text-[#AF52DE]">
                          注意: 此中转需要重新托运行李
                        </span>
                      </div>
                    )}

                    {/* Airline change information */}
                    {index + 1 < itinerary.segments.length && segment.airlineCode !== itinerary.segments[index + 1].airlineCode && (
                      <div className="flex items-center mt-2 bg-[#F5F5F7] p-1.5 rounded-md">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-[#86868B] mr-1.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                        </svg>
                        <span className="text-[#1D1D1F]">
                          航司变更: {segment.airlineName} → {itinerary.segments[index + 1].airlineName}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </React.Fragment>
          ))}
          </div>

          {/* 舱位信息 和 航司列表 */}
          <div className="mt-4 text-xs text-[#86868B] space-y-1">
            <p>舱位: {itinerary.segments?.[0]?.cabinClass === 'ECONOMY' ? '经济舱' :
                     itinerary.segments?.[0]?.cabinClass === 'PREMIUM_ECONOMY' ? '超级经济舱' :
                     itinerary.segments?.[0]?.cabinClass === 'BUSINESS' ? '商务舱' :
                     itinerary.segments?.[0]?.cabinClass === 'FIRST' ? '头等舱' : '未知'}</p>
            {itinerary.airlines && itinerary.airlines.length > 0 && (
              <p>执飞航司: {itinerary.airlines.join(', ')}</p>
            )}
          </div>


          {/* 预订链接 */}
          {itinerary.deepLink && (
            <div className="mt-4">
              <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center">
                <div className="mb-3 sm:mb-0">
                  <p className="text-xs text-[#86868B]">
                    通过 <span className="font-medium text-[#1D1D1F]">{itinerary.providerName || (itinerary.isProbeSuggestion ? 'Kiwi.com' : 'Trip.com')}</span> 预订
                  </p>
                  {itinerary.bookingToken && (
                    <p className="text-xs text-[#86868B] mt-1">
                      预订代码: <span className="font-mono bg-[#F5F5F7] px-1 py-0.5 rounded">{itinerary.bookingToken.substring(0, 12)}...</span>
                    </p>
                  )}
                </div>
                <a
                  href={itinerary.deepLink}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`inline-flex items-center justify-center px-6 py-2.5 text-white text-sm font-medium rounded-full transition-apple shadow-apple-sm w-full sm:w-auto animate-button-hover hover:shadow-apple group ${
                    itinerary.isProbeSuggestion
                      ? 'bg-[#FF9500] hover:bg-[#F08300]'
                      : isComboDeal
                        ? 'bg-[#AF52DE] hover:bg-[#9F42CE]'
                        : 'bg-[#0071E3] hover:bg-[#0077ED]'
                  }`}
                  onClick={handleBookingClick}
                  aria-label={`通过${itinerary.providerName || (itinerary.isProbeSuggestion ? 'Kiwi.com' : 'Trip.com')}预订此航班，价格${price} ${currencyName}`}
                >
                  <span className="mr-1 group-hover:translate-x-[-2px] transition-transform duration-300">
                    {itinerary.isProbeSuggestion
                      ? '查看实时价格'
                      : isComboDeal
                        ? '分别预订航段'
                        : '前往预订'}
                  </span>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 group-hover:translate-x-[2px] transition-transform duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                </a>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 查看详情按钮 */}
      <div className="mt-4 pt-4 border-t border-[#E6E6E6] flex justify-between items-center">
        <button
          className="text-sm text-[#0071E3] hover:text-[#0077ED] transition-apple font-medium focus:outline-none focus:ring-2 focus:ring-[#0071E3] focus:ring-offset-2 rounded-md px-2 py-1 -mx-2 -my-1 flex items-center"
          onClick={() => setShowDetails(!showDetails)}
          aria-expanded={showDetails}
          aria-controls="flight-details"
          aria-label={showDetails ? '收起航班详情' : '查看航班详情'}
        >
          {showDetails ? '收起详情' : '查看详情'}
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className={`h-4 w-4 ml-1 transition-transform ${showDetails ? 'rotate-180' : ''}`}
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            aria-hidden="true"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {/* 价格标签 */}
        <div className="text-xs text-[#86868B]">
          {currencyName}
        </div>
      </div>
      </Card>

      {/* 风险确认模态框 */}
      <RiskConfirmationModal
        isOpen={showRiskModal}
        onClose={() => setShowRiskModal(false)}
        onConfirm={handleRiskConfirm}
        itineraryId={itinerary.id}
        probeHub={itinerary.probeHub}
        probeDisclaimer={itinerary.probeDisclaimer}
      />
    </>
  );
};

export default FlightCard;