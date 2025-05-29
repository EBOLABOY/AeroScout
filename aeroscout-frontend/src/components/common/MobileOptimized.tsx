'use client';

import React from 'react';

interface MobileOptimizedProps {
  children: React.ReactNode;
  className?: string;
}

/**
 * 移动端优化包装组件
 * 提供移动端友好的布局和交互优化
 */
const MobileOptimized: React.FC<MobileOptimizedProps> = ({ 
  children, 
  className = '' 
}) => {
  return (
    <div className={`
      mobile-safe-area 
      mobile-scroll 
      ${className}
    `}>
      {children}
    </div>
  );
};

export default MobileOptimized;
