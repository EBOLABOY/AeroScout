import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * 合并多个className字符串，并解决冲突
 * 结合clsx和tailwind-merge功能
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}