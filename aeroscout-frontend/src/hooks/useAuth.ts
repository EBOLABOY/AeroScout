import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';

export const useAuth = (requiresAuth: boolean = true) => {
  const { isAuthenticated } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (requiresAuth && !isAuthenticated) {
      router.push('/auth/login');
    } else if (!requiresAuth && isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, requiresAuth, router]);

  return { isAuthenticated };
};