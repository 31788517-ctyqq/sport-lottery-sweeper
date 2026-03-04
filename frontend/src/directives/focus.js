/**
 * 自动聚焦指令
 * 自动将焦点设置到指令绑定的元素上
 * 支持延迟聚焦、条件聚焦等场景
 */

/**
 * 自动聚焦指令
 * @param {HTMLElement} el - 指令绑定的元素
 * @param {Object} binding - 指令绑定对象
 * @param {boolean|Object} binding.value - 控制是否聚焦
 * @param {Object} binding.arg - 指令参数
 * @param {number} binding.arg.delay - 延迟毫秒数
 * @param {boolean} binding.arg.select - 是否选中文本内容
 * @param {string} binding.arg.cursor - 光标位置（start/end）
 */
const focus = {
  mounted(el, binding) {
    const {
      delay = 0,
      select = false,
      cursor = 'start',
      condition = true
    } = binding.arg || {};
    
    const shouldFocus = binding.value !== false;
    
    // 如果条件不满足，则不进行聚焦
    if (!shouldFocus || !condition) return;
    
    const focusElement = () => {
      // 确保元素可见且可聚焦
      if (el.offsetParent === null) {
        console.warn('Focus directive: Element is not visible');
        return;
      }
      
      try {
        el.focus();
        
        // 如果需要选中文本
        if (select && el.select) {
          el.select();
        }
        
        // 设置光标位置
        if (cursor === 'end' && el.setSelectionRange) {
          const length = el.value ? el.value.length : 0;
          el.setSelectionRange(length, length);
        } else if (cursor === 'start' && el.setSelectionRange) {
          el.setSelectionRange(0, 0);
        }
      } catch (error) {
        console.warn('Focus directive failed:', error);
      }
    };
    
    // 延迟执行
    if (delay > 0) {
      setTimeout(focusElement, delay);
    } else {
      // 使用nextTick确保DOM已更新
      requestAnimationFrame(() => {
        requestAnimationFrame(focusElement);
      });
    }
    
    // 存储定时器ID，以便清理
    el._focusTimeout = delay > 0 ? setTimeout(focusElement, delay) : null;
  },
  
  updated(el, binding) {
    // 如果值从false变为true，则重新聚焦
    if (binding.value !== binding.oldValue && binding.value === true) {
      // 清理之前的定时器
      if (el._focusTimeout) {
        clearTimeout(el._focusTimeout);
        el._focusTimeout = null;
      }
      
      // 重新执行mounted逻辑
      focus.mounted(el, binding);
    }
  },
  
  beforeUnmount(el) {
    // 清理定时器
    if (el._focusTimeout) {
      clearTimeout(el._focusTimeout);
      el._focusTimeout = null;
    }
  }
};

/**
 * 聚焦管理器，用于处理多个元素的聚焦顺序
 */
export class FocusManager {
  constructor() {
    this.focusQueue = [];
    this.currentIndex = -1;
  }
  
  /**
   * 注册可聚焦元素
   * @param {HTMLElement} element - 要注册的元素
   * @param {Object} options - 选项
   * @returns {Function} 取消注册的函数
   */
  register(element, options = {}) {
    const { priority = 0, condition = () => true } = options;
    
    const item = {
      element,
      priority,
      condition,
      id: this.focusQueue.length
    };
    
    this.focusQueue.push(item);
    this.sortQueue();
    
    // 返回取消注册的函数
    return () => {
      const index = this.focusQueue.findIndex(item => item.element === element);
      if (index > -1) {
        this.focusQueue.splice(index, 1);
        this.sortQueue();
      }
    };
  }
  
  /**
   * 按优先级排序队列
   */
  sortQueue() {
    this.focusQueue.sort((a, b) => {
      if (a.priority !== b.priority) {
        return b.priority - a.priority; // 优先级高的在前
      }
      return a.id - b.id; // 保持插入顺序
    });
  }
  
  /**
   * 聚焦到下一个符合条件的元素
   * @returns {boolean} 是否成功聚焦
   */
  focusNext() {
    for (let i = 0; i < this.focusQueue.length; i++) {
      const item = this.focusQueue[i];
      
      // 检查条件
      if (item.condition()) {
        try {
          item.element.focus();
          this.currentIndex = i;
          return true;
        } catch (error) {
          console.warn('FocusManager: Failed to focus element', error);
        }
      }
    }
    
    return false;
  }
  
  /**
   * 聚焦到指定元素
   * @param {HTMLElement} element - 要聚焦的元素
   * @returns {boolean} 是否成功聚焦
   */
  focusTo(element) {
    const item = this.focusQueue.find(item => item.element === element);
    if (item && item.condition()) {
      try {
        element.focus();
        this.currentIndex = this.focusQueue.indexOf(item);
        return true;
      } catch (error) {
        console.warn('FocusManager: Failed to focus element', error);
      }
    }
    return false;
  }
  
  /**
   * 清除所有注册
   */
  clear() {
    this.focusQueue = [];
    this.currentIndex = -1;
  }
}

// 全局焦点管理器实例
export const focusManager = new FocusManager();

/**
 * 顺序聚焦指令
 * 用于处理表单等场景的Tab键顺序
 */
export const vFocusSequence = {
  mounted(el, binding) {
    const {
      priority = 0,
      condition = () => true,
      manager = focusManager
    } = binding.arg || {};
    
    // 注册到焦点管理器
    const unregister = manager.register(el, { priority, condition });
    
    // 存储取消注册函数
    el._focusUnregister = unregister;
    
    // 处理键盘事件
    const handleKeydown = (event) => {
      if (event.key === 'Tab' && !event.shiftKey) {
        // 阻止默认的Tab行为
        event.preventDefault();
        
        // 聚焦到下一个元素
        manager.focusNext();
      }
    };
    
    // 添加键盘事件监听
    el.addEventListener('keydown', handleKeydown);
    el._focusKeydownHandler = handleKeydown;
  },
  
  beforeUnmount(el) {
    // 取消注册
    if (el._focusUnregister) {
      el._focusUnregister();
      delete el._focusUnregister;
    }
    
    // 移除事件监听
    if (el._focusKeydownHandler) {
      el.removeEventListener('keydown', el._focusKeydownHandler);
      delete el._focusKeydownHandler;
    }
  }
};

/**
 * 安装指令到Vue应用
 * @param {Object} app - Vue应用实例
 */
export const installFocus = (app) => {
  app.directive('focus', focus);
  app.directive('focus-sequence', vFocusSequence);
  
  // 提供焦点管理器
  app.provide('focus-manager', focusManager);
};

/**
 * 组合式API中使用焦点指令的函数
 */
export const useFocus = () => {
  return {
    focusManager,
    focus: (element, options = {}) => {
      const { delay = 0, select = false } = options;
      
      if (!element) return;
      
      setTimeout(() => {
        try {
          element.focus();
          if (select && element.select) {
            element.select();
          }
        } catch (error) {
          console.warn('useFocus: Failed to focus element', error);
        }
      }, delay);
    }
  };
};

export default focus;