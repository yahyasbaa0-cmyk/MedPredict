import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useThemeStore = create(
  persist(
    (set) => ({
      theme: 'light',

      setTheme: (theme) => {
        localStorage.setItem('medpredict-theme', theme);
        document.documentElement.setAttribute('data-theme', theme);
        set({ theme });
      },

      toggleTheme: () => {
        set((state) => {
          const newTheme = state.theme === 'light' ? 'dark' : 'light';
          localStorage.setItem('medpredict-theme', newTheme);
          document.documentElement.setAttribute('data-theme', newTheme);
          return { theme: newTheme };
        });
      },

      initTheme: () => {
        const savedTheme = localStorage.getItem('medpredict-theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        set({ theme: savedTheme });
      },
    }),
    {
      name: 'medpredict-theme-storage',
      getStorage: () => localStorage,
    }
  )
);
