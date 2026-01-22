/**
 * 防抖和节流工具函数
 * 用于性能优化，控制函数执行频率
 */

/**
 * 防抖函数
 * 在事件被触发n秒后再执行回调，如果在这n秒内又被触发，则重新计时
 * @param {Function} func - 要执行的函数
 * @param {number} wait - 等待时间（毫秒）
 * @param {boolean} immediate - 是否立即执行
 * @returns {Function} 防抖处理后的函数
 */
export function debounce(func, wait = 300, immediate = false) {
  let timeout = null;
  let result = null;
  
  const debounced = function(...args) {
    const context = this;
    
    // 清除之前的定时器
    if (timeout) {
      clearTimeout(timeout);
    }
    
    // 立即执行模式
    if (immediate) {
      const callNow = !timeout;
      timeout = setTimeout(() => {
        timeout = null;
      }, wait);
      
      if (callNow) {
        result = func.apply(context, args);
      }
    } else {
      // 延迟执行模式
      timeout = setTimeout(() => {
        func.apply(context, args);
      }, wait);
    }
    
    return result;
  };
  
  // 取消函数
  debounced.cancel = function() {
    if (timeout) {
      clearTimeout(timeout);
      timeout = null;
    }
  };
  
  // 立即执行函数
  debounced.flush = function(...args) {
    if (timeout) {
      clearTimeout(timeout);
      timeout = null;
      return func.apply(this, args);
    }
    return result;
  };
  
  return debounced;
}

/**
 * 节流函数
 * 在一定时间内只执行一次函数
 * @param {Function} func - 要执行的函数
 * @param {number} wait - 等待时间（毫秒）
 * @param {Object} options - 选项
 * @param {boolean} options.leading - 是否在开始处执行
 * @param {boolean} options.trailing - 是否在结束处执行
 * @returns {Function} 节流处理后的函数
 */
export function throttle(func, wait = 300, options = {}) {
  let timeout = null;
  let previous = 0;
  let result = null;
  
  const { leading = true, trailing = true } = options;
  
  const throttled = function(...args) {
    const context = this;
    const now = Date.now();
    
    // 如果是第一次调用且不需要开始执行
    if (!previous && !leading) {
      previous = now;
    }
    
    const remaining = wait - (now - previous);
    
    // 如果剩余时间小于等于0或大于等待时间（系统时间调整）
    if (remaining <= 0 || remaining > wait) {
      if (timeout) {
        clearTimeout(timeout);
        timeout = null;
      }
      
      previous = now;
      result = func.apply(context, args);
    } else if (!timeout && trailing) {
      // 设置延迟执行
      timeout = setTimeout(() => {
        previous = !leading ? 0 : Date.now();
        timeout = null;
        result = func.apply(context, args);
      }, remaining);
    }
    
    return result;
  };
  
  // 取消函数
  throttled.cancel = function() {
    if (timeout) {
      clearTimeout(timeout);
      previous = 0;
      timeout = null;
    }
  };
  
  // 立即执行函数
  throttled.flush = function(...args) {
    if (timeout) {
      clearTimeout(timeout);
      timeout = null;
      previous = Date.now();
      return func.apply(this, args);
    }
    return result;
  };
  
  return throttled;
}

/**
 * 防抖装饰器（用于类方法）
 * @param {number} wait - 等待时间
 * @param {boolean} immediate - 是否立即执行
 * @returns {Function} 装饰器函数
 */
export function debounceDecorator(wait = 300, immediate = false) {
  return function(target, key, descriptor) {
    const originalMethod = descriptor.value;
    const debouncedMethod = debounce(originalMethod, wait, immediate);
    
    descriptor.value = function(...args) {
      return debouncedMethod.apply(this, args);
    };
    
    return descriptor;
  };
}

/**
 * 节流装饰器（用于类方法）
 * @param {number} wait - 等待时间
 * @param {Object} options - 选项
 * @returns {Function} 装饰器函数
 */
