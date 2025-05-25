'use client';

import React from 'react';
import { AirlineInfo } from '@/store/flightResultsStore';

export interface FilterConfig {
  selectedAirlines: string[]; // Array of airline codes
  maxStops: number | null; // null for any, 0 for direct, 1 for 1 stop, etc.
}

interface FilterControlsProps {
  availableAirlines: AirlineInfo[];
  availableStopOptions: { label: string; value: number | null }[];
  filterConfig: FilterConfig;
  onFilterChange: (newFilterConfig: FilterConfig) => void;
  disabled?: boolean;
}

const FilterControls: React.FC<FilterControlsProps> = ({
  availableAirlines,
  availableStopOptions,
  filterConfig,
  onFilterChange,
  disabled,
}) => {
  const handleAirlineChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedOptions = Array.from(event.target.selectedOptions, (option) => option.value);
    onFilterChange({ ...filterConfig, selectedAirlines: selectedOptions });
  };

  const handleStopsChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    const value = event.target.value;
    onFilterChange({
      ...filterConfig,
      maxStops: value === 'any' ? null : parseInt(value, 10),
    });
  };

  return (
    <div className="flex flex-col my-4 p-4 bg-white rounded-apple shadow-apple-sm border border-[#E8E8ED]">
      <div className="flex flex-col md:flex-row items-start md:items-start space-y-4 md:space-y-0 md:space-x-4">
        {/* Airline Filter */}
        <div className="flex flex-col w-full md:w-1/2">
          <label htmlFor="airline-filter" className="mb-1 text-sm font-medium text-[#1D1D1F]">
            航空公司:
          </label>
          <select
            id="airline-filter"
            multiple
            value={filterConfig.selectedAirlines}
            onChange={handleAirlineChange}
            disabled={disabled || availableAirlines.length === 0}
            className="block w-full pl-3 pr-10 py-2 text-sm border border-[#D2D2D7] focus:outline-none focus:ring-[#0071E3] focus:border-[#0071E3] rounded-md disabled:bg-[#F5F5F7] disabled:cursor-not-allowed transition-apple"
            size={Math.min(4, availableAirlines.length + 1)} // 减少在移动端显示的选项数量
          >
            {availableAirlines.map((airline) => (
              <option key={airline.code} value={airline.code}>
                {airline.name} ({airline.code})
              </option>
            ))}
          </select>
          <div className="flex justify-between items-center">
            {availableAirlines.length > 4 && (
              <p className="text-xs text-[#86868B] mt-1">可滚动查看更多航司</p>
            )}
            {availableAirlines.length === 0 && !disabled && (
              <p className="text-xs text-[#86868B] mt-1">当前结果无可选航司</p>
            )}
            {filterConfig.selectedAirlines.length > 0 && (
              <button
                onClick={() => onFilterChange({ ...filterConfig, selectedAirlines: [] })}
                className="text-xs text-[#0071E3] mt-1 hover:underline focus:outline-none"
                disabled={disabled}
              >
                清除选择
              </button>
            )}
          </div>
        </div>

        {/* Stops Filter */}
        <div className="flex flex-col w-full md:w-1/2">
          <label htmlFor="stops-filter" className="mb-1 text-sm font-medium text-[#1D1D1F]">
            中转次数:
          </label>
          <select
            id="stops-filter"
            value={filterConfig.maxStops === null ? 'any' : filterConfig.maxStops.toString()}
            onChange={handleStopsChange}
            disabled={disabled || availableStopOptions.length === 0}
            className="block w-full pl-3 pr-10 py-2 text-sm border border-[#D2D2D7] focus:outline-none focus:ring-[#0071E3] focus:border-[#0071E3] rounded-md disabled:bg-[#F5F5F7] disabled:cursor-not-allowed transition-apple"
          >
            {availableStopOptions.map((option) => (
              <option key={option.label} value={option.value === null ? 'any' : option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <div className="flex justify-between items-center">
            {availableStopOptions.length === 0 && !disabled && (
              <p className="text-xs text-[#86868B] mt-1">当前结果无可选次数</p>
            )}
            {filterConfig.maxStops !== null && (
              <button
                onClick={() => onFilterChange({ ...filterConfig, maxStops: null })}
                className="text-xs text-[#0071E3] mt-1 hover:underline focus:outline-none"
                disabled={disabled}
              >
                重置为任意中转
              </button>
            )}
          </div>
        </div>
      </div>

      {/* 清除所有筛选按钮 */}
      {(filterConfig.selectedAirlines.length > 0 || filterConfig.maxStops !== null) && (
        <div className="mt-4 pt-3 border-t border-[#E8E8ED] flex justify-end">
          <button
            onClick={() => onFilterChange({ selectedAirlines: [], maxStops: null })}
            className="text-sm text-[#0071E3] px-3 py-1 rounded-full border border-[#0071E3] hover:bg-[#F5F5F7] focus:outline-none focus:ring-2 focus:ring-[#0071E3] transition-apple"
            disabled={disabled}
          >
            清除所有筛选
          </button>
        </div>
      )}
    </div>
  );
};

export default FilterControls;