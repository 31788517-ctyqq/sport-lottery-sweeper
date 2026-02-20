/**
 * 设备检测工具函数
 * 用于检测设备类型、屏幕尺寸、触摸支持等
 */

/**
 * 检测是否为移动设备
 * 基于用户代理字符串和屏幕尺寸判断
 * @returns {boolean} 是否为移动设备
 */
export function isMobileDevice() {
  // 用户代理检测
  const userAgent = navigator.userAgent || navigator.vendor || window.opera;
  const mobileRegex = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i;
  
  // 屏幕尺寸检测（移动设备通常宽度小于768px）
  const screenWidth = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
  
  // 触摸支持检测
  const hasTouchSupport = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  
  // 综合判断：用户代理匹配移动设备 或 屏幕宽度小于768px且有触摸支持
  return mobileRegex.test(userAgent) || (screenWidth < 768 && hasTouchSupport);
}

/**
 * 检测是否为平板设备
 * @returns {boolean} 是否为平板设备
 */
export function isTabletDevice() {
  const userAgent = navigator.userAgent || navigator.vendor || window.opera;
  const tabletRegex = /iPad|Android(?!.*Mobile)|Tablet|Silk/i;
  const screenWidth = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
  
  // 平板通常宽度在768px-1024px之间
  return tabletRegex.test(userAgent) || (screenWidth >= 768 && screenWidth <= 1024);
}

/**
 * 检测设备屏幕尺寸分类
 * @returns {string} 屏幕尺寸分类：'xs' (<375px), 'sm' (375-480px), 'md' (481-768px), 'lg' (769-1024px), 'xl' (>1024px)
 */
export function getScreenSize() {
  const width = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
  
  if (width < 375) return 'xs';      // 超小屏幕（小手机）
  if (width < 480) return 'sm';      // 小屏幕（手机）
  if (width < 768) return 'md';      // 中等屏幕（大手机/小平板）
  if (width < 1024) return 'lg';     // 大屏幕（平板/小笔记本）
  return 'xl';                       // 超大屏幕（桌面）
}

/**
 * 检测设备方向
 * @returns {string} 设备方向：'portrait'（竖屏）, 'landscape'（横屏）
 */
export function getDeviceOrientation() {
  if (window.matchMedia('(orientation: portrait)').matches) {
    return 'portrait';
  }
  return 'landscape';
}

/**
 * 检测是否支持触摸
 * @returns {boolean} 是否支持触摸
 */
export function hasTouchSupport() {
  return 'ontouchstart' in window || 
         navigator.maxTouchPoints > 0 || 
         navigator.msMaxTouchPoints > 0;
}

/**
 * 检测是否为iOS设备
 * @returns {boolean} 是否为iOS设备
 */
export function isIOS() {
  const userAgent = navigator.userAgent || navigator.vendor || window.opera;
  return /iPad|iPhone|iPod/.test(userAgent) && !window.MSStream;
}

/**
 * 检测是否为Android设备
 * @returns {boolean} 是否为Android设备
 */
export function isAndroid() {
  const userAgent = navigator.userAgent || navigator.vendor || window.opera;
  return /Android/.test(userAgent);
}

/**
 * 检测是否为微信浏览器
 * @returns {boolean} 是否为微信浏览器
 */
export function isWeChatBrowser() {
  const userAgent = navigator.userAgent || navigator.vendor || window.opera;
  return /MicroMessenger/i.test(userAgent);
}

/**
 * 获取设备像素比
 * @returns {number} 设备像素比
 */
export function getDevicePixelRatio() {
  return window.devicePixelRatio || 1;
}

/**
 * 检测是否支持某些CSS特性
 * @param {string} feature - CSS特性名称，如 'flexbox', 'grid', 'transform'
 * @returns {boolean} 是否支持该特性
 */
export function supportsCSSFeature(feature) {
  const style = document.createElement('div').style;
  
  const featureMap = {
    'flexbox': 'flexBasis',
    'grid': 'gridTemplateColumns',
    'transform': 'transform',
    'transition': 'transition',
    'animation': 'animation',
    'flexboxGap': 'gap',
    'sticky': 'position',
  };
  
  const property = featureMap[feature];
  return property ? property in style : false;
}

/**
 * 检测是否为高刷新率屏幕（≥90Hz）
 * @returns {Promise<boolean>} 是否为高刷新率屏幕
 */
export async function isHighRefreshRateScreen() {
  if ('hardwareConcurrency' in navigator) {
    // 简单判断：高刷新率屏幕通常与高性能设备相关
    return navigator.hardwareConcurrency >= 4;
  }
  
  // 通过requestAnimationFrame检测
  return new Promise(resolve => {
    let lastTime = 0;
    let frameCount = 0;
    let totalTime = 0;
    
    function checkFrame(timestamp) {
      if (lastTime !== 0) {
        const delta = timestamp - lastTime;
        totalTime += delta;
        frameCount++;
        
        if (totalTime >= 1000) { // 检测1秒
          const fps = frameCount;
          resolve(fps >= 90);
          return;
        }
      }
      
      lastTime = timestamp;
      requestAnimationFrame(checkFrame);
    }
    
    requestAnimationFrame(checkFrame);
  });
}

/**
 * 获取设备信息摘要
 * @returns {Object} 设备信息对象
 */
export function getDeviceInfo() {
  return {
    isMobile: isMobileDevice(),
    isTablet: isTabletDevice(),
    screenSize: getScreenSize(),
    orientation: getDeviceOrientation(),
    hasTouch: hasTouchSupport(),
    isIOS: isIOS(),
    isAndroid: isAndroid(),
    isWeChat: isWeChatBrowser(),
    pixelRatio: getDevicePixelRatio(),
    userAgent: navigator.userAgent || '',
    screenWidth: window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth,
    screenHeight: window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight,
    language: navigator.language || navigator.userLanguage || '',
    platform: navigator.platform || '',
  };
}

/**
 * 添加设备变化监听器
 * @param {Function} callback - 设备变化时的回调函数
 * @returns {Function} 移除监听器的函数
 */
export function addDeviceChangeListener(callback) {
  if (typeof callback !== 'function') {
    throw new Error('Callback must be a function');
  }
  
  const handleResize = () => {
    callback(getDeviceInfo());
  };
  
  const handleOrientationChange = () => {
    callback(getDeviceInfo());
  };
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleResize, { passive: true });
  
  // 监听设备方向变化
  window.addEventListener('orientationchange', handleOrientationChange, { passive: true });
  
  // 返回移除监听器的函数
  return () => {
    window.removeEventListener('resize', handleResize);
    window.removeEventListener('orientationchange', handleOrientationChange);
  };
}

/**
 * 根据设备类型获取推荐的布局模式
 * @returns {string} 布局模式：'desktop'（桌面）, 'mobile'（移动）, 'tablet'（平板）
 */
export function getRecommendedLayout() {
  const deviceInfo = getDeviceInfo();
  
  if (deviceInfo.isMobile && deviceInfo.screenSize !== 'lg' && deviceInfo.screenSize !== 'xl') {
    return 'mobile';
  } else if (deviceInfo.isTablet || deviceInfo.screenSize === 'lg') {
    return 'tablet';
  }
  
  return 'desktop';
}

export default {
  isMobileDevice,
  isTabletDevice,
  getScreenSize,
  getDeviceOrientation,
  hasTouchSupport,
  isIOS,
  isAndroid,
  isWeChatBrowser,
  getDevicePixelRatio,
  supportsCSSFeature,
  isHighRefreshRateScreen,
  getDeviceInfo,
  addDeviceChangeListener,
  getRecommendedLayout,
};