export function throttleDecorator(wait = 300, options = {}) {
  return function(target, key, descriptor) {
    const originalMethod = descriptor.value;
    const throttledMethod = throttle(originalMethod, wait, options);
    
    descriptor.value = function(...args) {
      return throttledMethod.apply(this, args);
    };
    
    return descriptor;
  };
}

/**
 * 增强版防抖（支持最大等待时间）
 * @param {Function} func - 要执行的函数
 * @param {number} wait - 基础等待时间
 * @param {number} maxWait - 最大等待时间
 * @returns {Function} 防抖处理后的函数
 */
export function debounceMax(func, wait = 300, maxWait = 1000) {
  let timeout = null;
  let lastInvokeTime = 0;
  let result = null;
  
  const invokeFunc = function(context, args) {
    lastInvokeTime = Date.now();
    return func.apply(context, args);
  };
  
  const shouldInvoke = function(currentTime) {
    const timeSinceLastInvoke = currentTime - lastInvokeTime;
    return timeSinceLastInvoke >= maxWait;
  };
  
  const debounced = function(...args) {
    const context = this;
    const currentTime = Date.now();
    
    if (timeout) {
      clearTimeout(timeout);
    }
    
    if (shouldInvoke(currentTime)) {
      // 超过最大等待时间，立即执行
      timeout = null;
      lastInvokeTime = currentTime;
      result = invokeFunc(context, args);
    } else {
      // 设置定时器
      timeout = setTimeout(() => {
        timeout = null;
        lastInvokeTime = currentTime;
        result = invokeFunc(context, args);
      }, wait);
    }
    
    return result;
  };
  
  debounced.cancel = function() {
    if (timeout) {
      clearTimeout(timeout);
      timeout = null;
    }
  };
  
  return debounced;
}

/**
 * 空闲回调（使用requestIdleCallback）
 * @param {Function} func - 要执行的函数
 * @returns {Function} 空闲回调处理后的函数
 */
export function idleCallback(func) {
  let handle = null;
  
  const scheduled = function(...args) {
    const context = this;
    
    if (handle) {
      cancelIdleCallback(handle);
    }
    
    handle = requestIdleCallback(() => {
      func.apply(context, args);
    });
  };
  
  scheduled.cancel = function() {
    if (handle) {
      cancelIdleCallback(handle);
      handle = null;
    }
  };
  
  return scheduled;
}

/**
 * 批量处理函数（用于高频事件）
 * @param {Function} processor - 处理函数
 * @param {Function} batchFunc - 批量处理函数
 * @param {number} delay - 延迟时间
 * @returns {Function} 批量处理函数
 */
export function batchProcessor(processor, batchFunc, delay = 100) {
  let batch = [];
  let timeout = null;
  
  const processBatch = function() {
    if (batch.length > 0) {
      batchFunc(batch);
      batch = [];
    }
    timeout = null;
  };
  
  const addToBatch = function(...args) {
    const result = processor(...args);
    batch.push(result);
    
    if (!timeout) {
      timeout = setTimeout(processBatch, delay);
    }
  };
  
  addToBatch.flush = function() {
    if (timeout) {
      clearTimeout(timeout);
      processBatch();
    }
  };
  
  addToBatch.cancel = function() {
    if (timeout) {
      clearTimeout(timeout);
      timeout = null;
      batch = [];
    }
  };
  
  return addToBatch;
}

// 兼容性处理
if (typeof window !== 'undefined') {
  window.requestIdleCallback = window.requestIdleCallback || function(cb) {
    const start = Date.now();
    return setTimeout(() => {
      cb({
        didTimeout: false,
        timeRemaining: function() {
          return Math.max(0, 50 - (Date.now() - start));
        }
      });
    }, 1);
  };
  
  window.cancelIdleCallback = window.cancelIdleCallback || function(id) {
    clearTimeout(id);
  };
}

export default {
  debounce,
  throttle,
  debounceDecorator,
  throttleDecorator,
  debounceMax,
  idleCallback,
  batchProcessor
};