/**
 * 工具提示指令
 * 为元素添加悬停提示功能
 * 支持多种位置、样式和触发方式
 */

/**
 * 工具提示配置
 */
const defaultConfig = {
  position: 'top',      // top | bottom | left | right
  content: '',          // 提示内容
  delay: 100,           // 显示延迟（毫秒）
  duration: 3000,       // 自动隐藏时间（0表示不自动隐藏）
  showArrow: true,      // 是否显示箭头
  maxWidth: '200px',    // 最大宽度
  theme: 'light',       // light | dark
  trigger: 'hover',     // hover | click | focus | manual
  offset: 10,           // 偏移量
  disabled: false,      // 是否禁用
  html: false,          // 是否允许HTML内容
  zIndex: 9999,         // z-index值
  animation: 'fade',    // fade | slide | none
  customClass: '',      // 自定义CSS类名
  container: 'body',    // 容器选择器
  appendToBody: true    // 是否添加到body
};

/**
 * 工具提示指令
 */
const tooltip = {
  mounted(el, binding) {
    const config = {
      ...defaultConfig,
      ...(binding.arg || {}),
      content: binding.value || ''
    };
    
    // 如果禁用或没有内容，则不创建工具提示
    if (config.disabled || !config.content) {
      return;
    }
    
    // 创建工具提示元素
    const tooltipEl = document.createElement('div');
    tooltipEl.className = `vue-tooltip ${config.customClass}`;
    tooltipEl.setAttribute('role', 'tooltip');
    tooltipEl.style.cssText = `
      position: absolute;
      visibility: hidden;
      opacity: 0;
      max-width: ${config.maxWidth};
      z-index: ${config.zIndex};
      pointer-events: none;
      transition: opacity 0.2s ease;
    `;
    
    // 添加主题类
    tooltipEl.classList.add(`tooltip-${config.theme}`);
    
    // 添加动画类
    if (config.animation !== 'none') {
      tooltipEl.classList.add(`tooltip-${config.animation}`);
    }
    
    // 设置内容
    if (config.html) {
      tooltipEl.innerHTML = config.content;
    } else {
      tooltipEl.textContent = config.content;
    }
    
    // 添加箭头
    if (config.showArrow) {
      const arrowEl = document.createElement('div');
      arrowEl.className = 'tooltip-arrow';
      arrowEl.style.cssText = `
        position: absolute;
        width: 0;
        height: 0;
        border-style: solid;
      `;
      tooltipEl.appendChild(arrowEl);
    }
    
    // 添加到DOM
    let container = config.appendToBody ? document.body : el;
    if (typeof config.container === 'string') {
      const containerEl = document.querySelector(config.container);
      if (containerEl) {
        container = containerEl;
      }
    }
    container.appendChild(tooltipEl);
    
    // 存储引用和配置
    el._tooltip = {
      element: tooltipEl,
      config,
      timer: null,
      isVisible: false
    };
    
    // 绑定事件
    bindEvents(el);
  },
  
  updated(el, binding) {
    const tooltipData = el._tooltip;
    
    if (!tooltipData) {
      return;
    }
    
    const newConfig = {
      ...defaultConfig,
      ...(binding.arg || {}),
      content: binding.value || ''
    };
    
    // 检查配置是否变化
    const configChanged = JSON.stringify(tooltipData.config) !== JSON.stringify(newConfig);
    
    if (configChanged) {
      // 先隐藏工具提示
      hideTooltip(el);
      
      // 更新配置
      tooltipData.config = newConfig;
      
      // 更新内容
      if (newConfig.html) {
        tooltipData.element.innerHTML = newConfig.content;
      } else {
        tooltipData.element.textContent = newConfig.content;
      }
      
      // 更新样式
      tooltipData.element.style.maxWidth = newConfig.maxWidth;
      tooltipData.element.style.zIndex = newConfig.zIndex;
      
      // 更新类名
      tooltipData.element.className = `vue-tooltip ${newConfig.customClass}`;
      tooltipData.element.classList.add(`tooltip-${newConfig.theme}`);
      
      if (newConfig.animation !== 'none') {
        tooltipData.element.classList.add(`tooltip-${newConfig.animation}`);
      }
    }
  },
  
  beforeUnmount(el) {
    const tooltipData = el._tooltip;
    
    if (tooltipData) {
      // 清理定时器
      if (tooltipData.timer) {
        clearTimeout(tooltipData.timer);
      }
      
      // 移除事件监听
      unbindEvents(el);
      
      // 从DOM中移除工具提示
      if (tooltipData.element && tooltipData.element.parentNode) {
        tooltipData.element.parentNode.removeChild(tooltipData.element);
      }
      
      // 清理引用
      delete el._tooltip;
    }
  }
};

/**
 * 绑定事件
 */
