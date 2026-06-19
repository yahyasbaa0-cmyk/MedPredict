import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from '../services/api';

const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      login: async (username, password) => {
        try {
          const response = await api.post('/auth/login/', { username, password });
          const token = response.data.access;
          
          // Decode simple payload from JWT
          const base64Url = token.split('.')[1];
          const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
          const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
              return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
          }).join(''));
          const payload = JSON.parse(jsonPayload);

          localStorage.setItem('medpredict_token', token);
          
          set({
            user: {
              role: payload.role,
              email: payload.email,
              first_name: payload.first_name,
              last_name: payload.last_name,
              id: payload.user_id
            },
            token,
            isAuthenticated: true,
          });
          return true;
        } catch (error) {
          console.error("Login failed", error);
          return false;
        }
      },
      logout: () => {
        localStorage.removeItem('medpredict_token');
        set({ user: null, token: null, isAuthenticated: false });
      },
    }),
    {
      name: 'medpredict-auth-storage',
    }
  )
);

export default useAuthStore;
