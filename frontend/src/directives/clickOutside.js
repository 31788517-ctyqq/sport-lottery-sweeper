/**
 * 点击外部指令
 * 当点击指令绑定元素的外部时触发回调
 * 常用于下拉菜单、模态框等组件的关闭
 */

/**
 * 点击外部指令
 * @param {HTMLElement} el - 指令绑定的元素
 * @param {Object} binding - 指令绑定对象
 * @param {Function} binding.value - 点击外部时执行的回调函数
 * @param {Object} binding.arg - 指令参数，可配置
 * @param {Array} binding.arg.exclude - 排除的元素选择器数组
 * @param {boolean} binding.arg.include - 是否包含指令元素自身
 * @param {boolean} binding.arg.immediate - 是否立即执行
 */
const clickOutside = {
  mounted(el, binding) {
    const {
      exclude = [],
      includeSelf = false,
      immediate = false,
      disabled = false
    } = binding.arg || {};
    
    // 如果指令被禁用，则直接返回
    if (disabled) return;
    
    // 存储排除的元素
    const excludedElements = [];
    
    // 收集所有排除的元素
    exclude.forEach(selector => {
      const elements = document.querySelectorAll(selector);
      elements.forEach(element => excludedElements.push(element));
    });
    
    // 如果包含自身，则将指令绑定元素也添加到排除列表中
    if (includeSelf) {
      excludedElements.push(el);
    }
    
    // 点击事件处理函数
    const handleClickOutside = (event) => {
      const clickedElement = event.target;
      
      // 检查点击的元素是否是指令绑定的元素或其子元素
      const isInside = el.contains(clickedElement);
      
      // 检查点击的元素是否在排除列表中
      const isExcluded = excludedElements.some(excludedElement => 
        excludedElement && excludedElement.contains(clickedElement)
      );
      
      // 如果点击发生在外部且不在排除列表中，则执行回调
      if (!isInside && !isExcluded) {
        binding.value(event);
      }
    };
    
    // 将处理函数存储在元素上，以便在卸载时移除
    el._clickOutsideHandler = handleClickOutside;
    
    // 添加事件监听器
    // 使用捕获阶段以确保在其他点击处理程序之前执行
    document.addEventListener('click', handleClickOutside, true);
    
    // 如果设置了立即执行，则立即检查并可能执行回调
    if (immediate) {
      // 使用setTimeout确保在DOM更新后执行
      setTimeout(() => {
        const rect = el.getBoundingClientRect();
        const isVisible = rect.width > 0 && rect.height > 0;
        
        if (isVisible) {
          // 模拟点击外部事件
          handleClickOutside({ target: null });
        }
      }, 0);
    }
  },
  
  updated(el, binding) {
    // 如果指令值发生变化，更新处理函数
    if (binding.value !== binding.oldValue) {
      // 先移除旧的监听器
      if (el._clickOutsideHandler) {
        document.removeEventListener('click', el._clickOutsideHandler, true);
      }
      
      // 重新安装指令
      const { disabled } = binding.arg || {};
      
      if (!disabled) {
        clickOutside.mounted(el, binding);
      }
    }
  },
  
  beforeUnmount(el) {
    // 清理事件监听器
    if (el._clickOutsideHandler) {
      document.removeEventListener('click', el._clickOutsideHandler, true);
      delete el._clickOutsideHandler;
    }
  }
};

/**
 * 安装指令到Vue应用
 * @param {Object} app - Vue应用实例
 */
export const installClickOutside = (app) => {
  app.directive('click-outside', clickOutside);
};

/**
 * 单独导出指令对象，以便在组合式API中使用
 */
export const vClickOutside = clickOutside;

export default clickOutside;