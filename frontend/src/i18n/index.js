/**
 * 国际化配置入口文件
 * 基于 Vue I18n 构建的多语言支持
 */

import { createI18n } from 'vue-i18n';
import { messages } from './messages.js';
import { localeConfig, getBrowserLocale, getStoredLocale } from './locale.js';

/**
 * 创建I18n实例
 * @returns {Object} Vue I18n实例
 */
export function createI18nInstance() {
  // 获取当前语言
  const currentLocale = getCurrentLocale();
  
  // 创建I18n实例
  const i18n = createI18n({
    legacy: false, // 使用Composition API模式
    locale: currentLocale,
    fallbackLocale: localeConfig.defaultLocale,
    messages,
    datetimeFormats: createDatetimeFormats(),
    numberFormats: createNumberFormats(),
    silentTranslationWarn: import.meta.env.MODE === 'production',
    missingWarn: false,
    fallbackWarn: false,
    silentFallbackWarn: true,
    warnHtmlMessage: false,
    modifiers: {
      // 自定义修饰符
      uppercase: (str) => str.toUpperCase(),
      lowercase: (str) => str.toLowerCase(),
      capitalize: (str) => str.charAt(0).toUpperCase() + str.slice(1),
      // 足球相关修饰符
      team: (str) => `[${str}]`,
      odds: (num) => parseFloat(num).toFixed(2),
      percentage: (num) => `${(num * 100).toFixed(1)}%`
    },
    pluralizationRules: {
      // 自定义复数规则
      'zh-CN': (choice, choicesLength) => {
        // 中文复数规则
        if (choice === 0) return 0;
        return choice;
      },
      'en-US': (choice, choicesLength) => {
        // 英文复数规则
        if (choicesLength === 2) {
          return choice ? 1 : 0;
        }
        return choice;
      }
    }
  });
  
  // 设置全局属性 - 移除对只读属性的赋值
  i18n.global.locale = currentLocale;
  // 移除下面这行，因为availableLocales是只读属性
  // i18n.global.availableLocales = localeConfig.availableLocales;
  
  return i18n;
}

/**
 * 获取当前语言设置
 * @returns {string} 当前语言代码
 */
function getCurrentLocale() {
  // 1. 从存储中获取用户设置
  const storedLocale = getStoredLocale();
  if (storedLocale) {
    return storedLocale;
  }
  
  // 2. 从浏览器设置获取
  const browserLocale = getBrowserLocale();
  const matchedLocale = localeConfig.availableLocales.find(locale => 
    locale === browserLocale || locale.startsWith(browserLocale.split('-')[0])
  );
  
  if (matchedLocale) {
    return matchedLocale;
  }
  
  // 3. 使用默认语言
  return localeConfig.defaultLocale;
}

/**
 * 创建日期时间格式配置
 * @returns {Object} 日期时间格式
 */
function createDatetimeFormats() {
  return {
    'zh-CN': {
      short: {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      },
      long: {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long',
        hour: 'numeric',
        minute: 'numeric'
      },
      date: {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      },
      time: {
        hour: '2-digit',
        minute: '2-digit'
      },
      matchTime: {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
      },
      relative: {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }
    },
    'en-US': {
      short: {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      },
      long: {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'long',
        hour: 'numeric',
        minute: 'numeric',
        hour12: true
      },
      date: {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
      },
      time: {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      },
      matchTime: {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      },
      relative: {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
      }
    }
  };
}

/**
 * 创建数字格式配置
 * @returns {Object} 数字格式
 */
function createNumberFormats() {
  return {
    'zh-CN': {
      currency: {
        style: 'currency',
        currency: 'CNY',
        currencyDisplay: 'symbol'
      },
      decimal: {
        style: 'decimal',
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
      },
      odds: {
        style: 'decimal',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      },
      percentage: {
        style: 'percent',
        minimumFractionDigits: 1,
        maximumFractionDigits: 2
      },
      integer: {
        style: 'decimal',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }
    },
    'en-US': {
      currency: {
        style: 'currency',
        currency: 'USD',
        currencyDisplay: 'symbol'
      },
      decimal: {
        style: 'decimal',
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
      },
      odds: {
        style: 'decimal',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      },
      percentage: {
        style: 'percent',
        minimumFractionDigits: 1,
        maximumFractionDigits: 2
      },
      integer: {
        style: 'decimal',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }
    }
  };
}

