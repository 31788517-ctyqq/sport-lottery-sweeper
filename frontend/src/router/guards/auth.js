// frontend/src/router/guards/auth.js
import { useAuthStore } from '../../store/modules/user';

// 临时模拟模式 - 开发环境下跳过认证检查
const isDevelopment = import.meta.env.MODE === 'development';

/**
 * 认证守卫
 * 检查用户是否已登录
 * @returns {Promise<boolean>} - 如果用户已认证则返回 true，否则返回 false
 */
export const checkAuth = async () => {
  // 开发环境临时跳过认证检查
  if (isDevelopment) {
    console.log('🔧 开发模式：跳过认证检查');
    return true;
  }
  
  const authStore = useAuthStore();

  // 如果 store 中已经有用户信息，认为是已登录
  if (authStore.userInfo) {
    return true;
  }

  // 如果 store 中没有用户信息，尝试从持久化存储（如 localStorage）恢复或刷新 token
  const token = localStorage.getItem('auth_token');
  if (!token) {
    return false; // 没有 token，明确未登录
  }

  // 如果有 token，尝试刷新用户信息或验证 token 有效性
  // 这通常是一个 API 调用，例如 refreshUserSession()
  try {
    await userStore.refreshUserSession(); // 假设 store 中有这个方法
    // 如果刷新成功，用户信息会被更新到 store 中
    return true;
  } catch (error) {
    console.error("Token verification failed:", error);
    // Token 无效或过期，清除本地存储并更新 store
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_info'); // 假设有单独存用户信息
    userStore.logout(); // 假设 store 中有 logout 方法来清空状态
    return false;
  }
};

/**
 * 重定向到登录页
 * @param {Object} to - 目标路由
 * @param {Object} from - 源路由
 * @param {Function} next - Vue Router 的 next 函数
 */
export const redirectToLogin = (to, from, next) => {
  next({
    path: '/login',
    query: { redirect: to.fullPath }, // 将当前路由作为查询参数传递，以便登录后跳转回来
  });
};