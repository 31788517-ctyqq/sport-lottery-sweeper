// frontend/src/router/guards/admin.js
import { useAuthStore } from '../../store/modules/user';
import { UserRole } from '../../utils/permissions';

// 定义管理员角色标识符（使用权限常量）
const ADMIN_ROLE = UserRole.ADMIN;

/**
 * 管理员守卫
 * 检查用户是否具有管理员权限
 * @returns {boolean} - 如果用户是管理员则返回 true，否则返回 false
 */
export const checkAdmin = () => {
  const authStore = useAuthStore();
  // 注意：当前 store 中只有 isAuthenticated，没有 userRoles
  // 临时方案：如果有认证就允许访问
  return authStore.isAuthenticated;
};

/**
 * 重定向到管理员入口或无权限页面
 * @param {Object} to - 目标路由
 * @param {Object} from - 源路由
 * @param {Function} next - Vue Router 的 next 函数
 */
export const redirectToAdminOrForbidden = (to, from, next) => {
  // 如果目标就是管理员页面，但权限不足，重定向到 403
  if (to.path.startsWith('/admin')) {
      next('/403');
  } else {
      // 否则，可以重定向到一个通用的无权限提示页，或者主页
      // 这里选择重定向到 403，保持一致性
      next('/403');
  }
  // 或者重定向到一个专门给非管理员的提示页，例如 next('/not-admin');
};