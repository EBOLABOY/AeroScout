import { create } from 'zustand';
import apiClient from '../lib/apiService';
import { useAlertStore } from './alertStore';

interface User {
  id: number;
  username: string;
  email: string;
  is_admin: boolean;
}

interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  invitation_code: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

interface AuthState {
  isAuthenticated: boolean;
  accessToken: string | null;
  user: User | null;
  currentUser: User | null; // 保持兼容性
  isAdmin: boolean;
  setAuthenticated: (status: boolean) => void;
  setAccessToken: (token: string | null) => void;
  setCurrentUser: (user: User | null) => void;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (userData: RegisterRequest) => Promise<void>;
  logout: () => void;
  fetchCurrentUser: () => Promise<User | null>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  isAuthenticated: false,
  accessToken: null,
  user: null,
  currentUser: null,
  isAdmin: false,

  setAuthenticated: (status) => set({ isAuthenticated: status }),

  setAccessToken: (token) => {
    set({
      accessToken: token,
      isAuthenticated: !!token // 如果有token就设置为已认证
    });
    if (token) {
      localStorage.setItem('access_token', token);
    } else {
      localStorage.removeItem('access_token');
    }
  },

  setCurrentUser: (user) => {
    set({
      user,
      currentUser: user, // 保持兼容性
      isAdmin: user ? user.is_admin : false,
    });
  },

  login: async (credentials) => {
    try {
      const response = await apiClient.post<AuthResponse>('/auth/login', credentials);
      const { access_token, user } = response.data;

      // 更新状态
      set({
        isAuthenticated: true,
        accessToken: access_token,
        user,
        currentUser: user,
        isAdmin: user.is_admin,
      });

      // 保存token到localStorage
      localStorage.setItem('access_token', access_token);

      const { showAlert } = useAlertStore.getState();
      showAlert('登录成功！', 'success');
    } catch (error) {
      console.error('登录失败:', error);
      const { showAlert } = useAlertStore.getState();
      showAlert('登录失败，请检查邮箱和密码', 'error');
      throw error;
    }
  },

  register: async (userData) => {
    try {
      const response = await apiClient.post('/auth/register', userData);

      const { showAlert } = useAlertStore.getState();
      showAlert('注册成功！请登录', 'success');
    } catch (error) {
      console.error('注册失败:', error);
      const { showAlert } = useAlertStore.getState();

      // 根据错误类型显示不同的消息
      if (error instanceof Error) {
        if (error.message.includes('email')) {
          showAlert('该邮箱已被注册', 'error');
        } else if (error.message.includes('invitation')) {
          showAlert('邀请码无效或已被使用', 'error');
        } else if (error.message.includes('username')) {
          showAlert('用户名已被占用', 'error');
        } else {
          showAlert('注册失败，请稍后重试', 'error');
        }
      } else {
        showAlert('注册失败，请稍后重试', 'error');
      }
      throw error;
    }
  },

  logout: () => {
    localStorage.removeItem('access_token');
    set({
      isAuthenticated: false,
      accessToken: null,
      user: null,
      currentUser: null,
      isAdmin: false,
    });

    const { showAlert } = useAlertStore.getState();
    showAlert('已退出登录', 'info');
  },

  fetchCurrentUser: async () => {
    try {
      const response = await apiClient.get<User>('/users/me');
      if (response.data) {
        set({
          user: response.data,
          currentUser: response.data,
          isAdmin: response.data.is_admin,
          isAuthenticated: true,
        });
        return response.data;
      }
      return null;
    } catch (error) {
      console.error('获取用户信息失败:', error);
      localStorage.removeItem('access_token');
      set({
        user: null,
        currentUser: null,
        isAuthenticated: false,
        accessToken: null,
        isAdmin: false,
      });
      return null;
    }
  },
}));