function bindEvents(el) {
  const tooltipData = el._tooltip;
  const { trigger } = tooltipData.config;
  
  switch (trigger) {
    case 'hover':
      el.addEventListener('mouseenter', showTooltip);
      el.addEventListener('mouseleave', hideTooltip);
      break;
      
    case 'click':
      el.addEventListener('click', toggleTooltip);
      document.addEventListener('click', handleDocumentClick);
      break;
      
    case 'focus':
      el.addEventListener('focus', showTooltip);
      el.addEventListener('blur', hideTooltip);
      break;
      
    case 'manual':
      // 手动控制，不绑定事件
      break;
  }
  
  // 为工具提示元素添加鼠标事件，防止鼠标移入时隐藏
  if (trigger === 'hover') {
    tooltipData.element.addEventListener('mouseenter', () => {
      if (tooltipData.timer) {
        clearTimeout(tooltipData.timer);
      }
    });
    
    tooltipData.element.addEventListener('mouseleave', () => {
      hideTooltip({ target: el });
    });
  }
}

/**
 * 解绑事件
 */
function unbindEvents(el) {
  const tooltipData = el._tooltip;
  
  el.removeEventListener('mouseenter', showTooltip);
  el.removeEventListener('mouseleave', hideTooltip);
  el.removeEventListener('click', toggleTooltip);
  el.removeEventListener('focus', showTooltip);
  el.removeEventListener('blur', hideTooltip);
  document.removeEventListener('click', handleDocumentClick);
  
  if (tooltipData && tooltipData.element) {
    tooltipData.element.removeEventListener('mouseenter', () => {});
    tooltipData.element.removeEventListener('mouseleave', () => {});
  }
}

/**
 * 显示工具提示
 */
function showTooltip(event) {
  const el = event.currentTarget || event.target;
  const tooltipData = el._tooltip;
  
  if (!tooltipData || tooltipData.isVisible) {
    return;
  }
  
  // 清理之前的定时器
  if (tooltipData.timer) {
    clearTimeout(tooltipData.timer);
  }
  
  // 设置显示定时器
  tooltipData.timer = setTimeout(() => {
    positionTooltip(el);
    tooltipData.element.style.visibility = 'visible';
    tooltipData.element.style.opacity = '1';
    tooltipData.isVisible = true;
    
    // 自动隐藏
    const { duration } = tooltipData.config;
    if (duration > 0) {
      tooltipData.timer = setTimeout(() => {
        hideTooltip({ target: el });
      }, duration);
    }
  }, tooltipData.config.delay);
}

/**
 * 隐藏工具提示
 */
function hideTooltip(event) {
  const el = event.currentTarget || event.target;
  const tooltipData = el._tooltip;
  
  if (!tooltipData || !tooltipData.isVisible) {
    return;
  }
  
  // 清理定时器
  if (tooltipData.timer) {
    clearTimeout(tooltipData.timer);
  }
  
  // 隐藏工具提示
  tooltipData.element.style.opacity = '0';
  
  // 延迟移除可见性
  tooltipData.timer = setTimeout(() => {
    tooltipData.element.style.visibility = 'hidden';
    tooltipData.isVisible = false;
  }, 200);
}

/**
 * 切换工具提示显示/隐藏
 */
function toggleTooltip(event) {
  const el = event.currentTarget || event.target;
  const tooltipData = el._tooltip;
  
  if (!tooltipData) {
    return;
  }
  
  if (tooltipData.isVisible) {
    hideTooltip(event);
  } else {
    showTooltip(event);
  }
  
  event.stopPropagation();
}

/**
 * 处理文档点击事件（用于关闭点击触发的工具提示）
 */
function handleDocumentClick(event) {
  const tooltips = document.querySelectorAll('.vue-tooltip');
  
  tooltips.forEach(tooltipEl => {
    const triggerEl = tooltipEl._triggerEl;
    if (triggerEl && !triggerEl.contains(event.target) && !tooltipEl.contains(event.target)) {
      hideTooltip({ target: triggerEl });
    }
  });
}

/**
 * 定位工具提示
 */
