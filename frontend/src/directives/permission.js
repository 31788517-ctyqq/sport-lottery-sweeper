/**
 * 权限指令
 * 基于RBAC权限模型，控制元素的显示/隐藏
 * 与utils/permissions.js配合使用
 */

import { 
  hasPermission, 
  hasAnyPermission, 
  hasAllPermissions, 
  hasRole 
} from '../utils/permissions.js';

/**
 * 权限指令
 * @param {HTMLElement} el - 指令绑定的元素
 * @param {Object} binding - 指令绑定对象
 * @param {string|Array} binding.value - 需要的权限或角色
 * @param {Object} binding.arg - 指令参数
 * @param {boolean} binding.arg.any - 是否只需要任一权限
 * @param {boolean} binding.arg.all - 是否需要所有权限
 * @param {boolean} binding.arg.role - 是否是角色检查
 * @param {string} binding.arg.mode - 处理模式（show/hide/disable）
 */
const permission = {
  mounted(el, binding, vnode) {
    updatePermission(el, binding, vnode);
  },
  
  updated(el, binding, vnode) {
    updatePermission(el, binding, vnode);
  }
};

/**
 * 更新权限状态
 */
function updatePermission(el, binding, vnode) {
  const { 
    mode = 'show', 
    any = false, 
    all = false, 
    role = false 
  } = binding.arg || {};
  
  // 获取当前用户信息
  const user = getUserFromContext(vnode);
  
  if (!user) {
    handleNoUser(el, mode);
    return;
  }
  
  // 检查权限
  const hasAccess = checkAccess(user, binding.value, { any, all, role });
  
  // 根据模式处理元素
  handleElement(el, hasAccess, mode, binding);
}

/**
 * 从上下文获取用户信息
 */
function getUserFromContext(vnode) {
  // 尝试从多种来源获取用户信息
  
  // 1. 从全局状态管理（如Pinia）
  if (window.__VUE_APP_STORE__) {
    const store = window.__VUE_APP_STORE__;
    if (store.user && store.user.currentUser) {
      return store.user.currentUser;
    }
  }
  
  // 2. 从Vue实例的属性
  const instance = vnode.componentInstance || vnode.context;
  if (instance && instance.$store) {
    return instance.$store.state.user?.currentUser;
  }
  
  // 3. 从provide/inject
  if (instance && instance.provides && instance.provides.user) {
    return instance.provides.user;
  }
  
  // 4. 从localStorage（最后的手段）
  try {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      return JSON.parse(userStr);
    }
  } catch (error) {
    console.warn('Failed to get user from localStorage:', error);
  }
  
  return null;
}

/**
 * 检查访问权限
 */
function checkAccess(user, required, options = {}) {
  const { any = false, all = false, role = false } = options;
  
  if (!required) {
    return true;
  }
  
  if (role) {
    // 角色检查
    return hasRole(user.roles || [], required);
  }
  
  if (any) {
    // 任一权限检查
    return hasAnyPermission(user.permissions || [], required);
  }
  
  if (all) {
    // 所有权限检查
    return hasAllPermissions(user.permissions || [], required);
  }
  
  // 单一权限检查
  return hasPermission(user.permissions || [], required);
}

/**
 * 处理无用户的情况
 */
function handleNoUser(el, mode) {
  switch (mode) {
    case 'show':
    case 'enable':
      hideOrDisable(el, mode);
      break;
    case 'hide':
    case 'disable':
      showOrEnable(el, mode);
      break;
  }
}

/**
 * 处理元素显示/隐藏/禁用
 */
function handleElement(el, hasAccess, mode, binding) {
  switch (mode) {
    case 'show':
      // 有权限显示，无权限隐藏
      if (hasAccess) {
        showElement(el);
      } else {
        hideElement(el);
      }
      break;
      
    case 'hide':
      // 有权限隐藏，无权限显示
      if (hasAccess) {
        hideElement(el);
      } else {
        showElement(el);
      }
      break;
      
    case 'disable':
      // 有权限启用，无权限禁用
      if (hasAccess) {
        enableElement(el);
      } else {
        disableElement(el, binding.value);
      }
      break;
      
    case 'enable':
      // 有权限禁用，无权限启用
      if (hasAccess) {
        disableElement(el, binding.value);
      } else {
        enableElement(el);
      }
      break;
      
    case 'remove':
      // 无权限时从DOM中移除
      if (!hasAccess && el.parentNode) {
        el.parentNode.removeChild(el);
      }
      break;
      
    default:
      console.warn(`Unknown permission mode: ${mode}`);
      break;
  }
}

