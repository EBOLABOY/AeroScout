/**
 * 简化的机场搜索输入组件
 */
import React from 'react';

interface AirportSearchInputProps {
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  className?: string;
}

const AirportSearchInput: React.FC<AirportSearchInputProps> = ({
  placeholder = "搜索机场...",
  value = "",
  onChange,
  className = ""
}) => {
  return (
    <input
      type="text"
      placeholder={placeholder}
      value={value}
      onChange={(e) => onChange?.(e.target.value)}
      className={`w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${className}`}
    />
  );
};

export default AirportSearchInput; 