/**
 * 语言切换器
 */
export const localeSwitcher = {
  /**
   * 切换语言
   * @param {string} locale - 目标语言代码
   * @param {Object} i18n - I18n实例
   */
  switchLocale(locale, i18n) {
    if (!localeConfig.availableLocales.includes(locale)) {
      console.warn(`Locale ${locale} is not supported`);
      return false;
    }
    
    try {
      // 更新I18n实例的语言设置
      i18n.global.locale = locale;
      
      // 存储用户选择
      localStorage.setItem('user_locale', locale);
      
      // 更新HTML lang属性
      document.documentElement.lang = locale;
      
      // 触发语言切换事件
      window.dispatchEvent(new CustomEvent('localeChanged', { 
        detail: { locale } 
      }));
      
      return true;
    } catch (error) {
      console.error('Failed to switch locale:', error);
      return false;
    }
  },
  
  /**
   * 获取当前语言
   * @param {Object} i18n - I18n实例
   * @returns {string} 当前语言
   */
  getCurrentLocale(i18n) {
    return i18n.global.locale;
  },
  
  /**
   * 获取支持的语言列表
   * @returns {Array} 语言列表
   */
  getAvailableLocales() {
    return localeConfig.availableLocales.map(code => ({
      code,
      name: localeConfig.localeNames[code] || code,
      nativeName: localeConfig.nativeNames[code] || code,
      flag: localeConfig.flags[code]
    }));
  },
  
  /**
   * 检测语言方向
   * @param {string} locale - 语言代码
   * @returns {string} 文本方向 (ltr/rtl)
   */
  getTextDirection(locale) {
    return localeConfig.rtlLocales.includes(locale) ? 'rtl' : 'ltr';
  }
};

/**
 * 翻译工具函数
 */
export const translationUtils = {
  /**
   * 获取带参数的翻译
   * @param {Object} i18n - I18n实例
   * @param {string} key - 翻译键
   * @param {Object} params - 参数对象
   * @returns {string} 翻译结果
   */
  t(i18n, key, params = {}) {
    return i18n.global.t(key, params);
  },
  
  /**
   * 获取复数翻译
   * @param {Object} i18n - I18n实例
   * @param {string} key - 翻译键
   * @param {number} count - 数量
   * @param {Object} params - 参数对象
   * @returns {string} 翻译结果
   */
  tc(i18n, key, count, params = {}) {
    return i18n.global.t(key, { ...params, n: count });
  },
  
  /**
   * 获取日期时间格式
   * @param {Object} i18n - I18n实例
   * @param {Date|string|number} value - 日期值
   * @param {Object} options - 格式选项
   * @returns {string} 格式化后的日期时间
   */
  d(i18n, value, options = {}) {
    return i18n.global.d(value, options);
  },
  
  /**
   * 获取数字格式
   * @param {Object} i18n - I18n实例
   * @param {number} value - 数字值
   * @param {Object} options - 格式选项
   * @returns {string} 格式化后的数字
   */
  n(i18n, value, options = {}) {
    return i18n.global.n(value, options);
  },
  
  /**
   * 检查翻译是否存在
   * @param {Object} i18n - I18n实例
   * @param {string} key - 翻译键
   * @returns {boolean} 是否存在
   */
  te(i18n, key) {
    return i18n.global.te(key);
  },
  
  /**
   * 获取所有可用翻译键
   * @param {Object} i18n - I18n实例
   * @returns {Array} 翻译键列表
   */
  getTranslationKeys(i18n) {
    const keys = [];
    const traverse = (obj, path = '') => {
      for (const key in obj) {
        const currentPath = path ? `${path}.${key}` : key;
        if (typeof obj[key] === 'string') {
          keys.push(currentPath);
        } else if (typeof obj[key] === 'object') {
          traverse(obj[key], currentPath);
        }
      }
    };
    
    traverse(i18n.global.messages[i18n.global.locale]);
    return keys;
  }
};

/**
 * 足球比赛相关翻译辅助函数
 */
