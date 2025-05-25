'use client';

import React from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'tertiary' | 'link' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  isLoading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({
    className = '',
    variant = 'primary',
    size = 'md',
    fullWidth = false,
    isLoading = false,
    disabled = false,
    icon = null,
    iconPosition = 'left',
    children,
    ...props
  }, ref) => {
    // 基础样式 - 苹果风格
    const baseStyles = "inline-flex items-center justify-center font-medium transition-apple focus:outline-none";

    // 变体样式 - 苹果风格
    const variantStyles = {
      primary: "bg-[#0071E3] text-white hover:bg-[#0077ED] active:bg-[#0051A2] rounded-full shadow-apple-sm",
      secondary: "bg-[#E8E8ED] text-[#1D1D1F] hover:bg-[#D2D2D7] active:bg-[#AEAEB2] rounded-full",
      tertiary: "bg-white border border-[#D2D2D7] text-[#1D1D1F] hover:bg-[#F5F5F7] rounded-full",
      link: "bg-transparent text-[#0071E3] hover:underline",
      danger: "bg-[#FF3B30] text-white hover:bg-[#FF453A] active:bg-[#D70015] rounded-full",
    };

    // 尺寸样式 - 苹果风格
    const sizeStyles = {
      sm: "text-[13px] px-3.5 py-1.5 h-8",
      md: "text-[15px] px-4.5 py-2 h-10",
      lg: "text-[17px] px-6 py-3 h-12",
    };

    // 宽度样式
    const widthStyles = fullWidth ? "w-full" : "";

    // 禁用样式 - 苹果风格
    const disabledStyles = (disabled || isLoading) ? "opacity-30 cursor-not-allowed" : "";

    return (
      <button
        ref={ref}
        className={`
          ${baseStyles}
          ${variantStyles[variant]}
          ${sizeStyles[size]}
          ${widthStyles}
          ${disabledStyles}
          ${className}
        `}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading && (
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        )}
        {icon && iconPosition === 'left' && !isLoading && <span className="mr-2">{icon}</span>}
        <span className={variant === 'primary' ? 'font-medium' : ''}>{children}</span>
        {icon && iconPosition === 'right' && <span className="ml-2">{icon}</span>}
      </button>
    );
  }
);

Button.displayName = "Button";

export default Button;
