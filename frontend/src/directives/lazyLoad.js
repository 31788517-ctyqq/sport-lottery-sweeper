/**
 * 懒加载指令
 * 用于图片、组件等资源的懒加载
 * 支持Intersection Observer API，回退到滚动监听
 */

/**
 * 懒加载配置
 */
const defaultConfig = {
  root: null,           // 观察器的根元素
  rootMargin: '0px',    // 根元素的外边距
  threshold: 0.1,       // 可见度阈值
  placeholder: null,    // 占位图URL
  error: null,         // 错误图URL
  loadingClass: 'lazy-loading',     // 加载中的CSS类
  loadedClass: 'lazy-loaded',       // 加载完成的CSS类
  errorClass: 'lazy-error',         // 加载错误的CSS类
  useNativeLoading: false,          // 是否使用原生loading属性
  observerOnce: true,               // 是否只观察一次
  delay: 0,                         // 延迟加载时间
  srcKey: 'src',                    // 源属性键名
  srcsetKey: 'srcset',              // 源集合属性键名
  backgroundImage: false,           // 是否作为背景图片
  callback: null                    // 加载完成后的回调
};

/**
 * 懒加载指令
 */
const lazyLoad = {
  mounted(el, binding) {
    const config = {
      ...defaultConfig,
      ...(binding.arg || {})
    };
    
    // 存储原始数据
    const originalSrc = el.getAttribute(config.srcKey);
    const originalSrcset = el.getAttribute(config.srcsetKey);
    
    if (!originalSrc && !originalSrcset) {
      console.warn('LazyLoad: No source attribute found');
      return;
    }
    
    // 存储原始数据到元素上
    el._lazyLoadData = {
      originalSrc,
      originalSrcset,
      config,
      loaded: false,
      error: false,
      observer: null
    };
    
    // 设置占位图
    if (config.placeholder) {
      if (config.backgroundImage) {
        el.style.backgroundImage = `url(${config.placeholder})`;
      } else {
        el.setAttribute(config.srcKey, config.placeholder);
      }
    }
    
    // 添加加载类
    el.classList.add(config.loadingClass);
    
    // 如果使用原生loading，直接设置
    if (config.useNativeLoading && 'loading' in HTMLImageElement.prototype) {
      el.setAttribute('loading', 'lazy');
      loadImage(el);
      return;
    }
    
    // 延迟加载
    if (config.delay > 0) {
      setTimeout(() => {
        initObserver(el);
      }, config.delay);
    } else {
      initObserver(el);
    }
  },
  
  updated(el, binding) {
    // 如果源发生变化，重新加载
    const lazyData = el._lazyLoadData;
    
    if (!lazyData) {
      return;
    }
    
    const newSrc = el.getAttribute(lazyData.config.srcKey);
    const newSrcset = el.getAttribute(lazyData.config.srcsetKey);
    
    if (newSrc !== lazyData.originalSrc || newSrcset !== lazyData.originalSrcset) {
      // 重置状态
      el.classList.remove(lazyData.config.loadedClass);
      el.classList.remove(lazyData.config.errorClass);
      el.classList.add(lazyData.config.loadingClass);
      
      lazyData.originalSrc = newSrc;
      lazyData.originalSrcset = newSrcset;
      lazyData.loaded = false;
      lazyData.error = false;
      
      // 重新观察
      if (lazyData.observer) {
        lazyData.observer.disconnect();
        lazyData.observer = null;
      }
      
      initObserver(el);
    }
  },
  
  beforeUnmount(el) {
    const lazyData = el._lazyLoadData;
    
    if (lazyData && lazyData.observer) {
      lazyData.observer.disconnect();
    }
    
    delete el._lazyLoadData;
  }
};

/**
 * 初始化观察器
 */
