/**
 * 地区配置管理
 * 包含语言设置、区域设置、格式设置等
 */

/**
 * 地区配置
 */
export const localeConfig = {
  // 支持的语言列表
  availableLocales: ['zh-CN', 'en-US', 'ja-JP', 'ko-KR'],
  
  // 默认语言
  defaultLocale: 'zh-CN',
  
  // 语言显示名称
  localeNames: {
    'zh-CN': '中文 (简体)',
    'en-US': 'English (US)',
    'ja-JP': '日本語',
    'ko-KR': '한국어'
  },
  
  // 本地语言名称
  nativeNames: {
    'zh-CN': '简体中文',
    'en-US': 'English',
    'ja-JP': '日本語',
    'ko-KR': '한국어'
  },
  
  // 语言图标/标志
  flags: {
    'zh-CN': '🇨🇳',
    'en-US': '🇺🇸',
    'ja-JP': '🇯🇵',
    'ko-KR': '🇰🇷'
  },
  
  // 从右到左的语言（如阿拉伯语、希伯来语）
  rtlLocales: [],
  
  // 语言加载配置
  loadingConfig: {
    // 是否启用懒加载
    lazy: true,
    // 懒加载前缀
    prefix: 'locales/',
    // 文件后缀
    suffix: '.json'
  },
  
  // 日期格式配置
  dateFormats: {
    'zh-CN': 'YYYY-MM-DD',
    'en-US': 'MM/DD/YYYY',
    'ja-JP': 'YYYY/MM/DD',
    'ko-KR': 'YYYY.MM.DD'
  },
  
  // 时间格式配置
  timeFormats: {
    'zh-CN': 'HH:mm',
    'en-US': 'h:mm A',
    'ja-JP': 'HH:mm',
    'ko-KR': 'HH:mm'
  },
  
  // 数字格式配置
  numberFormats: {
    'zh-CN': {
      decimalSeparator: '.',
      thousandSeparator: ',',
      decimalDigits: 2
    },
    'en-US': {
      decimalSeparator: '.',
      thousandSeparator: ',',
      decimalDigits: 2
    },
    'ja-JP': {
      decimalSeparator: '.',
      thousandSeparator: ',',
      decimalDigits: 2
    },
    'ko-KR': {
      decimalSeparator: '.',
      thousandSeparator: ',',
      decimalDigits: 2
    }
  },
  
  // 货币配置
  currencyConfig: {
    'zh-CN': {
      code: 'CNY',
      symbol: '¥',
      position: 'before',
      decimalDigits: 2
    },
    'en-US': {
      code: 'USD',
      symbol: '$',
      position: 'before',
      decimalDigits: 2
    },
    'ja-JP': {
      code: 'JPY',
      symbol: '¥',
      position: 'before',
      decimalDigits: 0
    },
    'ko-KR': {
      code: 'KRW',
      symbol: '₩',
      position: 'before',
      decimalDigits: 0
    }
  },
  
  // 时区配置
  timezoneConfig: {
    'zh-CN': 'Asia/Shanghai',
    'en-US': 'America/New_York',
    'ja-JP': 'Asia/Tokyo',
    'ko-KR': 'Asia/Seoul'
  },
  
  // 第一周开始日
  firstDayOfWeek: {
    'zh-CN': 0, // 周日
    'en-US': 0, // 周日
    'ja-JP': 0, // 周日
    'ko-KR': 0  // 周日
  }
};

/**
 * 获取浏览器语言设置
 * @returns {string} 浏览器语言代码
 */
export function getBrowserLocale() {
  // 获取浏览器语言
  const browserLocale = navigator.language || 
                       navigator.userLanguage || 
                       navigator.browserLanguage || 
                       navigator.systemLanguage;
  
  // 标准化语言代码
  return standardizeLocaleCode(browserLocale);
}

/**
 * 标准化语言代码
 * @param {string} locale - 原始语言代码
 * @returns {string} 标准化后的语言代码
 */
