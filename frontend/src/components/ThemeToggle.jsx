import { useThemeStore } from '../store/useThemeStore';
import { Moon, Sun } from 'lucide-react';

export default function ThemeToggle() {
  const { theme, toggleTheme } = useThemeStore();

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-lg transition-all duration-300 hover:scale-110"
      style={{
        background: theme === 'light' 
          ? 'rgba(0, 0, 0, 0.05)' 
          : 'rgba(255, 255, 255, 0.1)',
        border: `1px solid ${theme === 'light' 
          ? 'rgba(0, 0, 0, 0.1)' 
          : 'rgba(255, 255, 255, 0.2)'}`,
        color: 'var(--text-main)',
        cursor: 'pointer',
      }}
      title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
      aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
    >
      {theme === 'light' ? (
        <Moon size={18} strokeWidth={2.5} />
      ) : (
        <Sun size={18} strokeWidth={2.5} />
      )}
    </button>
  );
}
