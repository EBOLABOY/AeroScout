'use client';

import React from 'react';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  variant?: 'filled' | 'outlined' | 'minimal';
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({
    label,
    error,
    helperText,
    className = '',
    icon,
    iconPosition = 'right',
    variant = 'filled',
    ...props
  }, ref) => {
    // 苹果风格的输入框变体
    const variantStyles = {
      filled: `
        w-full px-4 py-2.5 bg-[#F5F5F7] border-none rounded-lg text-[#1D1D1F]
        placeholder:text-[#8E8E93]
        focus:outline-none focus:bg-[#E8E8ED] focus:ring-0
        transition-apple
      `,
      outlined: `
        w-full px-4 py-2.5 bg-white border rounded-lg text-[#1D1D1F]
        placeholder:text-[#8E8E93]
        focus:outline-none focus:ring-2 focus:ring-[#0071E3] focus:border-transparent
        transition-apple
        ${error ? 'border-[#FF3B30] focus:ring-[#FF3B30]' : 'border-[#D2D2D7]'}
      `,
      minimal: `
        w-full px-1 py-2 bg-transparent border-b text-[#1D1D1F]
        placeholder:text-[#8E8E93]
        focus:outline-none focus:border-b-2 focus:border-[#0071E3]
        transition-apple
        ${error ? 'border-[#FF3B30] focus:border-[#FF3B30]' : 'border-[#D2D2D7]'}
      `
    };

    return (
      <div className="w-full">
        {label && (
          <label
            htmlFor={props.id}
            className="block text-[13px] font-medium text-[#1D1D1F] mb-1.5"
          >
            {label}
          </label>
        )}

        <div className="relative">
          <input
            ref={ref}
            className={`
              ${variantStyles[variant]}
              ${props.disabled ? 'opacity-50 cursor-not-allowed' : ''}
              ${icon && iconPosition === 'left' ? 'pl-10' : ''}
              ${icon && iconPosition === 'right' ? 'pr-10' : ''}
              ${className}
            `}
            {...props}
          />

          {icon && (
            <div
              className={`absolute top-1/2 transform -translate-y-1/2 text-[#8E8E93] pointer-events-none
                ${iconPosition === 'left' ? 'left-3' : 'right-3'}
              `}
            >
              {icon}
            </div>
          )}
        </div>

        {error && (
          <p className="mt-1.5 text-[13px] text-[#FF3B30] animate-fadeIn">{error}</p>
        )}

        {helperText && !error && (
          <p className="mt-1.5 text-[13px] text-[#8E8E93]">{helperText}</p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";

export default Input;