export function standardizeLocaleCode(locale) {
  if (!locale) return localeConfig.defaultLocale;
  
  // 转换为标准格式（如：zh-CN）
  const parts = locale.split(/[-_]/);
  const language = parts[0].toLowerCase();
  const region = parts[1] ? parts[1].toUpperCase() : '';
  
  // 构建标准代码
  const standardCode = region ? `${language}-${region}` : language;
  
  // 检查是否支持
  const supportedLocale = localeConfig.availableLocales.find(locale => 
    locale.toLowerCase() === standardCode.toLowerCase() ||
    locale.split('-')[0].toLowerCase() === language
  );
  
  return supportedLocale || localeConfig.defaultLocale;
}

/**
 * 获取存储的用户语言设置
 * @returns {string|null} 存储的语言设置
 */
export function getStoredLocale() {
  try {
    const storedLocale = localStorage.getItem('user_locale');
    if (storedLocale && localeConfig.availableLocales.includes(storedLocale)) {
      return storedLocale;
    }
  } catch (error) {
    console.warn('Failed to read locale from localStorage:', error);
  }
  
  return null;
}

/**
 * 保存用户语言设置
 * @param {string} locale - 语言代码
 * @returns {boolean} 是否保存成功
 */
export function saveLocale(locale) {
  try {
    if (localeConfig.availableLocales.includes(locale)) {
      localStorage.setItem('user_locale', locale);
      return true;
    }
  } catch (error) {
    console.error('Failed to save locale to localStorage:', error);
  }
  
  return false;
}

/**
 * 清除用户语言设置
 */
export function clearLocale() {
  try {
    localStorage.removeItem('user_locale');
  } catch (error) {
    console.warn('Failed to clear locale from localStorage:', error);
  }
}

/**
 * 检测语言方向
 * @param {string} locale - 语言代码
 * @returns {string} 文本方向 (ltr/rtl)
 */
export function getTextDirection(locale) {
  return localeConfig.rtlLocales.includes(locale) ? 'rtl' : 'ltr';
}

/**
 * 获取语言相关信息
 * @param {string} locale - 语言代码
 * @returns {Object} 语言信息
 */
export function getLocaleInfo(locale) {
  const standardizedLocale = standardizeLocaleCode(locale);
  
  return {
    code: standardizedLocale,
    name: localeConfig.localeNames[standardizedLocale] || standardizedLocale,
    nativeName: localeConfig.nativeNames[standardizedLocale] || standardizedLocale,
    flag: localeConfig.flags[standardizedLocale] || '🌐',
    direction: getTextDirection(standardizedLocale),
    dateFormat: localeConfig.dateFormats[standardizedLocale] || 'YYYY-MM-DD',
    timeFormat: localeConfig.timeFormats[standardizedLocale] || 'HH:mm',
    timezone: localeConfig.timezoneConfig[standardizedLocale] || 'UTC',
    firstDayOfWeek: localeConfig.firstDayOfWeek[standardizedLocale] || 0
  };
}

/**
 * 获取所有支持的语言信息
 * @returns {Array} 语言信息列表
 */
export function getAllLocaleInfos() {
  return localeConfig.availableLocales.map(getLocaleInfo);
}

/**
 * 格式化数字（根据地区）
 * @param {number} number - 要格式化的数字
 * @param {string} locale - 语言代码
 * @param {Object} options - 格式化选项
 * @returns {string} 格式化后的数字
 */
