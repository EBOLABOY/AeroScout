'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useAuthStore } from '@/store/authStore';
import { Card, CardHeader, CardContent, CardFooter } from '@/components/common/Card';
import Button from '@/components/common/Button';
import Input from '@/components/common/Input';
import Link from 'next/link';
import { useAlertStore } from '@/store/alertStore';
import {
  SearchRecordSkeleton,
  ApiUsageSkeleton,
  ChartSkeleton,
  InvitationCodeSkeleton,
  TextSkeleton
} from '@/components/common/Skeleton';
import {
  getUserRecentSearches,
  getUserApiUsageStats,
  getUserInvitationCodes,
  getUserApiUsageHistory,
  deleteSearchRecord,
  toggleSearchFavorite,
  getFilteredSearches
} from '@/lib/apiService';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, Cell
} from 'recharts';

// 根据一天中的时间返回合适的问候语
const getGreetingByTime = (): string => {
  const hour = new Date().getHours();
  if (hour >= 5 && hour < 12) {
    return '早上好';
  } else if (hour >= 12 && hour < 18) {
    return '下午好';
  } else {
    return '晚上好';
  }
};

// 格式化日期
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('zh-CN', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  }).format(date);
};

// 定义接口
interface RecentSearch {
  id: string;
  from: string;
  to: string;
  date: string;
  searchedAt: string;
  passengers: number;
  isFavorite: boolean;
}

interface ApiUsage {
  poiCallsToday: number;
  flightCallsToday: number;
  poiDailyLimit: number;
  flightDailyLimit: number;
  totalCalls: number;
  remainingCalls: number;
  usagePercentage: number;
  resetDate: string;
  isNearLimit: boolean;
}

interface DailyApiUsage {
  date: string;
  poiCalls: number;
  flightCalls: number;
  totalCalls: number;
}

interface InvitationCode {
  id: number;
  code: string;
  isUsed: boolean;
  createdAt: string;
  usedAt: string | null;
}

// 格式化简短日期 (MM-DD)
const formatShortDate = (dateString: string): string => {
  const date = new Date(dateString);
  return `${date.getMonth() + 1}-${date.getDate()}`;
};

// 获取相对时间，例如"3天前"
const getRelativeTime = (dateTimeString: string): string => {
  const date = new Date(dateTimeString);
  const now = new Date();
  const diffInDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
  
  if (diffInDays === 0) {
    return '今天';
  } else if (diffInDays === 1) {
    return '昨天';
  } else if (diffInDays < 7) {
    return `${diffInDays}天前`;
  } else {
    return formatDate(dateTimeString);
  }
};

// 搜索记录筛选组件
const SearchFilter = ({
  onFilterChange,
  onSortChange,
  onFavoritesToggle,
  showFavoritesOnly,
}: {
  onFilterChange: (from: string, to: string) => void;
  onSortChange: (sortBy: string) => void;
  onFavoritesToggle: () => void;
  showFavoritesOnly: boolean;
}) => {
  const [fromFilter, setFromFilter] = useState('');
  const [toFilter, setToFilter] = useState('');

  const handleFromChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFromFilter(e.target.value);
  };

  const handleToChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setToFilter(e.target.value);
  };

  const handleApplyFilter = () => {
    onFilterChange(fromFilter, toFilter);
  };

  const handleClearFilter = () => {
    setFromFilter('');
    setToFilter('');
    onFilterChange('', '');
  };

  return (
    <div className="mb-4 p-4 border border-[#E8E8ED] rounded-apple bg-white">
      <div className="text-sm font-medium text-[#1D1D1F] mb-3">筛选和排序</div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div>
          <Input
            label="出发地"
            placeholder="输入城市或机场名称"
            value={fromFilter}
            onChange={handleFromChange}
          />
        </div>
        <div>
          <Input
            label="目的地"
            placeholder="输入城市或机场名称"
            value={toFilter}
            onChange={handleToChange}
          />
        </div>
      </div>
      <div className="flex items-center justify-between mt-4">
        <div className="flex items-center gap-3">
          <Button
            variant="secondary"
            size="sm"
            onClick={handleApplyFilter}
          >
            应用筛选
          </Button>
          <Button
            variant="tertiary"
            size="sm"
            onClick={handleClearFilter}
          >
            清除筛选
          </Button>
        </div>
        <div className="flex items-center gap-3">
          <select
            className="text-sm border border-[#E8E8ED] rounded-md px-2 py-1 bg-white focus:outline-none focus:ring-1 focus:ring-[#0071E3]"
            onChange={(e) => onSortChange(e.target.value)}
            defaultValue="searched_at_desc"
          >
            <option value="searched_at_desc">最近搜索时间</option>
            <option value="searched_at_asc">最早搜索时间</option>
            <option value="date_asc">最早出发日期</option>
            <option value="date_desc">最晚出发日期</option>
          </select>
          <div
            className="flex items-center text-sm cursor-pointer"
            onClick={onFavoritesToggle}
          >
            <input
              type="checkbox"
              checked={showFavoritesOnly}
              readOnly
              className="mr-2 h-4 w-4 text-[#0071E3] rounded border-[#E8E8ED] focus:ring-[#0071E3]"
            />
            <span>只显示收藏</span>
          </div>
        </div>
      </div>
    </div>
  );
};

