// frontend/src/router/guards/permission.js
import { useAuthStore } from '../../store/modules/user';

/**
 * 权限守卫
 * 检查用户是否有访问特定路由的权限
 * @param {Object} route - 目标路由对象
 * @returns {boolean} - 如果用户有权限则返回 true，否则返回 false
 */
export const checkPermission = (route) => {
  const authStore = useAuthStore();
  const userRoles = authStore.userRoles || []; // 注意：当前 store 中没有 userRoles，需要后续添加
  const requiredPermissions = route.meta?.permissions; // 从路由元信息中获取所需权限

  // 如果路由没有定义特定权限，则认为任何人都可以访问
  if (!requiredPermissions || requiredPermissions.length === 0) {
    return true;
  }

  // 检查用户的角色是否包含所需的权限
  // 这里的逻辑可以根据实际权限模型调整，比如基于角色 (RBAC) 或基于权限 (ABAC)
  // 示例：检查角色名称是否与权限要求匹配（简单模型）
  // 更复杂的模型可能需要映射角色到具体权限列表
  return requiredPermissions.some(permission => userRoles.includes(permission));

  // 示例：更精细的权限检查（假设 userPermissions 存储了具体的权限字符串）
  // const userPermissions = userStore.userPermissions || [];
  // return requiredPermissions.every(permission => userPermissions.includes(permission));
};

/**
 * 重定向到无权限页面
 * @param {Object} to - 目标路由
 * @param {Object} from - 源路由
 * @param {Function} next - Vue Router 的 next 函数
 */
export const redirectToForbidden = (to, from, next) => {
  next('/403'); // 重定向到 403 无权访问页面
};