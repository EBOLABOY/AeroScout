'use client';

import React from 'react';

export interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  hoverable?: boolean;
  variant?: 'elevated' | 'filled' | 'outlined' | 'plain';
  role?: string;
  'aria-label'?: string;
  'aria-labelledby'?: string;
  'aria-describedby'?: string;
  'aria-hidden'?: boolean;
  tabIndex?: number;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  onClick,
  hoverable = false,
  variant = 'elevated',
  role,
  'aria-label': ariaLabel,
  'aria-labelledby': ariaLabelledby,
  'aria-describedby': ariaDescribedby,
  'aria-hidden': ariaHidden,
  tabIndex
}) => {
  // 苹果风格的卡片变体
  const variantStyles = {
    elevated: 'bg-white rounded-apple shadow-apple-sm border border-[#E8E8ED]',
    filled: 'bg-[#F5F5F7] rounded-apple',
    outlined: 'bg-white rounded-apple border border-[#D2D2D7]',
    plain: 'bg-transparent'
  };

  return (
    <div
      className={`
        ${variantStyles[variant]}
        p-6
        ${hoverable ? 'transition-apple hover:shadow-apple hover:translate-y-[-2px]' : ''}
        ${onClick ? 'cursor-pointer' : ''}
        ${className}
      `}
      onClick={onClick}
      role={role}
      aria-label={ariaLabel}
      aria-labelledby={ariaLabelledby}
      aria-describedby={ariaDescribedby}
      aria-hidden={ariaHidden}
      tabIndex={tabIndex}
    >
      {children}
    </div>
  );
};

interface CardHeaderProps {
  children: React.ReactNode;
  className?: string;
  withBorder?: boolean;
}

export const CardHeader: React.FC<CardHeaderProps> = ({
  children,
  className = '',
  withBorder = false
}) => {
  return (
    <div className={`
      px-6 py-4 -mx-6 -mt-6 mb-6
      ${withBorder ? 'border-b border-[#E8E8ED]' : ''}
      ${className}
    `}>
      {children}
    </div>
  );
};

interface CardContentProps {
  children: React.ReactNode;
  className?: string;
  padded?: boolean;
}

export const CardContent: React.FC<CardContentProps> = ({
  children,
  className = '',
  padded = false
}) => {
  return (
    <div className={`
      ${padded ? 'px-2 py-1' : ''}
      ${className}
    `}>
      {children}
    </div>
  );
};

interface CardFooterProps {
  children: React.ReactNode;
  className?: string;
  withBorder?: boolean;
}

export const CardFooter: React.FC<CardFooterProps> = ({
  children,
  className = '',
  withBorder = true
}) => {
  return (
    <div className={`
      mt-6 pt-4 px-6 -mx-6 -mb-6
      ${withBorder ? 'border-t border-[#E8E8ED]' : ''}
      ${className}
    `}>
      {children}
    </div>
  );
};