// 单条搜索记录组件
const SearchRecordItem = ({
  search,
  onDelete,
  onToggleFavorite
}: {
  search: RecentSearch;
  onDelete: (id: string) => void;
  onToggleFavorite: (id: string, isFavorite: boolean) => void;
}) => {
  const handleDelete = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    onDelete(search.id);
  };

  const handleToggleFavorite = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    onToggleFavorite(search.id, !search.isFavorite);
  };

  return (
    <div
      className="p-4 border border-[#E8E8ED] rounded-apple hover:shadow-apple-sm transition-apple"
    >
      <div className="flex justify-between items-start">
        <div>
          <div className="flex items-center text-[#1D1D1F] font-medium">
            <span>{search.from}</span>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="mx-2"
            >
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
            <span>{search.to}</span>
            <button
              onClick={handleToggleFavorite}
              className="ml-2 text-[#8E8E93] hover:text-[#0071E3]"
              title={search.isFavorite ? "取消收藏" : "收藏"}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill={search.isFavorite ? "currentColor" : "none"}
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className={search.isFavorite ? "text-[#FF9500]" : ""}
              >
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
              </svg>
            </button>
          </div>
          <div className="mt-1 flex items-center text-sm text-[#8E8E93]">
            <span>{formatDate(search.date)}</span>
            <span className="mx-2">•</span>
            <span>{search.passengers} 位乘客</span>
          </div>
        </div>
        <div className="text-right">
          <div className="text-xs text-[#8E8E93]">
            {getRelativeTime(search.searchedAt)}
          </div>
          <div className="mt-2 flex items-center space-x-2">
            <Link href={`/search?from=${search.from}&to=${search.to}&date=${search.date}&passengers=${search.passengers}`}>
              <Button
                variant="secondary"
                size="sm"
                icon={
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <polyline points="23 4 23 10 17 10"></polyline>
                    <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
                  </svg>
                }
              >
                再次搜索
              </Button>
            </Link>
            <button
              onClick={handleDelete}
              className="p-2 text-[#FF3B30] hover:bg-[#FFF1F0] rounded-full"
              title="删除"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                <line x1="10" y1="11" x2="10" y2="17"></line>
                <line x1="14" y1="11" x2="14" y2="17"></line>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// API使用趋势图表组件
const ApiUsageTrendChart = ({ usageHistory }: { usageHistory: DailyApiUsage[] }) => {
  const formattedData = usageHistory.map(day => ({
    ...day,
    date: formatShortDate(day.date),
  }));

  return (
    <Card variant="elevated" className="mb-6">
      <CardHeader withBorder>
        <h2 className="text-lg font-medium text-[#1D1D1F]">API使用趋势</h2>
      </CardHeader>
      <CardContent>
        <div className="h-[250px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={formattedData}
              margin={{ top: 10, right: 10, left: 0, bottom: 10 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#E8E8ED" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip
                formatter={(value, name) => {
                  const formattedName = name === 'poiCalls'
                    ? 'POI调用'
                    : name === 'flightCalls'
                      ? '航班调用'
                      : '总调用';
                  return [value, formattedName];
                }}
              />
              <Legend
                formatter={(value) => {
                  return value === 'poiCalls'
                    ? 'POI调用'
                    : value === 'flightCalls'
                      ? '航班调用'
                      : '总调用';
                }}
              />
              <Line
                type="monotone"
                dataKey="totalCalls"
                stroke="#0071E3"
                strokeWidth={2}
                activeDot={{ r: 8 }}
              />
              <Line
                type="monotone"
                dataKey="poiCalls"
                stroke="#5AC8FA"
                strokeWidth={2}
              />
              <Line
                type="monotone"
                dataKey="flightCalls"
                stroke="#FF9500"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
};

// API使用详情组件
const ApiUsageDetails = ({ apiUsage }: { apiUsage: ApiUsage }) => {
  // 计算POI和Flight调用的百分比
  const poiCallsPercent = Math.round((apiUsage.poiCallsToday / apiUsage.poiDailyLimit) * 100);
  const flightCallsPercent = Math.round((apiUsage.flightCallsToday / apiUsage.flightDailyLimit) * 100);
  
  // 为柱状图准备数据
  const barData = [
    {
      name: 'POI',
      value: apiUsage.poiCallsToday,
      limit: apiUsage.poiDailyLimit,
      percent: poiCallsPercent
    },
    {
      name: '航班',
      value: apiUsage.flightCallsToday,
      limit: apiUsage.flightDailyLimit,
      percent: flightCallsPercent
    }
  ];

  // 根据使用百分比确定颜色
  const getBarColor = (percent: number) => {
    if (percent >= 90) return '#FF3B30'; // 危险级别
    if (percent >= 70) return '#FF9500'; // 警告级别
    return '#34C759'; // 正常级别
  };

  return (
    <Card variant="elevated" className="mb-6">
      <CardHeader withBorder>
        <h2 className="text-lg font-medium text-[#1D1D1F]">API使用详情</h2>
      </CardHeader>
      <CardContent>
        <div className="mb-4">
          <div className="flex justify-between mb-1">
            <span className="text-sm text-[#8E8E93]">总体使用率</span>
            <span className={`text-sm font-medium ${
              apiUsage.usagePercentage >= 90 ? 'text-[#FF3B30]' :
              apiUsage.usagePercentage >= 70 ? 'text-[#FF9500]' :
              'text-[#34C759]'
            }`}>
              {apiUsage.usagePercentage}%
            </span>
          </div>
          <div className="w-full bg-[#E8E8ED] rounded-full h-2">
            <div
              className={`h-2 rounded-full ${
                apiUsage.usagePercentage >= 90 ? 'bg-[#FF3B30]' :
                apiUsage.usagePercentage >= 70 ? 'bg-[#FF9500]' :
                'bg-[#34C759]'
              }`}
              style={{ width: `${apiUsage.usagePercentage}%` }}
            ></div>
          </div>
        </div>

        <div className="mb-4 h-[180px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={barData}
              margin={{ top: 10, right: 10, left: 10, bottom: 10 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#E8E8ED" vertical={false} />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip
                formatter={(value, name, props) => {
                  const { payload } = props;
                  return [`${value}/${payload.limit} (${payload.percent}%)`, name];
                }}
              />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {barData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getBarColor(entry.percent)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <h3 className="text-sm font-medium text-[#8E8E93]">剩余调用</h3>
            <p className="text-[#1D1D1F]">{apiUsage.remainingCalls}</p>
          </div>
          <div>
            <h3 className="text-sm font-medium text-[#8E8E93]">总调用限制</h3>
            <p className="text-[#1D1D1F]">{apiUsage.totalCalls}</p>
          </div>
        </div>
        <div className="mt-3">
          <h3 className="text-sm font-medium text-[#8E8E93]">重置时间</h3>
          <p className="text-[#1D1D1F]">{formatDate(apiUsage.resetDate)}</p>
        </div>

        {apiUsage.isNearLimit && (
          <div className="mt-4 p-3 bg-[#FFF5EB] border border-[#FF9500] rounded-apple text-sm text-[#FF9500]">
            <div className="flex items-center">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="mr-2"
              >
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
              您的API使用量接近限额，请注意合理使用以避免额度耗尽
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

const DashboardPage = () => {
  const { isAuthenticated } = useAuth(true);
  const { currentUser, logout } = useAuthStore();
  const { showAlert } = useAlertStore();
  const [showUserMenu, setShowUserMenu] = useState(false);
  
  // 数据状态
  const [recentSearches, setRecentSearches] = useState<RecentSearch[]>([]);
  const [apiUsage, setApiUsage] = useState<ApiUsage | null>(null);
  const [apiUsageHistory, setApiUsageHistory] = useState<DailyApiUsage[]>([]);
  const [invitationCodes, setInvitationCodes] = useState<InvitationCode[]>([]);
  
  // 筛选和排序状态
  const [fromFilter, setFromFilter] = useState('');
  const [toFilter, setToFilter] = useState('');
  const [sortBy, setSortBy] = useState('searched_at_desc');
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);
  
  // 加载状态
  const [isLoadingSearches, setIsLoadingSearches] = useState(true);
  const [isLoadingUsage, setIsLoadingUsage] = useState(true);
  const [isLoadingHistory, setIsLoadingHistory] = useState(true);
  const [isLoadingCodes, setIsLoadingCodes] = useState(true);
  
  // 错误状态
  const [searchesError, setSearchesError] = useState<string | null>(null);
  const [usageError, setUsageError] = useState<string | null>(null);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [codesError, setCodesError] = useState<string | null>(null);

  // 从API获取数据
  useEffect(() => {
    const fetchRecentSearches = async () => {
      try {
        setIsLoadingSearches(true);
        const response = await getUserRecentSearches();
        
        // 转换数据格式以匹配前端组件需要的格式
        const formattedSearches = response.data.map(item => ({
          id: item.id,
          from: item.from_location,
          to: item.to_location,
          date: item.date,
          searchedAt: item.searched_at,
          passengers: item.passengers,
          isFavorite: item.is_favorite || false
        }));
        
        setRecentSearches(formattedSearches);
        setSearchesError(null);
      } catch (error) {
        console.error('获取最近搜索记录失败:', error);
        setSearchesError('获取搜索记录失败，请稍后再试');
      } finally {
        setIsLoadingSearches(false);
      }
    };

    const fetchApiUsage = async () => {
      try {
        setIsLoadingUsage(true);
        const response = await getUserApiUsageStats();
        const data = response.data;
        
        // 计算总调用次数、剩余次数和百分比
        const totalPoiCalls = data.poi_daily_limit;
        const totalFlightCalls = data.flight_daily_limit;
        const totalCalls = totalPoiCalls + totalFlightCalls;
        const usedPoiCalls = data.poi_calls_today;
        const usedFlightCalls = data.flight_calls_today;
        const totalUsedCalls = usedPoiCalls + usedFlightCalls;
        const remainingCalls = totalCalls - totalUsedCalls;
        const usagePercentage = Math.round((totalUsedCalls / totalCalls) * 100);
        
        // 转换为前端需要的格式
        setApiUsage({
          poiCallsToday: data.poi_calls_today,
          flightCallsToday: data.flight_calls_today,
          poiDailyLimit: data.poi_daily_limit,
          flightDailyLimit: data.flight_daily_limit,
          totalCalls: totalCalls,
          remainingCalls: remainingCalls,
          usagePercentage: usagePercentage,
          resetDate: data.reset_date,
          isNearLimit: data.is_near_limit || usagePercentage > 80
        });
        
        setUsageError(null);
      } catch (error) {
        console.error('获取API使用统计失败:', error);
        setUsageError('获取API使用统计失败，请稍后再试');
      } finally {
        setIsLoadingUsage(false);
      }
    };

    const fetchInvitationCodes = async () => {
      try {
        setIsLoadingCodes(true);
        const response = await getUserInvitationCodes();
        
        // 转换数据格式
        const formattedCodes = response.data.map(item => ({
          id: item.id,
          code: item.code,
          isUsed: item.is_used,
          createdAt: item.created_at,
          usedAt: item.used_at
        }));
        
        setInvitationCodes(formattedCodes);
        setCodesError(null);
      } catch (error) {
        console.error('获取邀请码失败:', error);
        setCodesError('获取邀请码失败，请稍后再试');
      } finally {
        setIsLoadingCodes(false);
      }
    };

    const fetchApiUsageHistory = async () => {
      try {
        setIsLoadingHistory(true);
        // 尝试从API获取数据
        try {
          const response = await getUserApiUsageHistory(7);
          
          // 转换数据格式
          const formattedHistory = response.data.map(item => ({
            date: item.date,
            poiCalls: item.poi_calls,
            flightCalls: item.flight_calls,
            totalCalls: item.total_calls
          }));
          
          setApiUsageHistory(formattedHistory);
          setHistoryError(null);
        } catch (apiError) {
          console.error('获取API使用历史失败:', apiError);
          // 使用模拟数据作为备用
          const { apiUsageHistory } = await import('@/__mocks__/mockDashboardData');
          setApiUsageHistory(apiUsageHistory);
          setHistoryError('无法获取实时API使用历史，显示模拟数据');
        }
      } finally {
        setIsLoadingHistory(false);
      }
    };

    if (isAuthenticated) {
      fetchRecentSearches();
      fetchApiUsage();
      fetchApiUsageHistory();
      fetchInvitationCodes();
    }
  }, [isAuthenticated]);
  
  // 处理搜索筛选和排序
  const handleFilterChange = (from: string, to: string) => {
    setFromFilter(from);
    setToFilter(to);
    applyFilters(from, to, sortBy, showFavoritesOnly);
  };

  const handleSortChange = (newSortBy: string) => {
    setSortBy(newSortBy);
    applyFilters(fromFilter, toFilter, newSortBy, showFavoritesOnly);
  };

  const handleFavoritesToggle = () => {
    const newShowFavoritesOnly = !showFavoritesOnly;
    setShowFavoritesOnly(newShowFavoritesOnly);
    applyFilters(fromFilter, toFilter, sortBy, newShowFavoritesOnly);
  };

  // 应用筛选和排序
  const applyFilters = async (
    from: string,
    to: string,
    sort: string,
    favoritesOnly: boolean
  ) => {
    try {
      setIsLoadingSearches(true);
      
      // 尝试从API获取数据
      try {
        // 解析排序选项
        const [sortField, sortOrder] = sort.split('_');
        
        const response = await getFilteredSearches({
          from,
          to,
          sort_by: sortField as "date" | "searched_at",
          order: sortOrder as "asc" | "desc",
          favorites_only: favoritesOnly
        });
        
        // 转换数据格式
        const formattedSearches = response.data.map(item => ({
          id: item.id,
          from: item.from_location,
          to: item.to_location,
          date: item.date,
          searchedAt: item.searched_at,
          passengers: item.passengers,
          isFavorite: item.is_favorite || false
        }));
        
        setRecentSearches(formattedSearches);
        setSearchesError(null);
      } catch (apiError) {
        console.error('筛选搜索记录失败:', apiError);
        
        // 本地筛选和排序逻辑作为备用
        let filteredSearches = [...recentSearches];
        
        if (from) {
          filteredSearches = filteredSearches.filter(
            search => search.from.toLowerCase().includes(from.toLowerCase())
          );
        }
        
        if (to) {
          filteredSearches = filteredSearches.filter(
            search => search.to.toLowerCase().includes(to.toLowerCase())
          );
        }
        
        if (favoritesOnly) {
          filteredSearches = filteredSearches.filter(search => search.isFavorite);
        }
        
        const [field, order] = sort.split('_');
        filteredSearches.sort((a, b) => {
          if (field === 'searched_at') {
            return order === 'asc'
              ? new Date(a.searchedAt).getTime() - new Date(b.searchedAt).getTime()
              : new Date(b.searchedAt).getTime() - new Date(a.searchedAt).getTime();
          } else { // date
            return order === 'asc'
              ? new Date(a.date).getTime() - new Date(b.date).getTime()
              : new Date(b.date).getTime() - new Date(a.date).getTime();
          }
        });
        
        setRecentSearches(filteredSearches);
        setSearchesError('使用本地筛选（API调用失败）');
      }
    } finally {
      setIsLoadingSearches(false);
    }
  };

  // 处理删除搜索记录
  const handleDeleteSearch = async (id: string) => {
    try {
      showAlert('正在删除搜索记录...', 'info');
      await deleteSearchRecord(id);
      
      // 从本地状态中移除
      setRecentSearches(current => current.filter(search => search.id !== id));
      showAlert('搜索记录已删除', 'success');
    } catch (error) {
      console.error('删除搜索记录失败:', error);
      showAlert('删除搜索记录失败，请稍后再试', 'error');
    }
  };

  // 处理切换收藏状态
  const handleToggleFavorite = async (id: string, isFavorite: boolean) => {
    try {
      await toggleSearchFavorite(id, isFavorite);
      
      // 更新本地状态
      setRecentSearches(current =>
        current.map(search =>
          search.id === id
            ? { ...search, isFavorite }
            : search
        )
      );
      
      showAlert(
        isFavorite ? '已添加到收藏' : '已从收藏中移除',
        'success'
      );
    } catch (error) {
      console.error('切换收藏状态失败:', error);
      showAlert('操作失败，请稍后再试', 'error');
    }
  };

  // 如果认证钩子正在进行重定向，则不要渲染内容
  if (!isAuthenticated) {
    return null;
  }

  const greeting = getGreetingByTime();

  return (
    <div className="min-h-screen flex flex-col bg-[#F5F5F7]">
      {/* 顶部导航栏 */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto py-3 px-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <Link href="/dashboard" className="flex items-center">
            <span className="text-xl font-semibold text-[#1D1D1F]">AeroScout</span>
          </Link>
          
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center space-x-2 text-sm font-medium text-[#1D1D1F] hover:text-[#0071E3] transition-apple focus:outline-none"
            >
              <div className="h-8 w-8 rounded-full bg-[#0071E3] flex items-center justify-center text-white">
                {currentUser?.email?.charAt(0).toUpperCase() || 'U'}
              </div>
              <span>{currentUser?.email}</span>
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                width="16" 
                height="16" 
                viewBox="0 0 24 24" 
                fill="none" 
                stroke="currentColor" 
                strokeWidth="2" 
                strokeLinecap="round" 
                strokeLinejoin="round"
                className={`transition-transform duration-300 ${showUserMenu ? 'rotate-180' : ''}`}
              >
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </button>
            
            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-apple shadow-apple-sm border border-[#E8E8ED] py-1 z-20">
                {/* 管理员面板链接 - 只对管理员显示 */}
                {currentUser?.is_admin && (
                  <>
                    <Link
                      href="/admin"
                      className="block px-4 py-2 text-sm text-[#0071E3] hover:bg-[#F5F5F7] transition-apple font-medium"
                    >
                      🛠️ 管理员面板
                    </Link>
                    <div className="border-t border-[#E8E8ED] my-1"></div>
                  </>
                )}
                <Link
                  href="/settings"
                  className="block px-4 py-2 text-sm text-[#1D1D1F] hover:bg-[#F5F5F7] transition-apple"
                >
                  账户设置
                </Link>
                <Link
                  href="/search-history"
                  className="block px-4 py-2 text-sm text-[#1D1D1F] hover:bg-[#F5F5F7] transition-apple"
                >
                  搜索历史
                </Link>
                <button
                  onClick={() => {
                    logout();
                    localStorage.removeItem('access_token');
                    window.location.href = '/auth/login';
                  }}
                  className="block w-full text-left px-4 py-2 text-sm text-[#FF3B30] hover:bg-[#F5F5F7] transition-apple"
                >
                  登出
                </button>
              </div>
            )}
          </div>
        </div>
      </header>

      <main className="flex-1 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* 欢迎与概览区 */}
          <div className="mb-8">
            <Card variant="plain" className="bg-transparent p-0">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                <div>
                  {isLoadingUsage ? (
                    <div>
                      <TextSkeleton height={36} width={240} className="mb-2" />
                      <TextSkeleton height={20} width={320} />
                    </div>
                  ) : (
                    <>
                      <h1 className="text-2xl sm:text-3xl font-semibold text-[#1D1D1F]">
                        {greeting}，{currentUser?.email?.split('@')[0] || '用户'}
                      </h1>
                      <p className="mt-2 text-[#8E8E93]">
                        欢迎回到AeroScout，开始探索您的下一段旅程
                      </p>
                    </>
                  )}
                </div>
                <div className="mt-4 md:mt-0">
                  <Link href="/search">
                    <Button 
                      variant="primary" 
                      size="lg"
                      icon={
                        <svg 
                          xmlns="http://www.w3.org/2000/svg" 
                          width="20" 
                          height="20" 
                          viewBox="0 0 24 24" 
                          fill="none" 
                          stroke="currentColor" 
                          strokeWidth="2" 
                          strokeLinecap="round" 
                          strokeLinejoin="round"
                        >
                          <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
                          <path d="M14.05 2a9 9 0 0 1 8 7.94"></path>
                          <path d="M14.05 6A5 5 0 0 1 18 10"></path>
                        </svg>
                      }
                    >
                      开始新的搜索
                    </Button>
                  </Link>
                </div>
              </div>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              {/* 最近搜索记录 */}
              <Card variant="elevated" className="mb-6">
                <CardHeader withBorder>
                  <div className="flex justify-between items-center">
                    <h2 className="text-lg font-medium text-[#1D1D1F]">最近搜索记录</h2>
                    <Link href="/search-history">
                      <Button variant="link" size="sm">
                        查看全部
                      </Button>
                    </Link>
                  </div>
                </CardHeader>
                <CardContent>
                  {/* 搜索筛选器 */}
                  <SearchFilter
                    onFilterChange={handleFilterChange}
                    onSortChange={handleSortChange}
                    onFavoritesToggle={handleFavoritesToggle}
                    showFavoritesOnly={showFavoritesOnly}
                  />
                  
                  {isLoadingSearches ? (
                    <div className="space-y-4">
                      {Array.from({ length: 3 }).map((_, index) => (
                        <SearchRecordSkeleton key={`search-skeleton-${index}`} />
                      ))}
                    </div>
                  ) : searchesError ? (
                    <div className="text-center py-8">
                      <p className="text-[#FF3B30]">{searchesError}</p>
                    </div>
                  ) : recentSearches.length > 0 ? (
                    <div className="space-y-4">
                      {recentSearches.map((search) => (
                        <SearchRecordItem
                          key={search.id}
                          search={search}
                          onDelete={handleDeleteSearch}
                          onToggleFavorite={handleToggleFavorite}
                        />
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-[#8E8E93]">您还没有搜索记录</p>
                      <div className="mt-4">
                        <Link href="/search">
                          <Button variant="secondary" size="sm">
                            开始您的第一次搜索
                          </Button>
                        </Link>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            <div>
              {/* 账户信息与API使用情况 */}
              <Card variant="elevated" className="mb-6">
                <CardHeader withBorder>
                  <h2 className="text-lg font-medium text-[#1D1D1F]">账户信息</h2>
                </CardHeader>
                <CardContent>
                  {isLoadingUsage ? (
                    <div className="space-y-4">
                      {Array.from({ length: 3 }).map((_, index) => (
                        <div key={`account-skeleton-${index}`}>
                          <TextSkeleton height={16} width={80} className="mb-1" />
                          <TextSkeleton height={20} width={160} />
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div>
                        <h3 className="text-sm font-medium text-[#8E8E93]">邮箱</h3>
                        <p className="text-[#1D1D1F]">{currentUser?.email}</p>
                      </div>
                      <div>
                        <h3 className="text-sm font-medium text-[#8E8E93]">用户ID</h3>
                        <p className="text-[#1D1D1F]">{currentUser?.id}</p>
                      </div>
                      <div>
                        <h3 className="text-sm font-medium text-[#8E8E93]">账户类型</h3>
                        <p className="text-[#1D1D1F]">{currentUser?.is_admin ? '管理员' : '标准用户'}</p>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card variant="elevated">
                <CardHeader withBorder>
                  <h2 className="text-lg font-medium text-[#1D1D1F]">API使用情况</h2>
                </CardHeader>
                <CardContent>
                  {isLoadingUsage ? (
                    <ApiUsageSkeleton />
                  ) : usageError ? (
                    <div className="text-center py-8">
                      <p className="text-[#FF3B30]">{usageError}</p>
                    </div>
                  ) : apiUsage ? (
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between mb-1">
                          <span className="text-sm text-[#8E8E93]">已使用</span>
                          <span className="text-sm font-medium text-[#1D1D1F]">
                            {apiUsage.usagePercentage}%
                          </span>
                        </div>
                        <div className="w-full bg-[#E8E8ED] rounded-full h-2">
                          <div
                            className="bg-[#0071E3] h-2 rounded-full"
                            style={{ width: `${apiUsage.usagePercentage}%` }}
                          ></div>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <h3 className="text-sm font-medium text-[#8E8E93]">剩余调用</h3>
                          <p className="text-[#1D1D1F]">{apiUsage.remainingCalls}</p>
                        </div>
                        <div>
                          <h3 className="text-sm font-medium text-[#8E8E93]">总调用次数</h3>
                          <p className="text-[#1D1D1F]">{apiUsage.totalCalls}</p>
                        </div>
                      </div>
                      <div>
                        <h3 className="text-sm font-medium text-[#8E8E93]">重置时间</h3>
                        <p className="text-[#1D1D1F]">{formatDate(apiUsage.resetDate)}</p>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-[#8E8E93]">暂无API使用数据</p>
                    </div>
                  )}
                </CardContent>
                <CardFooter withBorder>
                  <Link href="/settings" className="w-full">
                    <Button 
                      variant="tertiary" 
                      size="sm"
                      fullWidth
                    >
                      升级账户
                    </Button>
                  </Link>
                </CardFooter>
              </Card>
              
              {/* API使用趋势图表 */}
              {isLoadingHistory ? (
                <div className="mt-6">
                  <Card variant="elevated" className="mb-6">
                    <CardHeader withBorder>
                      <h2 className="text-lg font-medium text-[#1D1D1F]">API使用趋势</h2>
                    </CardHeader>
                    <CardContent>
                      <ChartSkeleton />
                    </CardContent>
                  </Card>
                </div>
              ) : historyError ? (
                <div className="mt-6">
                  <Card variant="elevated" className="mb-6">
                    <CardHeader withBorder>
                      <h2 className="text-lg font-medium text-[#1D1D1F]">API使用趋势</h2>
                    </CardHeader>
                    <CardContent>
                      <div className="text-center py-8">
                        <p className="text-[#FF3B30]">{historyError}</p>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ) : apiUsageHistory.length > 0 ? (
                <div className="mt-6">
                  <ApiUsageTrendChart usageHistory={apiUsageHistory} />
                </div>
              ) : null}
              
              {/* API使用详情 */}
              {apiUsage && (
                <div className="mt-6">
                  <ApiUsageDetails apiUsage={apiUsage} />
                </div>
              )}
              
              {/* 邀请码 */}
              <Card variant="elevated" className="mt-6">
                <CardHeader withBorder>
                  <h2 className="text-lg font-medium text-[#1D1D1F]">我的邀请码</h2>
                </CardHeader>
                <CardContent>
                  {isLoadingCodes ? (
                    <div className="space-y-4">
                      {Array.from({ length: 2 }).map((_, index) => (
                        <InvitationCodeSkeleton key={`invitation-skeleton-${index}`} />
                      ))}
                    </div>
                  ) : codesError ? (
                    <div className="text-center py-8">
                      <p className="text-[#FF3B30]">{codesError}</p>
                    </div>
                  ) : invitationCodes.length > 0 ? (
                    <div className="space-y-4">
                      {invitationCodes.map((code) => (
                        <div
                          key={code.id}
                          className="p-4 border border-[#E8E8ED] rounded-apple hover:shadow-apple-sm transition-apple"
                        >
                          <div className="flex justify-between items-center">
                            <div>
                              <div className="text-[#1D1D1F] font-medium">
                                {code.code}
                              </div>
                              <div className="mt-1 text-sm text-[#8E8E93]">
                                创建于 {formatDate(code.createdAt)}
                              </div>
                            </div>
                            <div className="flex items-center">
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                code.isUsed ? 'bg-[#FF3B30]/10 text-[#FF3B30]' : 'bg-[#34C759]/10 text-[#34C759]'
                              }`}>
                                {code.isUsed ? '已使用' : '可用'}
                              </span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-[#8E8E93]">您还没有邀请码</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default DashboardPage;