/**
 * 显示元素
 */
function showElement(el) {
  // 恢复原始display值
  if (el._originalDisplay !== undefined) {
    el.style.display = el._originalDisplay;
  } else {
    el.style.display = '';
  }
  
  // 移除隐藏类
  el.classList.remove('permission-hidden');
}

/**
 * 隐藏元素
 */
function hideElement(el) {
  // 保存原始display值
  if (el._originalDisplay === undefined) {
    el._originalDisplay = window.getComputedStyle(el).display;
  }
  
  // 隐藏元素
  el.style.display = 'none';
  
  // 添加隐藏类（用于CSS选择器）
  el.classList.add('permission-hidden');
}

/**
 * 启用元素
 */
function enableElement(el) {
  el.disabled = false;
  el.style.opacity = '';
  el.style.pointerEvents = '';
  el.classList.remove('permission-disabled');
  
  // 恢复原始title
  if (el._originalTitle !== undefined) {
    el.title = el._originalTitle;
    delete el._originalTitle;
  }
}

/**
 * 禁用元素
 */
function disableElement(el, reason = '') {
  el.disabled = true;
  el.style.opacity = '0.5';
  el.style.pointerEvents = 'none';
  el.classList.add('permission-disabled');
  
  // 添加提示
  if (reason && !el._originalTitle) {
    el._originalTitle = el.title || '';
    el.title = `无权限: ${reason}`;
  }
}

/**
 * 权限指令的快捷方式
 */
export const vPermission = permission;

/**
 * 创建特定模式的权限指令
 */
export function createPermissionDirective(mode = 'show') {
  return {
    mounted(el, binding, vnode) {
      const newBinding = {
        ...binding,
        arg: { ...binding.arg, mode }
      };
      updatePermission(el, newBinding, vnode);
    },
    
    updated(el, binding, vnode) {
      const newBinding = {
        ...binding,
        arg: { ...binding.arg, mode }
      };
      updatePermission(el, newBinding, vnode);
    }
  };
}

/**
 * 权限检查函数（用于组合式API）
 */
export const usePermission = () => {
  const check = (required, options = {}) => {
    // 获取用户信息（这里需要根据实际项目调整）
    let user = null;
    
    try {
      // 尝试从localStorage获取
      const userStr = localStorage.getItem('user');
      if (userStr) {
        user = JSON.parse(userStr);
      }
    } catch (error) {
      console.warn('Failed to get user in usePermission:', error);
    }
    
    if (!user) return false;
    
    return checkAccess(user, required, options);
  };
  
  return {
    check,
    hasPermission: (permission) => check(permission),
    hasAnyPermission: (permissions) => check(permissions, { any: true }),
    hasAllPermissions: (permissions) => check(permissions, { all: true }),
    hasRole: (role) => check(role, { role: true })
  };
};

/**
 * 权限守卫（用于路由守卫）
 */
export const permissionGuard = {
  /**
   * 创建路由守卫
   * @param {Function} getUser - 获取用户信息的函数
   * @returns {Function} 路由守卫函数
   */
  createGuard(getUser) {
    return (to, from, next) => {
      const user = getUser();
      
      // 检查路由元信息中的权限要求
      if (to.meta && to.meta.permissions) {
        const { permissions, roles, any = false, all = false } = to.meta;
        
        if (!user) {
          // 无用户，重定向到登录页
          next({ name: 'login', query: { redirect: to.fullPath } });
          return;
        }
        
        let hasAccess = false;
        
        if (roles) {
          // 检查角色
          hasAccess = hasRole(user.roles || [], roles);
        } else if (permissions) {
          // 检查权限
          if (any) {
            hasAccess = hasAnyPermission(user.permissions || [], permissions);
          } else if (all) {
            hasAccess = hasAllPermissions(user.permissions || [], permissions);
          } else {
            hasAccess = hasPermission(user.permissions || [], permissions);
          }
        }
        
        if (!hasAccess) {
          // 无权限，重定向到无权限页面
          next({ name: 'forbidden' });
          return;
        }
      }
      
      next();
    };
  }
};

/**
 * 安装指令到Vue应用
 * @param {Object} app - Vue应用实例
 */
export const installPermission = (app) => {
  // 注册主指令
  app.directive('permission', permission);
  
  // 注册快捷指令
  app.directive('can', createPermissionDirective('show'));
  app.directive('cannot', createPermissionDirective('hide'));
  app.directive('can-disable', createPermissionDirective('disable'));
  app.directive('can-enable', createPermissionDirective('enable'));
  
  // 提供权限工具
  app.provide('permission', usePermission());
};

export default permission;