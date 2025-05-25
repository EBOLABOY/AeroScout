'use client';

import React from 'react';

type AlertVariant = 'info' | 'success' | 'warning' | 'error';

interface AlertProps {
  title?: string;
  children: React.ReactNode;
  variant?: AlertVariant;
  icon?: React.ReactNode;
  className?: string;
  onClose?: () => void; // 新增 onClose 属性
}

const Alert: React.FC<AlertProps> = ({
  title, 
  children, 
  variant = 'info',
  icon,
  className = '',
  onClose
}) => {
  // 定义不同变体的样式
  const variantStyles = {
    info: {
      container: 'bg-[#E3F2FD] border-[#2997FF]',
      title: 'text-[#0077ED]',
      content: 'text-[#0077ED]',
      icon: (
        <svg className="h-5 w-5 text-[#2997FF]" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
        </svg>
      )
    },
    success: {
      container: 'bg-[#E9F7EF] border-[#34C759]',
      title: 'text-[#28A745]',
      content: 'text-[#28A745]',
      icon: (
        <svg className="h-5 w-5 text-[#34C759]" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
        </svg>
      )
    },
    warning: {
      container: 'bg-[#FFF8E6] border-[#FF9500]',
      title: 'text-[#CC7700]',
      content: 'text-[#CC7700]',
      icon: (
        <svg className="h-5 w-5 text-[#FF9500]" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
        </svg>
      )
    },
    error: {
      container: 'bg-[#FFEBEB] border-[#FF3B30]',
      title: 'text-[#D70015]',
      content: 'text-[#D70015]',
      icon: (
        <svg className="h-5 w-5 text-[#FF3B30]" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
        </svg>
      )
    }
  };

  const styles = variantStyles[variant];

  return (
    <div className={`border-l-4 p-4 rounded-r-md ${styles.container} ${className} relative`}>
      <div className="flex">
        <div className="flex-shrink-0">
          {icon || styles.icon}
        </div>
        <div className="ml-3 flex-grow">
          {title && (
            <h3 className={`text-sm font-semibold ${styles.title}`}>{title}</h3>
          )}
          <div className={`mt-2 text-sm ${styles.content}`}>
            {children}
          </div>
        </div>
        {onClose && (
          <div className="ml-auto pl-3">
            <div className="-mx-1.5 -my-1.5">
              <button
                type="button"
                onClick={onClose}
                className={`inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2
                            ${variant === 'info' ? 'bg-[#E3F2FD] text-[#0077ED] hover:bg-[#BDE0FE] focus:ring-offset-[#E3F2FD] focus:ring-[#2997FF]' : ''}
                            ${variant === 'success' ? 'bg-[#E9F7EF] text-[#28A745] hover:bg-[#D4F0E0] focus:ring-offset-[#E9F7EF] focus:ring-[#34C759]' : ''}
                            ${variant === 'warning' ? 'bg-[#FFF8E6] text-[#CC7700] hover:bg-[#FFEFCF] focus:ring-offset-[#FFF8E6] focus:ring-[#FF9500]' : ''}
                            ${variant === 'error' ? 'bg-[#FFEBEB] text-[#D70015] hover:bg-[#FFD6D6] focus:ring-offset-[#FFEBEB] focus:ring-[#FF3B30]' : ''}
                          `}
                aria-label="Dismiss"
              >
                <span className="sr-only">Dismiss</span>
                <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Alert;
