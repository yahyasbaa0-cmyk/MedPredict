import { create } from 'zustand';

let idCounter = 0;

const useToastStore = create((set) => ({
  toasts: [],
  addToast: (title, message, type = 'info', duration = 4000) => {
    const id = ++idCounter;
    set((state) => ({
      toasts: [...state.toasts, { id, title, message, type }],
    }));
    
    if (duration > 0) {
      setTimeout(() => {
        set((state) => ({
          toasts: state.toasts.filter((t) => t.id !== id),
        }));
      }, duration);
    }
  },
  removeToast: (id) => {
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id),
    }));
  },
}));

export default useToastStore;
