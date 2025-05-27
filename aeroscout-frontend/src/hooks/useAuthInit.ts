import { useEffect, useState } from 'react';
import { useAuthStore } from '../store/authStore';

export const useAuthInit = () => {
  const { isAuthenticated, setAccessToken, fetchCurrentUser } = useAuthStore();
  const [isInitialized, setIsInitialized] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // 检查localStorage中是否有token
        if (typeof window !== 'undefined') {
          const token = localStorage.getItem('access_token');
          
          if (token && !isAuthenticated) {
            // 设置token到store
            setAccessToken(token);
            
            // 尝试获取用户信息
            try {
              await fetchCurrentUser();
            } catch (error) {
              console.error('获取用户信息失败:', error);
              // 如果获取用户信息失败，清除token
              setAccessToken(null);
              localStorage.removeItem('access_token');
            }
          }
        }
        
        setIsInitialized(true);
      } catch (error) {
        console.error('认证初始化失败:', error);
        setIsInitialized(true);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []); // 只在组件挂载时执行一次

  return { isInitialized, isLoading };
};