export const footballTranslations = {
  /**
   * 翻译联赛名称
   * @param {Object} i18n - I18n实例
   * @param {string} leagueCode - 联赛代码
   * @returns {string} 联赛名称
   */
  translateLeague(i18n, leagueCode) {
    const key = `leagues.${leagueCode}`;
    return i18n.global.te(key) 
      ? i18n.global.t(key) 
      : leagueCode;
  },
  
  /**
   * 翻译球队名称
   * @param {Object} i18n - I18n实例
   * @param {string} teamCode - 球队代码
   * @returns {string} 球队名称
   */
  translateTeam(i18n, teamCode) {
    const key = `teams.${teamCode}`;
    return i18n.global.te(key) 
      ? i18n.global.t(key) 
      : teamCode;
  },
  
  /**
   * 翻译情报类型
   * @param {Object} i18n - I18n实例
   * @param {string} type - 情报类型
   * @returns {string} 情报类型名称
   */
  translateIntelligenceType(i18n, type) {
    const key = `intelligence.types.${type}`;
    return i18n.global.te(key) 
      ? i18n.global.t(key) 
      : type;
  },
  
  /**
   * 翻译比赛状态
   * @param {Object} i18n - I18n实例
   * @param {string} status - 比赛状态
   * @returns {string} 状态名称
   */
  translateMatchStatus(i18n, status) {
    const key = `matches.status.${status}`;
    return i18n.global.te(key) 
      ? i18n.global.t(key) 
      : status;
  },
  
  /**
   * 格式化赔率
   * @param {Object} i18n - I18n实例
   * @param {number} odds - 赔率值
   * @returns {string} 格式化后的赔率
   */
  formatOdds(i18n, odds) {
    return i18n.global.n(odds, 'odds');
  },
  
  /**
   * 格式化比赛时间
   * @param {Object} i18n - I18n实例
   * @param {Date} date - 比赛时间
   * @returns {string} 格式化后的时间
   */
  formatMatchTime(i18n, date) {
    return i18n.global.d(date, 'matchTime');
  },
  
  /**
   * 获取相对时间描述
   * @param {Object} i18n - I18n实例
   * @param {Date} date - 日期
   * @returns {string} 相对时间描述
   */
  getRelativeTime(i18n, date) {
    const now = new Date();
    const diffMs = date - now;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    
    if (diffDays > 0) {
      return i18n.global.tc('time.days', diffDays, { n: diffDays });
    } else if (diffHours > 0) {
      return i18n.global.tc('time.hours', diffHours, { n: diffHours });
    } else if (diffMinutes > 0) {
      return i18n.global.tc('time.minutes', diffMinutes, { n: diffMinutes });
    } else {
      return i18n.global.t('time.now');
    }
  }
};

/**
 * 组合式API中使用国际化的函数
 */
export const useI18n = () => {
  // 在组件中使用时，通过inject获取i18n实例
  const getI18n = () => {
    if (window.__VUE_APP_I18N__) {
      return window.__VUE_APP_I18N__;
    }
    return null;
  };
  
  const i18n = getI18n();
  
  return {
    // 基础翻译函数
    t: (key, params) => i18n ? translationUtils.t(i18n, key, params) : key,
    tc: (key, count, params) => i18n ? translationUtils.tc(i18n, key, count, params) : key,
    d: (value, options) => i18n ? translationUtils.d(i18n, value, options) : value,
    n: (value, options) => i18n ? translationUtils.n(i18n, value, options) : value,
    te: (key) => i18n ? translationUtils.te(i18n, key) : false,
    
    // 语言切换
    locale: i18n ? i18n.global.locale : localeConfig.defaultLocale,
    availableLocales: localeSwitcher.getAvailableLocales(),
    switchLocale: (locale) => i18n ? localeSwitcher.switchLocale(locale, i18n) : false,
    
    // 足球相关辅助函数
    translateLeague: (leagueCode) => i18n ? footballTranslations.translateLeague(i18n, leagueCode) : leagueCode,
    translateTeam: (teamCode) => i18n ? footballTranslations.translateTeam(i18n, teamCode) : teamCode,
    translateIntelligenceType: (type) => i18n ? footballTranslations.translateIntelligenceType(i18n, type) : type,
    translateMatchStatus: (status) => i18n ? footballTranslations.translateMatchStatus(i18n, status) : status,
    formatOdds: (odds) => i18n ? footballTranslations.formatOdds(i18n, odds) : odds,
    formatMatchTime: (date) => i18n ? footballTranslations.formatMatchTime(i18n, date) : date,
    getRelativeTime: (date) => i18n ? footballTranslations.getRelativeTime(i18n, date) : ''
  };
};

// 导出I18n实例创建函数
export default createI18nInstance;