function positionTooltip(el) {
  const tooltipData = el._tooltip;
  const { element: tooltipEl, config } = tooltipData;
  
  // 存储触发元素引用
  tooltipEl._triggerEl = el;
  
  // 获取元素位置
  const rect = el.getBoundingClientRect();
  const tooltipRect = tooltipEl.getBoundingClientRect();
  
  // 计算位置
  let top, left;
  const offset = config.offset;
  
  switch (config.position) {
    case 'top':
      top = rect.top - tooltipRect.height - offset;
      left = rect.left + (rect.width - tooltipRect.width) / 2;
      break;
      
    case 'bottom':
      top = rect.bottom + offset;
      left = rect.left + (rect.width - tooltipRect.width) / 2;
      break;
      
    case 'left':
      top = rect.top + (rect.height - tooltipRect.height) / 2;
      left = rect.left - tooltipRect.width - offset;
      break;
      
    case 'right':
      top = rect.top + (rect.height - tooltipRect.height) / 2;
      left = rect.right + offset;
      break;
  }
  
  // 调整位置，确保在视口内
  const viewportWidth = window.innerWidth;
  const viewportHeight = window.innerHeight;
  
  // 水平调整
  if (left < 0) left = 10;
  if (left + tooltipRect.width > viewportWidth) {
    left = viewportWidth - tooltipRect.width - 10;
  }
  
  // 垂直调整
  if (top < 0) {
    // 如果顶部位置不够，尝试显示在底部
    if (config.position === 'top') {
      top = rect.bottom + offset;
    } else {
      top = 10;
    }
  }
  if (top + tooltipRect.height > viewportHeight) {
    // 如果底部位置不够，尝试显示在顶部
    if (config.position === 'bottom') {
      top = rect.top - tooltipRect.height - offset;
    } else {
      top = viewportHeight - tooltipRect.height - 10;
    }
  }
  
  // 设置位置
  tooltipEl.style.top = `${top + window.scrollY}px`;
  tooltipEl.style.left = `${left + window.scrollX}px`;
  
  // 定位箭头
  const arrowEl = tooltipEl.querySelector('.tooltip-arrow');
  if (arrowEl) {
    const arrowSize = 6;
    
    switch (config.position) {
      case 'top':
        arrowEl.style.bottom = `-${arrowSize}px`;
        arrowEl.style.left = '50%';
        arrowEl.style.marginLeft = `-${arrowSize}px`;
        arrowEl.style.borderWidth = `${arrowSize}px ${arrowSize}px 0`;
        arrowEl.style.borderTopColor = 'inherit';
        break;
        
      case 'bottom':
        arrowEl.style.top = `-${arrowSize}px`;
        arrowEl.style.left = '50%';
        arrowEl.style.marginLeft = `-${arrowSize}px`;
        arrowEl.style.borderWidth = `0 ${arrowSize}px ${arrowSize}px`;
        arrowEl.style.borderBottomColor = 'inherit';
        break;
        
      case 'left':
        arrowEl.style.right = `-${arrowSize}px`;
        arrowEl.style.top = '50%';
        arrowEl.style.marginTop = `-${arrowSize}px`;
        arrowEl.style.borderWidth = `${arrowSize}px 0 ${arrowSize}px ${arrowSize}px`;
        arrowEl.style.borderLeftColor = 'inherit';
        break;
        
      case 'right':
        arrowEl.style.left = `-${arrowSize}px`;
        arrowEl.style.top = '50%';
        arrowEl.style.marginTop = `-${arrowSize}px`;
        arrowEl.style.borderWidth = `${arrowSize}px ${arrowSize}px ${arrowSize}px 0`;
        arrowEl.style.borderRightColor = 'inherit';
        break;
    }
  }
}

/**
 * 手动控制工具提示的API
 */
export const tooltipAPI = {
  /**
   * 显示工具提示
   * @param {HTMLElement} el - 指令绑定的元素
   */
  show(el) {
    if (el._tooltip) {
      showTooltip({ target: el });
    }
  },
  
  /**
   * 隐藏工具提示
   * @param {HTMLElement} el - 指令绑定的元素
   */
  hide(el) {
    if (el._tooltip) {
      hideTooltip({ target: el });
    }
  },
  
  /**
   * 更新工具提示内容
   * @param {HTMLElement} el - 指令绑定的元素
   * @param {string} content - 新的提示内容
   */
  updateContent(el, content) {
    if (el._tooltip) {
      el._tooltip.config.content = content;
      
      if (el._tooltip.config.html) {
        el._tooltip.element.innerHTML = content;
      } else {
        el._tooltip.element.textContent = content;
      }
    }
  },
  
  /**
   * 切换工具提示显示状态
   * @param {HTMLElement} el - 指令绑定的元素
   */
  toggle(el) {
    if (el._tooltip) {
      if (el._tooltip.isVisible) {
        this.hide(el);
      } else {
        this.show(el);
      }
    }
  },
  
  /**
   * 销毁工具提示
   * @param {HTMLElement} el - 指令绑定的元素
   */
  destroy(el) {
    if (el._tooltip) {
      tooltip.beforeUnmount(el);
    }
  }
};

/**
 * 安装指令到Vue应用
 * @param {Object} app - Vue应用实例
 */
export const installTooltip = (app) => {
  app.directive('tooltip', tooltip);
  
  // 提供工具提示API
  app.provide('tooltip-api', tooltipAPI);
};

/**
 * 组合式API中使用工具提示的函数
 */
export const useTooltip = () => {
  return {
    tooltipAPI,
    createTooltip: (content, options = {}) => {
      const tooltipEl = document.createElement('div');
      tooltipEl.className = 'vue-tooltip';
      tooltipEl.textContent = content;
      tooltipEl.style.cssText = `
        position: fixed;
        z-index: 9999;
        background: #333;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-size: 14px;
        max-width: 200px;
      `;
      
      document.body.appendChild(tooltipEl);
      
      return {
        element: tooltipEl,
        show: (x, y) => {
          tooltipEl.style.left = `${x}px`;
          tooltipEl.style.top = `${y}px`;
          tooltipEl.style.display = 'block';
        },
        hide: () => {
          tooltipEl.style.display = 'none';
        },
        destroy: () => {
          if (tooltipEl.parentNode) {
            tooltipEl.parentNode.removeChild(tooltipEl);
          }
        }
      };
    }
  };
};

export default tooltip;