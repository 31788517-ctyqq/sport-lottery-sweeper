/**
 * Vue 3 Composable for Authentication Logic
 * Manages user login, logout, token storage, and authentication state.
 */

import { ref, computed, readonly } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus'; // Or element-ui
import { authAPI } from '@/api/modules/auth'; // Adjust path based on your structure

// State
const user = ref(null);
const token = ref(localStorage.getItem('access_token') || null);
const loading = ref(false);

// Computed
const isAuthenticated = computed(() => !!token.value && !!user.value);

// Actions
const login = async (credentials) => {
  try {
    loading.value = true;
    const response = await authAPI.login(credentials);
    const { access_token, user: userData } = response.data; // Assuming API returns token and user data together or separately

    // Store token and user data
    token.value = access_token;
    user.value = userData;
    localStorage.setItem('access_token', access_token);
    if (userData) {
      localStorage.setItem('user_info', JSON.stringify(userData));
    }

    ElMessage.success('登录成功');
    return response;
  } catch (error) {
    console.error('Login failed:', error);
    // Error handling is done in the API interceptor
    throw error;
  } finally {
    loading.value = false;
  }
};

const logout = async () => {
  try {
    // Optionally call backend logout endpoint
    // await authAPI.logout();
    // Clear local storage and state
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
    token.value = null;
    user.value = null;
    ElMessage.success('已登出');
  } catch (error) {
    console.error('Logout failed:', error);
    // Handle potential logout failure if needed
    // For now, clear local state anyway
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
    token.value = null;
    user.value = null;
    ElMessage.warning('登出，本地数据已清理');
  }
};

const fetchCurrentUser = async () => {
  if (!token.value) {
    console.warn('No token available to fetch user info.');
    return;
  }
  try {
    loading.value = true;
    const response = await authAPI.getCurrentUser();
    user.value = response.data;
    localStorage.setItem('user_info', JSON.stringify(response.data)); // Update local storage
  } catch (error) {
    console.error('Failed to fetch user info:', error);
    // If fetching fails, it might indicate an invalid token
    // Consider auto-logout here if desired
    // await logout();
  } finally {
    loading.value = false;
  }
};

// Initialize user info if token exists
if (token.value) {
  const storedUserInfo = localStorage.getItem('user_info');
  if (storedUserInfo) {
    try {
      user.value = JSON.parse(storedUserInfo);
    } catch (e) {
      console.error('Failed to parse stored user info:', e);
      localStorage.removeItem('user_info'); // Clean up corrupted data
    }
  } else {
    // Fallback: fetch user info from API if not stored locally
    fetchCurrentUser();
  }
}

export function useAuth() {
  return {
    user: readonly(user),
    token: readonly(token),
    loading: readonly(loading),
    isAuthenticated,
    login,
    logout,
    fetchCurrentUser,
  };
}