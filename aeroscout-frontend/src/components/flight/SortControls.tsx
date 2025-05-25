'use client';

import React from 'react';

type SortOption = 'price' | 'duration' | 'departureTime' | 'arrivalTime';
type SortOrder = 'asc' | 'desc';

interface SortConfig {
  sortBy: SortOption;
  order: SortOrder;
}

interface SortControlsProps {
  sortConfig: SortConfig;
  onSortChange: (newSortConfig: SortConfig) => void;
  disabled?: boolean;
}

const sortOptions: { value: SortOption; label: string }[] = [
  { value: 'price', label: '价格' },
  { value: 'duration', label: '总时长' },
  { value: 'departureTime', label: '出发时间' },
  { value: 'arrivalTime', label: '到达时间' },
];

const SortControls: React.FC<SortControlsProps> = ({ sortConfig, onSortChange, disabled }) => {
  const handleSortByChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    onSortChange({ ...sortConfig, sortBy: event.target.value as SortOption });
  };

  const handleOrderChange = (newOrder: SortOrder) => {
    onSortChange({ ...sortConfig, order: newOrder });
  };

  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-4 sm:space-y-0 sm:space-x-4 my-4 p-4 bg-white rounded-apple shadow-apple-sm border border-[#E8E8ED]">
      <div className="flex items-center w-full sm:w-auto">
        <label htmlFor="sort-by" className="text-sm font-medium text-[#1D1D1F] mr-2 whitespace-nowrap">
          排序方式:
        </label>
        <select
          id="sort-by"
          value={sortConfig.sortBy}
          onChange={handleSortByChange}
          disabled={disabled}
          className="block w-full sm:w-40 pl-3 pr-10 py-2 text-sm border border-[#D2D2D7] focus:outline-none focus:ring-[#0071E3] focus:border-[#0071E3] rounded-md disabled:bg-[#F5F5F7] disabled:cursor-not-allowed transition-apple"
        >
          {sortOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      <div className="flex items-center w-full sm:w-auto">
        <span className="text-sm font-medium text-[#1D1D1F] mr-2 sm:hidden whitespace-nowrap">
          排序顺序:
        </span>
        <div className="flex items-center flex-grow sm:flex-grow-0">
          <button
            onClick={() => handleOrderChange('asc')}
            disabled={disabled || sortConfig.order === 'asc'}
            className={`px-3 py-2 border text-sm font-medium rounded-l-md transition-apple flex-1 sm:flex-auto
                        ${sortConfig.order === 'asc'
                          ? 'bg-[#0071E3] text-white border-[#0071E3]'
                          : 'bg-white text-[#1D1D1F] border-[#D2D2D7] hover:bg-[#F5F5F7]'}
                        disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            升序
          </button>
          <button
            onClick={() => handleOrderChange('desc')}
            disabled={disabled || sortConfig.order === 'desc'}
            className={`px-3 py-2 border-t border-b border-r rounded-r-md text-sm font-medium transition-apple flex-1 sm:flex-auto
                        ${sortConfig.order === 'desc'
                          ? 'bg-[#0071E3] text-white border-[#0071E3]'
                          : 'bg-white text-[#1D1D1F] border-[#D2D2D7] hover:bg-[#F5F5F7]'}
                        disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            降序
          </button>
        </div>
      </div>
    </div>
  );
};

export default SortControls;
export type { SortConfig, SortOption, SortOrder };