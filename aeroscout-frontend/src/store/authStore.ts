import { create } from 'zustand';
import apiClient from '@/lib/apiService'; // 导入 apiClient

interface User {
  id: number;
  email: string;
  is_admin: boolean; // 后端会返回 is_admin
  // 其他用户信息字段
}

interface AuthState {
  isAuthenticated: boolean;
  accessToken: string | null;
  currentUser: User | null;
  isAdmin: boolean; // 新增 isAdmin 状态
  setAuthenticated: (status: boolean) => void;
  setAccessToken: (token: string | null) => void;
  setCurrentUser: (user: User | null) => void;
  logout: () => void;
  fetchCurrentUser: () => Promise<User | null>; // 添加 fetchCurrentUser
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  accessToken: null,
  currentUser: null,
  isAdmin: false, // 初始化 isAdmin
  setAuthenticated: (status) => set({ isAuthenticated: status }),
  setAccessToken: (token) => set({ accessToken: token }),
  setCurrentUser: (user) =>
    set({
      currentUser: user,
      isAdmin: user ? user.is_admin : false,
    }),
  logout: () => {
    localStorage.removeItem('access_token');
    set({
      isAuthenticated: false,
      accessToken: null,
      currentUser: null,
      isAdmin: false, // 登出时重置 isAdmin
    });
  },
  fetchCurrentUser: async () => {
    try {
      const response = await apiClient.get<User>('/users/me');
      if (response.data) {
        set({
          currentUser: response.data,
          isAdmin: response.data.is_admin,
          isAuthenticated: true, // 获取用户信息成功，也应视为已认证
        });
        return response.data;
      }
      return null;
    } catch (error) {
      console.error('Failed to fetch current user:', error);
      localStorage.removeItem('access_token');
      set({
        currentUser: null,
        isAuthenticated: false,
        accessToken: null,
        isAdmin: false,
      });
      return null;
    }
  },
}));