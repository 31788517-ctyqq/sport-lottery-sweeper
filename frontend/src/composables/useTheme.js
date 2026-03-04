/**
 * Composable for managing application theme (light/dark mode).
 * Persists the choice in localStorage and applies it to the document root.
 */

import { ref, watchEffect, readonly } from 'vue';
import { STORAGE_KEYS } from '@/constants/storage-keys';

const THEME_KEY = STORAGE_KEYS.THEME_PREFERENCE;

// Determine initial theme based on system preference or saved preference
const getInitialTheme = () => {
  const savedTheme = localStorage.getItem(THEME_KEY);
  if (savedTheme) {
    return savedTheme;
  }
  // Fallback to system preference
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};

const currentTheme = ref(getInitialTheme());

const applyTheme = (theme) => {
  if (theme === 'dark') {
    document.documentElement.classList.add('dark-theme');
    document.documentElement.classList.remove('light-theme');
  } else {
    document.documentElement.classList.add('light-theme');
    document.documentElement.classList.remove('dark-theme');
  }
};

// Apply theme when currentTheme changes
watchEffect(() => {
  applyTheme(currentTheme.value);
  localStorage.setItem(THEME_KEY, currentTheme.value);
});

const toggleTheme = () => {
  currentTheme.value = currentTheme.value === 'light' ? 'dark' : 'light';
};

const setTheme = (theme) => {
  if (['light', 'dark'].includes(theme)) {
    currentTheme.value = theme;
  }
};

export function useTheme() {
  return {
    currentTheme: readonly(currentTheme),
    toggleTheme,
    setTheme,
  };
}