export function formatNumber(number, locale = 'zh-CN', options = {}) {
  const localeInfo = getLocaleInfo(locale);
  const config = localeConfig.numberFormats[localeInfo.code] || 
                 localeConfig.numberFormats[localeConfig.defaultLocale];
  
  const { 
    decimalDigits = config.decimalDigits,
    decimalSeparator = config.decimalSeparator,
    thousandSeparator = config.thousandSeparator 
  } = options;
  
  // 格式化整数部分
  let integerPart = Math.floor(Math.abs(number)).toString();
  let formattedInteger = '';
  
  for (let i = integerPart.length - 1, count = 0; i >= 0; i--, count++) {
    if (count > 0 && count % 3 === 0) {
      formattedInteger = thousandSeparator + formattedInteger;
    }
    formattedInteger = integerPart[i] + formattedInteger;
  }
  
  // 格式化小数部分
  let decimalPart = '';
  if (decimalDigits > 0) {
    const multiplier = Math.pow(10, decimalDigits);
    decimalPart = Math.round((Math.abs(number) % 1) * multiplier)
      .toString()
      .padStart(decimalDigits, '0');
    
    decimalPart = decimalSeparator + decimalPart;
  }
  
  // 处理负数
  const sign = number < 0 ? '-' : '';
  
  return sign + formattedInteger + decimalPart;
}

/**
 * 格式化货币（根据地区）
 * @param {number} amount - 金额
 * @param {string} locale - 语言代码
 * @param {Object} options - 格式化选项
 * @returns {string} 格式化后的货币
 */
export function formatCurrency(amount, locale = 'zh-CN', options = {}) {
  const localeInfo = getLocaleInfo(locale);
  const config = localeConfig.currencyConfig[localeInfo.code] || 
                 localeConfig.currencyConfig[localeConfig.defaultLocale];
  
  const {
    showSymbol = true,
    showCode = false
  } = options;
  
  // 格式化数字
  const formattedNumber = formatNumber(amount, locale, {
    decimalDigits: config.decimalDigits
  });
  
  // 构建结果
  let result = formattedNumber;
  
  if (showSymbol) {
    result = config.position === 'before' 
      ? `${config.symbol}${result}` 
      : `${result}${config.symbol}`;
  }
  
  if (showCode) {
    result += ` ${config.code}`;
  }
  
  return result;
}

/**
 * 格式化日期（根据地区）
 * @param {Date|string|number} date - 日期
 * @param {string} locale - 语言代码
 * @param {string} format - 格式模板
 * @returns {string} 格式化后的日期
 */
export function formatDate(date, locale = 'zh-CN', format = 'default') {
  const dateObj = new Date(date);
  const localeInfo = getLocaleInfo(locale);
  
  // 获取日期部分
  const year = dateObj.getFullYear();
  const month = dateObj.getMonth() + 1;
  const day = dateObj.getDate();
  
  // 根据格式模板格式化
  const formatMap = {
    'zh-CN': {
      default: `${year}-${padZero(month)}-${padZero(day)}`,
      short: `${padZero(month)}-${padZero(day)}`,
      long: `${year}年${padZero(month)}月${padZero(day)}日`,
      relative: getRelativeDate(dateObj, locale)
    },
    'en-US': {
      default: `${padZero(month)}/${padZero(day)}/${year}`,
      short: `${padZero(month)}/${padZero(day)}`,
      long: getEnglishMonth(month) + ' ' + day + ', ' + year,
      relative: getRelativeDate(dateObj, locale)
    },
    'ja-JP': {
      default: `${year}/${padZero(month)}/${padZero(day)}`,
      short: `${padZero(month)}/${padZero(day)}`,
      long: `${year}年${padZero(month)}月${padZero(day)}日`,
      relative: getRelativeDate(dateObj, locale)
    },
    'ko-KR': {
      default: `${year}.${padZero(month)}.${padZero(day)}`,
      short: `${padZero(month)}.${padZero(day)}`,
      long: `${year}년 ${padZero(month)}월 ${padZero(day)}일`,
      relative: getRelativeDate(dateObj, locale)
    }
  };
  
  const localeFormat = formatMap[localeInfo.code] || formatMap[localeConfig.defaultLocale];
  return localeFormat[format] || localeFormat.default;
}

/**
 * 补零函数
 */
function padZero(num) {
  return num.toString().padStart(2, '0');
}

/**
 * 获取英文月份
 */
function getEnglishMonth(month) {
  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];
  return months[month - 1];
}

