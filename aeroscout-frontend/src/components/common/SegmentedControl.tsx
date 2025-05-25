'use client';

import React, { useState, useEffect, useRef } from 'react';

interface SegmentOption {
  value: string;
  label: string;
  icon?: React.ReactNode;
}

interface SegmentedControlProps {
  options: SegmentOption[];
  value: string;
  onChange: (value: string) => void;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  disabled?: boolean;
}

const SegmentedControl: React.FC<SegmentedControlProps> = ({
  options,
  value,
  onChange,
  className = '',
  size = 'md',
  fullWidth = false,
  disabled = false,
}) => {
  const [activeIndex, setActiveIndex] = useState(0);
  const [indicatorStyle, setIndicatorStyle] = useState({});
  const segmentRefs = useRef<(HTMLButtonElement | null)[]>([]);

  // 尺寸样式
  const sizeStyles = {
    sm: {
      container: 'h-8 text-[13px]',
      segment: 'py-1.5',
    },
    md: {
      container: 'h-10 text-[15px]',
      segment: 'py-2',
    },
    lg: {
      container: 'h-12 text-[17px]',
      segment: 'py-2.5',
    },
  };

  // 更新选中项和指示器位置
  useEffect(() => {
    const index = options.findIndex(option => option.value === value);
    if (index !== -1) {
      setActiveIndex(index);
      updateIndicator(index);
    }
  }, [value, options]);

  // 更新指示器位置
  const updateIndicator = (index: number) => {
    const currentSegment = segmentRefs.current[index];
    if (currentSegment) {
      setIndicatorStyle({
        width: `${currentSegment.offsetWidth}px`,
        transform: `translateX(${currentSegment.offsetLeft}px)`,
      });
    }
  };

  // 处理选项点击
  const handleSegmentClick = (option: SegmentOption, index: number) => {
    if (disabled) return;
    setActiveIndex(index);
    onChange(option.value);
  };

  return (
    <div
      className={`
        relative inline-flex bg-[#F5F5F7] rounded-full p-1
        ${sizeStyles[size].container}
        ${fullWidth ? 'w-full' : ''}
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        ${className}
      `}
    >
      {/* 背景指示器 */}
      <div
        className="absolute top-1 bottom-1 rounded-full bg-white shadow-apple-sm transition-apple"
        style={indicatorStyle}
      />

      {/* 选项按钮 */}
      {options.map((option, index) => (
        <button
          key={option.value}
          ref={el => (segmentRefs.current[index] = el)}
          className={`
            relative flex-1 flex items-center justify-center px-4 rounded-full
            ${sizeStyles[size].segment}
            transition-apple
            ${disabled ? 'cursor-not-allowed' : 'cursor-pointer'}
            ${activeIndex === index ? 'text-[#1D1D1F] font-medium' : 'text-[#8E8E93]'}
          `}
          onClick={() => handleSegmentClick(option, index)}
          disabled={disabled}
          type="button"
        >
          {option.icon && <span className="mr-1.5">{option.icon}</span>}
          {option.label}
        </button>
      ))}
    </div>
  );
};

export default SegmentedControl;
