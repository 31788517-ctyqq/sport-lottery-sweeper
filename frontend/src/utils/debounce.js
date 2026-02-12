/**
 * 防抖工具函数
 * 用于优化高频触发的操作，如筛选、搜索等
 */

/**
 * 防抖函数
 * @param {Function} fn - 要防抖的函数
 * @param {number} delay - 延迟时间(ms)
 * @param {Object} options - 选项
 * @param {boolean} options.leading - 是否在延迟开始前调用
 * @param {boolean} options.trailing - 是否在延迟结束后调用
 * @returns {Function} 防抖后的函数
 */
export function useDebounceFn(fn, delay, options = {}) {
  const { leading = false, trailing = true } = options;
  let timeoutId = null;
  let lastArgs = null;
  let lastThis = null;

  const debounced = function(...args) {
    lastArgs = args;
    lastThis = this;

    const shouldCallNow = leading && !timeoutId;

    clearTimeout(timeoutId);

    timeoutId = setTimeout(() => {
      timeoutId = null;
      if (trailing && lastArgs) {
        fn.apply(lastThis, lastArgs);
      }
      lastArgs = null;
      lastThis = null;
    }, delay);

    if (shouldCallNow) {
      fn.apply(this, args);
    }
  };

  // 取消防抖
  debounced.cancel = () => {
    clearTimeout(timeoutId);
    timeoutId = null;
    lastArgs = null;
    lastThis = null;
  };

  // 立即执行
  debounced.flush = () => {
    if (timeoutId) {
      clearTimeout(timeoutId);
      timeoutId = null;
      if (trailing && lastArgs) {
        fn.apply(lastThis, lastArgs);
      }
      lastArgs = null;
      lastThis = null;
    }
  };

  return debounced;
}

/**
 * 节流函数
 * @param {Function} fn - 要节流的函数
 * @param {number} delay - 间隔时间(ms)
 * @returns {Function} 节流后的函数
 */
export function useThrottleFn(fn, delay) {
  let lastCall = 0;
  let timeoutId = null;

  return function(...args) {
    const now = Date.now();
    const timeSinceLastCall = now - lastCall;

    if (timeSinceLastCall >= delay) {
      // 距离上次调用足够久，直接执行
      lastCall = now;
      return fn.apply(this, args);
    } else {
      // 还在冷却期，设置定时器
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        lastCall = Date.now();
        fn.apply(this, args);
      }, delay - timeSinceLastCall);
    }
  };
}