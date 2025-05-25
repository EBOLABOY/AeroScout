'use client';

import React, { useState, useEffect, useRef } from 'react';
import { FlightItinerary } from '@/store/flightResultsStore';
import FlightCard from './FlightCard';

interface VirtualizedFlightListProps {
  itineraries: FlightItinerary[];
  isComboDeal?: boolean;
}

const VirtualizedFlightList: React.FC<VirtualizedFlightListProps> = ({ 
  itineraries, 
  isComboDeal = false 
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [visibleRange, setVisibleRange] = useState({ start: 0, end: 10 });
  const [itemHeight, setItemHeight] = useState(300); // 预估的每个FlightCard高度
  const bufferSize = 3; // 上下各多渲染几个项目，以避免滚动时出现空白
  
  // 监听滚动事件，更新可见范围
  useEffect(() => {
    const updateVisibleRange = () => {
      if (!containerRef.current) return;
      
      const container = containerRef.current;
      const scrollTop = window.scrollY;
      const viewportHeight = window.innerHeight;
      const containerTop = container.getBoundingClientRect().top + window.scrollY;
      
      // 计算可见范围内的第一个和最后一个项目索引
      const start = Math.max(0, Math.floor((scrollTop - containerTop) / itemHeight) - bufferSize);
      const end = Math.min(
        itineraries.length,
        Math.ceil((scrollTop - containerTop + viewportHeight) / itemHeight) + bufferSize
      );
      
      setVisibleRange({ start, end });
    };
    
    // 初始更新
    updateVisibleRange();
    
    // 添加滚动事件监听器
    window.addEventListener('scroll', updateVisibleRange);
    window.addEventListener('resize', updateVisibleRange);
    
    // 清理函数
    return () => {
      window.removeEventListener('scroll', updateVisibleRange);
      window.removeEventListener('resize', updateVisibleRange);
    };
  }, [itineraries.length, itemHeight]);
  
  // 测量第一个渲染项目的高度，以更新itemHeight
  useEffect(() => {
    if (containerRef.current && containerRef.current.firstChild) {
      const firstItem = containerRef.current.firstChild as HTMLElement;
      const observer = new ResizeObserver((entries) => {
        const height = entries[0].contentRect.height;
        if (height > 0 && Math.abs(height - itemHeight) > 50) {
          setItemHeight(height);
        }
      });
      
      observer.observe(firstItem);
      return () => observer.disconnect();
    }
  }, [visibleRange, itemHeight]);
  
  // 计算容器总高度
  const totalHeight = itineraries.length * itemHeight;
  
  // 计算可见项目的偏移量
  const topPadding = visibleRange.start * itemHeight;
  const bottomPadding = (itineraries.length - visibleRange.end) * itemHeight;
  
  return (
    <div 
      ref={containerRef} 
      style={{ position: 'relative', height: `${totalHeight}px` }}
      className="grid grid-cols-1 gap-6"
    >
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: `${topPadding}px` }} />
      
      {itineraries.slice(visibleRange.start, visibleRange.end).map((itinerary, index) => (
        <div 
          key={itinerary.id || `flight-${visibleRange.start + index}`}
          style={{ 
            position: 'absolute', 
            top: `${topPadding + index * itemHeight}px`,
            left: 0,
            right: 0
          }}
        >
          <FlightCard 
            itinerary={itinerary} 
            isComboDeal={isComboDeal} 
          />
        </div>
      ))}
      
      <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: `${bottomPadding}px` }} />
    </div>
  );
};

export default VirtualizedFlightList;
