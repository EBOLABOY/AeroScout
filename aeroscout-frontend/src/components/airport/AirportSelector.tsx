'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Airport } from '../../types/airport';
import { searchAirports } from '../../lib/apiService';
import { useAlertStore } from '../../store/alertStore';

interface SimpleAirportSelectorProps {
  value: Airport | null;
  onChange: (airport: Airport | null) => void;
  placeholder?: string;
  mode: 'dep' | 'arr';
  disabled?: boolean;
  className?: string;
}

const SimpleAirportSelector: React.FC<SimpleAirportSelectorProps> = ({
  value,
  onChange,
  placeholder = '搜索机场或城市...',
  mode,
  disabled = false,
  className = '',
}) => {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [airports, setAirports] = useState<Airport[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);

  const { showAlert } = useAlertStore();
  const debounceTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [touchStartY, setTouchStartY] = useState<number | null>(null);

  // 防抖搜索函数
  const searchAirportsDebounced = useCallback(async (searchQuery: string) => {
    if (searchQuery.length < 2) {
      setAirports([]);
      return;
    }

    if (process.env.NODE_ENV === 'development') {
      console.log('Searching airports for query:', searchQuery);
    }

    setIsLoading(true);
    try {
      const response = await searchAirports({
        query: searchQuery,
        trip_type: 'flight',
        mode: mode,
      });

      if (process.env.NODE_ENV === 'development') {
        console.log('Airport search response:', response);
      }

      if (response && response.success && Array.isArray(response.airports)) {
        const formattedAirports: Airport[] = response.airports.map(airport => ({
          code: airport.code || '',
          name: airport.name || '',
          city: airport.city || '',
          country: airport.country || '',
          type: airport.type || 'AIRPORT',
        }));

        setAirports(formattedAirports);
      } else {
        setAirports([]);
      }
    } catch (error) {
      if (process.env.NODE_ENV === 'development') {
        console.error('机场搜索失败:', error);
        showAlert('机场搜索失败，请检查网络连接', 'error');
      }
      setAirports([]);
    } finally {
      setIsLoading(false);
    }
  }, [mode, showAlert]);

  // 处理输入变化
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newQuery = e.target.value;

    if (process.env.NODE_ENV === 'development') {
      console.log('Input change:', newQuery);
    }

    setQuery(newQuery);
    setSelectedIndex(-1);

    // 清除之前的防抖定时器
    if (debounceTimeoutRef.current) {
      clearTimeout(debounceTimeoutRef.current);
    }

    if (newQuery.length < 2) {
      setIsOpen(false);
      setAirports([]);
      return;
    }

    // 打开下拉菜单
    setIsOpen(true);

    // 防抖搜索
    debounceTimeoutRef.current = setTimeout(() => {
      searchAirportsDebounced(newQuery);
    }, 300);
  };

  // 处理机场选择
  const handleAirportSelect = (airport: Airport) => {
    setQuery(`${airport.name} (${airport.code})`);
    setIsOpen(false);
    setSelectedIndex(-1);
    onChange(airport);
  };

  // 处理触摸滚动 - 防止页面滚动
  const handleTouchStart = (e: React.TouchEvent) => {
    setTouchStartY(e.touches[0].clientY);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!dropdownRef.current || touchStartY === null) return;

    const touchY = e.touches[0].clientY;
    const deltaY = touchY - touchStartY;
    const dropdown = dropdownRef.current;

    // 检查是否在下拉菜单的边界
    const isAtTop = dropdown.scrollTop === 0 && deltaY > 0;
    const isAtBottom = dropdown.scrollTop + dropdown.clientHeight >= dropdown.scrollHeight && deltaY < 0;

    // 如果在边界且试图继续滚动，阻止默认行为
    if (isAtTop || isAtBottom) {
      e.preventDefault();
    }
  };

  // 处理键盘导航
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen || airports.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => Math.min(prev + 1, airports.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => Math.max(prev - 1, -1));
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < airports.length) {
          handleAirportSelect(airports[selectedIndex]);
        }
        break;
      case 'Escape':
        e.preventDefault();
        setIsOpen(false);
        setSelectedIndex(-1);
        inputRef.current?.focus();
        break;
    }
  };

  // 处理点击外部关闭 - 移动端优化
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent | TouchEvent) => {
      const target = event.target as Node;

      if (containerRef.current && !containerRef.current.contains(target)) {
        setIsOpen(false);
        setSelectedIndex(-1);
      }
    };

    const handleTouchOutside = (event: TouchEvent) => {
      const target = event.target as Node;

      if (containerRef.current && !containerRef.current.contains(target)) {
        setIsOpen(false);
        setSelectedIndex(-1);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('touchstart', handleTouchOutside, { passive: true });
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
        document.removeEventListener('touchstart', handleTouchOutside);
      };
    }
  }, [isOpen]);

  // 清理防抖定时器
  useEffect(() => {
    return () => {
      if (debounceTimeoutRef.current) {
        clearTimeout(debounceTimeoutRef.current);
      }
    };
  }, []);

  // 当value变化时更新显示
  useEffect(() => {
    if (value) {
      setQuery(`${value.name} (${value.code})`);
    } else {
      setQuery('');
    }
  }, [value]);

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={() => {
            if (query.length >= 2 && airports.length === 0 && !isLoading) {
              searchAirportsDebounced(query);
            }
          }}
          placeholder={placeholder}
          disabled={disabled}
          className="w-full px-3 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 bg-white transition-all duration-200 hover:border-gray-400 text-[14px] sm:text-[14px] font-medium placeholder:text-gray-400 min-h-[48px] text-[16px]"
          autoComplete="off"
          inputMode="search"
          enterKeyHint="search"
        />

        {/* 搜索图标或加载指示器 */}
        <div className="absolute right-4 top-1/2 transform -translate-y-1/2">
          {isLoading ? (
            <div className="animate-spin rounded-full h-5 w-5 border-2 border-gray-300 border-t-blue-500"></div>
          ) : (
            <svg
              className="w-5 h-5 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          )}
        </div>
      </div>

      {/* 下拉菜单 - 移动端优化 */}
      {isOpen && (
        <div
          ref={dropdownRef}
          className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-xl shadow-lg max-h-64 sm:max-h-80 overflow-y-auto z-50 animate-slideDown mobile-scroll"
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          style={{
            minWidth: '280px',
            maxWidth: '100vw',
            boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.15)',
            WebkitOverflowScrolling: 'touch', // iOS 滚动优化
            overscrollBehavior: 'contain', // 防止滚动链
          }}
        >
          {isLoading ? (
            <div className="px-6 py-5 text-gray-600 text-[15px] text-center flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-gray-300 border-t-blue-600 mr-3"></div>
              搜索中...
            </div>
          ) : airports.length > 0 ? (
            <div className="py-1">
              {airports.map((airport, index) => (
                <div
                  key={airport.code}
                  onClick={() => handleAirportSelect(airport)}
                  onTouchStart={(e) => {
                    // 防止触摸时的默认行为
                    e.currentTarget.style.backgroundColor = index === selectedIndex ? '#3B82F6' : '#F9FAFB';
                  }}
                  onTouchEnd={(e) => {
                    // 恢复原始样式
                    setTimeout(() => {
                      if (e.currentTarget) {
                        e.currentTarget.style.backgroundColor = '';
                      }
                    }, 150);
                  }}
                  className={`mx-1 px-3 py-4 sm:py-3 cursor-pointer transition-all duration-150 rounded-lg min-h-[56px] sm:min-h-[auto] flex items-center ${
                    index === selectedIndex
                      ? 'bg-blue-500 text-white'
                      : 'hover:bg-gray-50 text-gray-900 active:bg-gray-100'
                  }`}
                  style={{
                    WebkitTapHighlightColor: 'transparent', // 移除iOS点击高亮
                    touchAction: 'manipulation', // 优化触摸响应
                  }}
                >
                  <div className="flex items-center justify-between w-full">
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-[14px] sm:text-[14px] truncate">
                        {airport.name}
                      </div>
                      <div className={`text-[12px] sm:text-[12px] truncate mt-0.5 ${
                        index === selectedIndex ? 'text-white/80' : 'text-gray-500'
                      }`}>
                        {airport.city}, {airport.country}
                      </div>
                    </div>
                    <div className={`text-[11px] sm:text-[12px] font-mono font-bold px-2 py-1 rounded ml-3 flex-shrink-0 ${
                      index === selectedIndex
                        ? 'bg-white/20 text-white'
                        : 'bg-gray-100 text-gray-700'
                    }`}>
                      {airport.code}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : query.length >= 2 ? (
            <div className="px-6 py-8 text-gray-500 text-[15px] text-center">
              <div className="mb-2">
                <svg className="w-8 h-8 text-gray-300 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              未找到匹配的机场
            </div>
          ) : (
            <div className="px-6 py-8 text-gray-500 text-[15px] text-center">
              <div className="mb-2">
                <svg className="w-8 h-8 text-gray-300 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16l2.879-2.879m0 0a3 3 0 104.243-4.242 3 3 0 00-4.243 4.242zM21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              请输入至少2个字符进行搜索
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SimpleAirportSelector;