/**
 * 获取相对日期描述
 */
function getRelativeDate(date, locale) {
  const now = new Date();
  const diffTime = Math.abs(now - date);
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) {
    return locale === 'zh-CN' ? '今天' : 'Today';
  } else if (diffDays === 1) {
    return locale === 'zh-CN' ? '昨天' : 'Yesterday';
  } else if (diffDays === 2) {
    return locale === 'zh-CN' ? '前天' : 'The day before yesterday';
  } else if (diffDays < 7) {
    return locale === 'zh-CN' ? `${diffDays}天前` : `${diffDays} days ago`;
  } else {
    return formatDate(date, locale, 'default');
  }
}

/**
 * 获取时区偏移
 * @param {string} locale - 语言代码
 * @returns {string} 时区偏移
 */
export function getTimezoneOffset(locale = 'zh-CN') {
  const localeInfo = getLocaleInfo(locale);
  const timezone = localeInfo.timezone;
  
  // 这里可以扩展为实际获取时区偏移的逻辑
  // 目前返回示例值
  const offsetMap = {
    'Asia/Shanghai': '+08:00',
    'America/New_York': '-05:00',
    'Asia/Tokyo': '+09:00',
    'Asia/Seoul': '+09:00'
  };
  
  return offsetMap[timezone] || '+00:00';
}

/**
 * 语言切换器工具
 */
export const localeSwitcher = {
  /**
   * 切换语言
   * @param {string} locale - 目标语言代码
   * @param {Function} callback - 切换后的回调函数
   */
  switch(locale, callback = null) {
    if (!localeConfig.availableLocales.includes(locale)) {
      console.warn(`Locale ${locale} is not supported`);
      return false;
    }
    
    // 保存设置
    saveLocale(locale);
    
    // 更新HTML lang属性
    document.documentElement.lang = locale;
    
    // 更新文本方向
    const direction = getTextDirection(locale);
    document.documentElement.dir = direction;
    
    // 触发事件
    window.dispatchEvent(new CustomEvent('localechange', {
      detail: { locale, direction }
    }));
    
    // 执行回调
    if (typeof callback === 'function') {
      callback(locale, direction);
    }
    
    return true;
  },
  
  /**
   * 获取当前语言
   * @returns {string} 当前语言
   */
  getCurrent() {
    return getStoredLocale() || getBrowserLocale() || localeConfig.defaultLocale;
  },
  
  /**
   * 监听语言变化
   * @param {Function} handler - 处理函数
   * @returns {Function} 取消监听函数
   */
  onChange(handler) {
    const eventHandler = (event) => {
      handler(event.detail.locale, event.detail.direction);
    };
    
    window.addEventListener('localechange', eventHandler);
    
    return () => {
      window.removeEventListener('localechange', eventHandler);
    };
  }
};

/**
 * 组合式API中使用地区的函数
 */
export const useLocale = () => {
  const currentLocale = localeSwitcher.getCurrent();
  const localeInfo = getLocaleInfo(currentLocale);
  
  return {
    // 当前地区信息
    current: currentLocale,
    info: localeInfo,
    direction: localeInfo.direction,
    
    // 所有可用地区
    available: getAllLocaleInfos(),
    
    // 切换地区
    switch: localeSwitcher.switch,
    
    // 格式化函数
    formatNumber: (number, options) => formatNumber(number, currentLocale, options),
    formatCurrency: (amount, options) => formatCurrency(amount, currentLocale, options),
    formatDate: (date, format) => formatDate(date, currentLocale, format),
    
    // 监听变化
    onChange: localeSwitcher.onChange
  };
};

export default {
  localeConfig,
  getBrowserLocale,
  getStoredLocale,
  saveLocale,
  clearLocale,
  getLocaleInfo,
  getAllLocaleInfos,
  formatNumber,
  formatCurrency,
  formatDate,
  getTimezoneOffset,
  localeSwitcher,
  useLocale
};