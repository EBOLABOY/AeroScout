import React from 'react';
import { cn } from '@/lib/utils';

interface SkeletonProps {
  className?: string;
  height?: string | number;
  width?: string | number;
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'full' | 'apple';
  animate?: boolean;
}

/**
 * 通用骨架屏组件
 */
const Skeleton: React.FC<SkeletonProps> = ({
  className,
  height,
  width,
  rounded = 'md',
  animate = true,
}) => {
  const roundedMap = {
    none: 'rounded-none',
    sm: 'rounded-sm',
    md: 'rounded-md',
    lg: 'rounded-lg',
    full: 'rounded-full',
    apple: 'rounded-apple',
  };

  return (
    <div
      className={cn(
        'bg-gray-200',
        animate && 'animate-pulse',
        roundedMap[rounded],
        className
      )}
      style={{
        height: height ? (typeof height === 'number' ? `${height}px` : height) : undefined,
        width: width ? (typeof width === 'number' ? `${width}px` : width) : undefined,
      }}
    />
  );
};

/**
 * 文本骨架屏组件
 */
export const TextSkeleton: React.FC<SkeletonProps & { lines?: number }> = ({
  className,
  height = '1rem',
  width = '100%',
  rounded = 'md',
  animate = true,
  lines = 1,
}) => {
  return (
    <div className="space-y-2">
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          className={className}
          height={height}
          width={i === lines - 1 && lines > 1 ? '80%' : width}
          rounded={rounded}
          animate={animate}
        />
      ))}
    </div>
  );
};

/**
 * 搜索记录骨架屏组件
 */
export const SearchRecordSkeleton: React.FC = () => {
  return (
    <div className="p-4 border border-[#E8E8ED] rounded-apple">
      <div className="flex justify-between items-start">
        <div>
          <div className="flex items-center">
            <Skeleton width={80} height={20} rounded="md" />
            <Skeleton className="mx-2" width={16} height={16} rounded="none" />
            <Skeleton width={80} height={20} rounded="md" />
          </div>
          <div className="mt-1 flex items-center">
            <Skeleton width={120} height={16} rounded="md" />
          </div>
        </div>
        <div className="text-right">
          <Skeleton width={60} height={14} rounded="md" />
          <div className="mt-2 flex items-center space-x-2">
            <Skeleton width={100} height={30} rounded="md" />
            <Skeleton width={30} height={30} rounded="full" />
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * API使用统计骨架屏组件
 */
export const ApiUsageSkeleton: React.FC = () => {
  return (
    <div className="space-y-4">
      <div>
        <div className="flex justify-between mb-1">
          <Skeleton width={60} height={16} rounded="md" />
          <Skeleton width={40} height={16} rounded="md" />
        </div>
        <Skeleton height={8} width="100%" rounded="full" />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Skeleton width={80} height={16} rounded="md" className="mb-1" />
          <Skeleton width={60} height={20} rounded="md" />
        </div>
        <div>
          <Skeleton width={80} height={16} rounded="md" className="mb-1" />
          <Skeleton width={60} height={20} rounded="md" />
        </div>
      </div>

      <div>
        <Skeleton width={80} height={16} rounded="md" className="mb-1" />
        <Skeleton width={120} height={20} rounded="md" />
      </div>
    </div>
  );
};

/**
 * API使用图表骨架屏组件
 */
export const ChartSkeleton: React.FC = () => {
  // 使用固定的预定义高度值数组替代随机生成
  const barHeights = [25, 45, 65, 35, 75, 55, 40];
  
  // 客户端渲染时的随机高度
  const [heights, setHeights] = React.useState<number[]>(barHeights);
  
  // 使用useEffect确保只在客户端渲染后更新随机高度
  React.useEffect(() => {
    // 客户端渲染后生成新的随机高度
    const randomHeights = Array.from({ length: 7 }).map(() => 10 + Math.random() * 90);
    setHeights(randomHeights);
  }, []);
  
  return (
    <div className="h-[250px] w-full">
      <div className="flex h-full w-full flex-col">
        <div className="flex justify-between mb-4">
          <Skeleton width={100} height={20} rounded="md" />
          <Skeleton width={60} height={20} rounded="md" />
        </div>
        <div className="flex-1 flex items-end space-x-2">
          {heights.map((height, i) => (
            <div key={i} className="flex-1 flex flex-col justify-end">
              <Skeleton
                height={`${height}%`}
                width="100%"
                rounded="sm"
                className="mb-2"
              />
              <Skeleton height={16} width="100%" rounded="sm" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

/**
 * 邀请码骨架屏组件
 */
export const InvitationCodeSkeleton: React.FC = () => {
  return (
    <div className="p-4 border border-[#E8E8ED] rounded-apple">
      <div className="flex justify-between items-center">
        <div>
          <Skeleton width={120} height={20} rounded="md" />
          <Skeleton width={160} height={16} rounded="md" className="mt-1" />
        </div>
        <div>
          <Skeleton width={60} height={24} rounded="full" />
        </div>
      </div>
    </div>
  );
};

export default Skeleton;