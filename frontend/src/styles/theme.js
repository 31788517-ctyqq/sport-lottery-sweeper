import { ref, computed, watchEffect } from 'vue'

// Theme configuration
const themes = {
  light: {
    name: '浅色主题',
    icon: 'Sunny',
    colors: {
      primary: '#409eff',
      secondary: '#67c23a',
      accent: '#e6a23c',
      danger: '#f56c6c',
      gradientStart: '#667eea',
      gradientEnd: '#764ba2',
      bgLight: '#f8fafc',
      border: '#e2e8f0',
      textPrimary: '#2d3748',
      textSecondary: '#718096'
    }
  },
  dark: {
    name: '深色主题',
    icon: 'Moon',
    colors: {
      primary: '#60a5fa',
      secondary: '#4ade80',
      accent: '#fbbf24',
      danger: '#f87171',
      gradientStart: '#4c1d95',
      gradientEnd: '#1e293b',
      bgLight: '#1a1a1a',
      border: '#374151',
      textPrimary: '#f9fafb',
      textSecondary: '#d1d5db'
    }
  },
  blue: {
    name: '蓝色主题',
    icon: 'Watermelon',
    colors: {
      primary: '#3b82f6',
      secondary: '#06b6d4',
      accent: '#f59e0b',
      danger: '#ef4444',
      gradientStart: '#1e3a8a',
      gradientEnd: '#3b82f6',
      bgLight: '#f0f9ff',
      border: '#bfdbfe',
      textPrimary: '#1e293b',
      textSecondary: '#64748b'
    }
  },
  green: {
    name: '绿色主题',
    icon: 'SuccessFilled',
    colors: {
      primary: '#10b981',
      secondary: '#059669',
      accent: '#f59e0b',
      danger: '#ef4444',
      gradientStart: '#064e3b',
      gradientEnd: '#10b981',
      bgLight: '#f0fdf4',
      border: '#bbf7d0',
      textPrimary: '#064e3b',
      textSecondary: '#6b7280'
    }
  },
  purple: {
    name: '紫色主题',
    icon: 'MagicStick',
    colors: {
      primary: '#8b5cf6',
      secondary: '#a855f7',
      accent: '#f59e0b',
      danger: '#ef4444',
      gradientStart: '#581c87',
      gradientEnd: '#8b5cf6',
      bgLight: '#faf5ff',
      border: '#ddd6fe',
      textPrimary: '#581c87',
      textSecondary: '#6b7280'
    }
  }
}

// Theme management composable
export function useTheme() {
  const currentTheme = ref('light')
  const isDark = computed(() => currentTheme.value === 'dark')

  // Load saved theme from localStorage
  const savedTheme = localStorage.getItem('theme') || 'light'
  currentTheme.value = savedTheme

  // Apply theme to document
  const applyTheme = (themeName) => {
    const theme = themes[themeName]
    if (!theme) return

    // Set data attribute for CSS variables
    document.documentElement.setAttribute('data-theme', themeName)
    
    // Update CSS custom properties
    const root = document.documentElement
    Object.entries(theme.colors).forEach(([key, value]) => {
      root.style.setProperty(`--sports-${key}`, value)
    })

    // Update Element Plus theme if needed
    if (themeName === 'dark') {
      document.documentElement.setAttribute('data-theme', 'dark')
    } else {
      document.documentElement.setAttribute('data-theme', 'light')
    }

    currentTheme.value = themeName
    localStorage.setItem('theme', themeName)
  }

  // Watch for theme changes
  watchEffect(() => {
    applyTheme(currentTheme.value)
  })

  // Toggle between light and dark
  const toggleDark = () => {
    const newTheme = isDark.value ? 'light' : 'dark'
    applyTheme(newTheme)
  }

  // Set specific theme
  const setTheme = (themeName) => {
    if (themes[themeName]) {
      applyTheme(themeName)
    }
  }

  // Get current theme info
  const getCurrentTheme = computed(() => {
    return themes[currentTheme.value]
  })

  // Get all available themes
  const getAvailableThemes = () => {
    return Object.entries(themes).map(([key, theme]) => ({
      key,
      ...theme
    }))
  }

  return {
    currentTheme,
    isDark,
    themes,
    getCurrentTheme,
    getAvailableThemes,
    toggleDark,
    setTheme,
    applyTheme
  }
}

// Theme-aware color utilities
export const themeColors = {
  // Get color with theme awareness
  getPrimary: (opacity = 1) => {
    const color = getComputedStyle(document.documentElement).getPropertyValue('--sports-primary').trim()
    return opacity < 1 ? `${color}${Math.round(opacity * 255).toString(16).padStart(2, '0')}` : color
  },

  getSecondary: (opacity = 1) => {
    const color = getComputedStyle(document.documentElement).getPropertyValue('--sports-secondary').trim()
    return opacity < 1 ? `${color}${Math.round(opacity * 255).toString(16).padStart(2, '0')}` : color
  },

  getAccent: (opacity = 1) => {
    const color = getComputedStyle(document.documentElement).getPropertyValue('--sports-accent').trim()
    return opacity < 1 ? `${color}${Math.round(opacity * 255).toString(16).padStart(2, '0')}` : color
  },

  getDanger: (opacity = 1) => {
    const color = getComputedStyle(document.documentElement).getPropertyValue('--sports-danger').trim()
    return opacity < 1 ? `${color}${Math.round(opacity * 255).toString(16).padStart(2, '0')}` : color
  },

  // Gradient backgrounds
  getGradient: (angle = '135deg') => {
    const start = getComputedStyle(document.documentElement).getPropertyValue('--sports-gradient-start').trim()
    const end = getComputedStyle(document.documentElement).getPropertyValue('--sports-gradient-end').trim()
    return `linear-gradient(${angle}, ${start} 0%, ${end} 100%)`
  },

  // Status colors based on theme
  getSuccessColor: () => getComputedStyle(document.documentElement).getPropertyValue('--el-color-success').trim(),
  getWarningColor: () => getComputedStyle(document.documentElement).getPropertyValue('--el-color-warning').trim(),
  getInfoColor: () => getComputedStyle(document.documentElement).getPropertyValue('--el-color-info').trim()
}

// Theme transition animations
export const themeTransition = {
  beforeEnter: (el) => {
    el.style.transition = 'none'
  },
  enter: (el, done) => {
    el.offsetHeight // trigger reflow
    el.style.transition = 'all 0.3s ease'
    done()
  },
  leave: (el, done) => {
    el.style.transition = 'all 0.3s ease'
    done()
  }
}

// Export theme names as constants
export const THEME_NAMES = {
  LIGHT: 'light',
  DARK: 'dark',
  BLUE: 'blue',
  GREEN: 'green',
  PURPLE: 'purple'
}

// Default export
export default {
  useTheme,
  themeColors,
  themeTransition,
  THEME_NAMES,
  themes
}