import { create } from 'zustand';

type AlertVariant = 'info' | 'success' | 'warning' | 'error';

interface AlertState {
  isOpen: boolean;
  message: string;
  variant: AlertVariant;
  title?: string;
  showAlert: (message: string, variant?: AlertVariant, title?: string) => void;
  hideAlert: () => void;
}

export const useAlertStore = create<AlertState>((set) => ({
  isOpen: false,
  message: '',
  variant: 'info',
  title: undefined,
  showAlert: (message, variant = 'error', title) => {
    set({ 
      isOpen: true, 
      message, 
      variant,
      title: title || (variant === 'error' ? '错误' : variant === 'success' ? '成功' : variant === 'warning' ? '警告' : '提示')
    });
  },
  hideAlert: () => set({ isOpen: false, message: '', title: undefined }),
}));

// Custom hook for easier usage
export const useAlert = () => {
  const { showAlert, hideAlert } = useAlertStore();
  return { showAlert, hideAlert };
};