function initObserver(el) {
  const lazyData = el._lazyLoadData;
  
  // 检查是否已经在视口中
  if (isElementInViewport(el)) {
    loadImage(el);
    return;
  }
  
  // 使用Intersection Observer API
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            loadImage(el);
            
            // 如果只观察一次，则停止观察
            if (lazyData.config.observerOnce) {
              observer.unobserve(el);
              lazyData.observer = null;
            }
          }
        });
      },
      {
        root: lazyData.config.root,
        rootMargin: lazyData.config.rootMargin,
        threshold: lazyData.config.threshold
      }
    );
    
    observer.observe(el);
    lazyData.observer = observer;
  } else {
    // 回退方案：使用滚动监听
    initScrollListener(el);
  }
}

/**
 * 初始化滚动监听
 */
function initScrollListener(el) {
  const checkVisibility = () => {
    if (isElementInViewport(el)) {
      loadImage(el);
      window.removeEventListener('scroll', checkVisibility);
      window.removeEventListener('resize', checkVisibility);
    }
  };
  
  // 初始检查
  checkVisibility();
  
  // 监听滚动和窗口大小变化
  window.addEventListener('scroll', checkVisibility, { passive: true });
  window.addEventListener('resize', checkVisibility, { passive: true });
  
  // 存储清理函数
  el._lazyLoadScrollCleanup = () => {
    window.removeEventListener('scroll', checkVisibility);
    window.removeEventListener('resize', checkVisibility);
  };
}

/**
 * 检查元素是否在视口中
 */
function isElementInViewport(el) {
  const rect = el.getBoundingClientRect();
  const windowHeight = window.innerHeight || document.documentElement.clientHeight;
  const windowWidth = window.innerWidth || document.documentElement.clientWidth;
  
  // 检查元素是否在视口内
  return (
    rect.top <= windowHeight &&
    rect.bottom >= 0 &&
    rect.left <= windowWidth &&
    rect.right >= 0
  );
}

/**
 * 加载图片
 */
function loadImage(el) {
  const lazyData = el._lazyLoadData;
  
  if (lazyData.loaded || lazyData.error) {
    return;
  }
  
  const { originalSrc, originalSrcset, config } = lazyData;
  
  // 创建Image对象预加载
  const img = new Image();
  
  img.onload = () => {
    lazyData.loaded = true;
    
    // 更新元素
    updateElement(el, originalSrc, originalSrcset, config);
    
    // 更新类名
    el.classList.remove(config.loadingClass);
    el.classList.add(config.loadedClass);
    
    // 执行回调
    if (typeof config.callback === 'function') {
      config.callback(el, 'loaded');
    }
    
    // 触发加载完成事件
    el.dispatchEvent(new CustomEvent('lazyload:loaded', {
      detail: { element: el, src: originalSrc }
    }));
  };
  
  img.onerror = () => {
    lazyData.error = true;
    
    // 设置错误图
    if (config.error) {
      updateElement(el, config.error, null, config);
    }
    
    // 更新类名
    el.classList.remove(config.loadingClass);
    el.classList.add(config.errorClass);
    
    // 执行回调
    if (typeof config.callback === 'function') {
      config.callback(el, 'error');
    }
    
    // 触发加载错误事件
    el.dispatchEvent(new CustomEvent('lazyload:error', {
      detail: { element: el, src: originalSrc }
    }));
  };
  
  // 开始加载
  if (originalSrc) {
    img.src = originalSrc;
  }
  
  // 如果有srcset也加载
  if (originalSrcset) {
    img.srcset = originalSrcset;
  }
}

/**
 * 更新元素属性
 */
function updateElement(el, src, srcset, config) {
  if (config.backgroundImage) {
    // 背景图片
    el.style.backgroundImage = `url(${src})`;
  } else {
    // 普通图片或iframe
    if (src) {
      el.setAttribute(config.srcKey, src);
    }
    
    if (srcset) {
      el.setAttribute(config.srcsetKey, srcset);
    }
  }
}

/**
 * 懒加载管理器
 */
export class LazyLoadManager {
  constructor() {
    this.observers = new Map();
    this.instances = new Set();
  }
  
