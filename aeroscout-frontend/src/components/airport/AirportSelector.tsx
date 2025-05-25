'use client';

import React, { useState, useEffect, useRef } from 'react';
import { searchAirports, AirportInfo } from '@/lib/apiService';
import useDebounce from '@/hooks/useDebounce';
// import { useAlertStore } from '@/store/alertStore'; // showAlert 未使用，移除

interface AirportSelectorProps {
  label: string;
  placeholder?: string;
  onAirportSelected: (airport: AirportInfo | null) => void;
  value?: AirportInfo | null;
  disabled?: boolean;
  error?: string; // 添加错误消息属性
}

/**
 * 简化版AirportSelector组件
 * 使用单一数据源和清晰的状态流，避免竞态条件
 */
const AirportSelector: React.FC<AirportSelectorProps> = ({
  label,
  placeholder = "搜索机场或城市...",
  onAirportSelected,
  value,
  disabled = false,
  error
}) => {
  // 基本状态
  const [inputValue, setInputValue] = useState('');
  const [searchResults, setSearchResults] = useState<AirportInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);

  // 引用
  const inputRef = useRef<HTMLInputElement>(null);
  const selectingRef = useRef(false); // 跟踪是否正在进行选择操作

  // 格式化机场信息为显示文本
  const formatAirportText = (airport: AirportInfo | null | undefined): string => {
    if (!airport || !airport.name || !airport.code) return '';
    return `${airport.name} (${airport.code})`;
  };

  // 当value属性变化时，更新输入框显示
  useEffect(() => {
    const currentTime = Date.now();
    const newText = formatAirportText(value);
    console.log(`[AirportSelector] useEffect[value] triggered at ${currentTime}:`, {
      value,
      currentInputValue: inputValue,
      selectingRefCurrent: selectingRef.current,
      newText
    });

    // 如果外部value变更且不是在选择中，更新输入值
    // 只有当新文本与当前输入值不同，且当前输入值等于之前value的格式化文本时才更新
    // 这避免了在用户正在输入时被干扰
    if (!selectingRef.current) {
      const shouldUpdate = newText !== inputValue &&
        (inputValue === '' || inputValue === formatAirportText(null));

      if (shouldUpdate) {
        console.log(`[AirportSelector] useEffect[value] at ${currentTime}: updating inputValue from "${inputValue}" to "${newText}"`);
        setInputValue(newText);
      } else {
        console.log(`[AirportSelector] useEffect[value] at ${currentTime}: skipping update - shouldUpdate: ${shouldUpdate}`);
      }
    } else {
      console.log(`[AirportSelector] useEffect[value] at ${currentTime}: skipping update - selectingRef is true`);
    }
  }, [value, inputValue]); // 添加inputValue依赖

  // 处理搜索查询
  const debouncedQuery = useDebounce(inputValue, 300);

  useEffect(() => {
    // 只有当输入不是当前选中值的显示文本时才搜索
    // 同时确保不在选择过程中触发搜索
    if (debouncedQuery && debouncedQuery.length >= 2 &&
        debouncedQuery !== formatAirportText(value) &&
        !selectingRef.current) { // 添加selectingRef检查

      console.log(`[AirportSelector] Search triggered for query: "${debouncedQuery}", selectingRef: ${selectingRef.current}`);

      const fetchAirports = async () => {
        setIsLoading(true);
        try {
          const response = await searchAirports({
            query: debouncedQuery,
            trip_type: 'flight',
            mode: 'dep'
          });
          setSearchResults(response.airports);
          setIsDropdownOpen(response.airports.length > 0);
        } catch (error) {
          console.error('搜索机场失败:', error);
          setSearchResults([]);
          setIsDropdownOpen(false);
        } finally {
          setIsLoading(false);
        }
      };

      fetchAirports();
    } else if (debouncedQuery.length < 2) {
      setSearchResults([]);
      setIsDropdownOpen(false);
    } else {
      console.log(`[AirportSelector] Search skipped for query: "${debouncedQuery}", reasons: length=${debouncedQuery.length}, matchesValue=${debouncedQuery === formatAirportText(value)}, selectingRef=${selectingRef.current}`);
    }
  }, [debouncedQuery, value]);

  // 处理输入变化
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInputValue(newValue);

    // 如果清空输入，则清空选择
    if (newValue === '' && value) {
      onAirportSelected(null);
    }

    // 如果输入的不是当前选中的值，打开下拉列表
    if (newValue !== formatAirportText(value)) {
      setIsDropdownOpen(newValue.length >= 2);
    }
  };

  // 选择机场
  const handleSelectAirport = (airport: AirportInfo) => {
    console.log(`[AirportSelector] handleSelectAirport called at ${Date.now()}: selecting airport`, airport);
    selectingRef.current = true;

    // 更新UI
    const formattedText = formatAirportText(airport);
    setInputValue(formattedText);
    setIsDropdownOpen(false);
    setSearchResults([]);

    console.log(`[AirportSelector] handleSelectAirport: set inputValue to "${formattedText}"`);

    // 通知父组件
    onAirportSelected(airport);

    // 重置选择状态 - 延长时间以确保状态更新链完成
    setTimeout(() => {
      console.log(`[AirportSelector] selectingRef reset at ${Date.now()}: resetting selectingRef to false`);
      selectingRef.current = false;
    }, 300); // 增加到300ms以提供足够的状态更新时间

    // 移除焦点
    inputRef.current?.blur();
  };

  // 处理输入框失去焦点
  const handleBlur = () => {
    console.log(`[AirportSelector] handleBlur called at ${Date.now()}: current selectingRef: ${selectingRef.current}`);

    // 延迟处理失焦，以便可以先处理选择事件
    // 延迟时间与handleSelectAirport保持一致
    setTimeout(() => {
      if (!selectingRef.current) {
        console.log(`[AirportSelector] handleBlur timeout executed at ${Date.now()}: closing dropdown`);
        setIsDropdownOpen(false);

        // 简化逻辑：如果当前输入不匹配任何选择的值且不为空，则重置
        const currentValueText = formatAirportText(value);
        if (inputValue !== currentValueText && inputValue.trim() !== '') {
          console.log(`[AirportSelector] handleBlur: resetting inputValue from "${inputValue}" to "${currentValueText}"`);
          setInputValue(currentValueText);
        }
      } else {
        console.log(`[AirportSelector] handleBlur timeout skipped at ${Date.now()}: selectingRef is still true`);
      }
    }, 300); // 与handleSelectAirport的延迟保持一致
  };

  // 清除选择
  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation(); // 阻止冒泡，避免触发其他事件
    setInputValue('');
    setSearchResults([]);
    setIsDropdownOpen(false);
    onAirportSelected(null);
    inputRef.current?.focus();
  };

  // 处理键盘导航
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isDropdownOpen || searchResults.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex(prev =>
          prev < searchResults.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex(prev =>
          prev > 0 ? prev - 1 : searchResults.length - 1
        );
        break;
      case 'Enter':
        e.preventDefault();
        if (highlightedIndex >= 0 && highlightedIndex < searchResults.length) {
          handleSelectAirport(searchResults[highlightedIndex]);
        }
        break;
      case 'Escape':
        e.preventDefault();
        setIsDropdownOpen(false);
        inputRef.current?.blur();
        break;
    }
  };

  return (
    <div className="relative w-full">
      <label className="block text-[15px] font-semibold text-[#1D1D1F] mb-3 flex items-center">
        <svg className="w-4 h-4 mr-2 text-[#0071E3]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
        </svg>
        {label}
      </label>

      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onFocus={() => setIsDropdownOpen(inputValue.length >= 2)}
          onBlur={handleBlur}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          className={`
            w-full px-4 py-3.5 pr-16 text-[#1D1D1F] bg-white border border-[#D2D2D7]
            rounded-apple-lg focus:outline-none focus:ring-2 focus:ring-[#0071E3]/20 focus:border-[#0071E3]
            transition-all duration-200 ease-out placeholder-[#86868B] text-[15px] font-medium
            ${disabled ? 'bg-[#F5F5F7] cursor-not-allowed' : 'hover:border-[#AEAEB2] hover:shadow-apple-sm'}
            ${error ? 'border-[#FF3B30] focus:border-[#FF3B30] focus:ring-[#FF3B30]/20' : ''}
            ${isDropdownOpen ? 'border-[#0071E3] ring-2 ring-[#0071E3]/20 shadow-apple-sm' : ''}
          `}
          autoComplete="off"
          role="combobox"
          aria-expanded={isDropdownOpen}
          aria-haspopup="listbox"
          aria-autocomplete="list"
          aria-controls="airport-dropdown"
        />

        {/* 右侧图标 */}
        <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center space-x-2">
          {isLoading ? (
            <div className="w-5 h-5 border-2 border-[#0071E3] border-t-transparent rounded-full animate-spin"></div>
          ) : value ? (
            <button
              type="button"
              onClick={handleClear}
              className="w-5 h-5 rounded-full bg-[#86868B] hover:bg-[#FF3B30] flex items-center justify-center transition-all duration-200 group"
              aria-label="清除选择"
            >
              <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          ) : null}

          <svg className={`h-4 w-4 transition-colors duration-200 ${isDropdownOpen ? 'text-[#0071E3]' : 'text-[#86868B]'}`} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
      </div>

      {/* 下拉菜单 */}
      {isDropdownOpen && (
        <div id="airport-dropdown" className="absolute z-[99999] left-0 right-0 mt-1 bg-white border border-[#D2D2D7] rounded-apple shadow-apple-lg max-h-64 overflow-hidden animate-slideDown min-w-[400px]" style={{ zIndex: 99999 }}>
          {/* 搜索状态指示器 */}
          {isLoading && (
            <div className="px-4 py-3 border-b border-[#F5F5F7]">
              <div className="flex items-center justify-center space-x-2">
                <div className="w-4 h-4 border-2 border-[#0071E3] border-t-transparent rounded-full animate-spin"></div>
                <span className="text-sm text-[#86868B]">搜索中...</span>
              </div>
            </div>
          )}

          {/* 搜索结果 */}
          <div className="max-h-72 overflow-y-auto">
            {searchResults.length === 0 && !isLoading ? (
              <div className="px-4 py-8 text-center">
                <div className="w-12 h-12 mx-auto mb-3 bg-[#F5F5F7] rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6 text-[#86868B]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <p className="text-sm text-[#86868B] font-medium">未找到相关机场</p>
                <p className="text-xs text-[#86868B] mt-1">请尝试输入城市名称或机场代码</p>
              </div>
            ) : (
              searchResults.map((airport, index) => (
                <div
                  key={airport.code}
                  onClick={() => handleSelectAirport(airport)}
                  className={`
                    group px-5 py-3.5 cursor-pointer transition-all duration-150 ease-out border-b border-[#F5F5F7] last:border-b-0
                    ${index === highlightedIndex
                      ? 'bg-[#0071E3] text-white'
                      : 'hover:bg-[#F5F5F7]'
                    }
                  `}
                  role="option"
                  aria-selected={index === highlightedIndex}
                >
                  <div className="flex items-center space-x-4">
                    {/* 机场图标 */}
                    <div className={`
                      w-8 h-8 rounded-md flex items-center justify-center flex-shrink-0 transition-all duration-150
                      ${index === highlightedIndex
                        ? 'bg-white/20 text-white'
                        : 'bg-[#0071E3] text-white'
                      }
                    `}>
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                      </svg>
                    </div>

                    {/* 机场名称 */}
                    <div className={`
                      flex-1 font-medium text-[15px] transition-colors duration-150
                      ${index === highlightedIndex ? 'text-white' : 'text-[#1D1D1F]'}
                    `}>
                      {airport.name}
                    </div>

                    {/* 城市信息 */}
                    <div className={`
                      text-sm transition-colors duration-150 flex-shrink-0
                      ${index === highlightedIndex ? 'text-white/80' : 'text-[#86868B]'}
                    `}>
                      {airport.city}, {airport.country}
                    </div>

                    {/* 机场代码 */}
                    <div className={`
                      text-sm font-mono font-bold transition-colors duration-150 flex-shrink-0 min-w-[3rem] text-right
                      ${index === highlightedIndex ? 'text-white' : 'text-[#0071E3]'}
                    `}>
                      {airport.code}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* 错误提示 */}
      {error && (
        <p className="text-[#FF3B30] text-xs mt-1">{error}</p>
      )}
    </div>
  );
};

export default AirportSelector;