  /**
   * 注册懒加载元素
   * @param {HTMLElement} element - 要懒加载的元素
   * @param {Object} options - 配置选项
   * @returns {Function} 取消注册的函数
   */
  register(element, options = {}) {
    const config = { ...defaultConfig, ...options };
    
    // 创建IntersectionObserver
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const el = entry.target;
            const instance = this.getInstance(el);
            
            if (instance) {
              this.loadElement(el, instance);
              
              if (config.observerOnce) {
                observer.unobserve(el);
              }
            }
          }
        });
      },
      {
        root: config.root,
        rootMargin: config.rootMargin,
        threshold: config.threshold
      }
    );
    
    // 存储实例数据
    const instance = {
      element,
      config,
      observer,
      loaded: false,
      data: {}
    };
    
    this.instances.add(instance);
    this.observers.set(element, observer);
    
    // 开始观察
    observer.observe(element);
    
    // 返回清理函数
    return () => {
      this.unregister(element);
    };
  }
  
  /**
   * 获取元素实例
   */
  getInstance(element) {
    for (const instance of this.instances) {
      if (instance.element === element) {
        return instance;
      }
    }
    return null;
  }
  
  /**
   * 加载元素
   */
  loadElement(element, instance) {
    if (instance.loaded) return;
    
    const { config } = instance;
    
    // 模拟加载逻辑
    setTimeout(() => {
      instance.loaded = true;
      
      // 触发事件
      element.dispatchEvent(new CustomEvent('lazyload:loaded'));
      
      // 执行回调
      if (typeof config.callback === 'function') {
        config.callback(element);
      }
    }, 100);
  }
  
  /**
   * 取消注册
   */
  unregister(element) {
    const observer = this.observers.get(element);
    
    if (observer) {
      observer.disconnect();
      this.observers.delete(element);
    }
    
    // 移除实例
    for (const instance of this.instances) {
      if (instance.element === element) {
        this.instances.delete(instance);
        break;
      }
    }
  }
  
  /**
   * 手动触发加载
   */
  loadAll() {
    this.instances.forEach(instance => {
      if (!instance.loaded) {
        this.loadElement(instance.element, instance);
      }
    });
  }
  
  /**
   * 清理所有
   */
  destroy() {
    this.observers.forEach(observer => observer.disconnect());
    this.observers.clear();
    this.instances.clear();
  }
}

// 全局懒加载管理器实例
export const lazyLoadManager = new LazyLoadManager();

/**
 * 懒加载指令的高级版本（使用管理器）
 */
export const vLazyLoadManaged = {
  mounted(el, binding) {
    const config = {
      ...defaultConfig,
      ...(binding.arg || {})
    };
    
    // 使用管理器注册
    const unregister = lazyLoadManager.register(el, config);
    
    // 存储清理函数
    el._lazyLoadUnregister = unregister;
  },
  
  beforeUnmount(el) {
    if (el._lazyLoadUnregister) {
      el._lazyLoadUnregister();
      delete el._lazyLoadUnregister;
    }
  }
};

/**
 * 安装指令到Vue应用
 * @param {Object} app - Vue应用实例
 */
export const installLazyLoad = (app) => {
  app.directive('lazy', lazyLoad);
  app.directive('lazy-managed', vLazyLoadManaged);
  
  // 提供懒加载管理器
  app.provide('lazy-load-manager', lazyLoadManager);
};

/**
 * 组合式API中使用懒加载的函数
 */
export const useLazyLoad = () => {
  const loadImage = (src, options = {}) => {
    return new Promise((resolve, reject) => {
      const img = new Image();
      
      img.onload = () => resolve(img);
      img.onerror = reject;
      
      if (options.crossOrigin) {
        img.crossOrigin = options.crossOrigin;
      }
      
      img.src = src;
    });
  };
  
  const loadImages = (sources, options = {}) => {
    const promises = sources.map(src => loadImage(src, options));
    return Promise.all(promises);
  };
  
  const createObserver = (element, callback, options = {}) => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          callback(entry.target);
          
          if (options.once) {
            observer.unobserve(entry.target);
          }
        }
      });
    }, options);
    
    observer.observe(element);
    
    return {
      observer,
      disconnect: () => observer.disconnect()
    };
  };
  
  return {
    lazyLoadManager,
    loadImage,
    loadImages,
    createObserver,
    isElementInViewport
  };
};

export default lazyLoad;