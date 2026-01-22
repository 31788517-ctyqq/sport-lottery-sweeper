// src/assets/locales/index.js
import zhCN from './zh-CN.json';
import enUS from './en-US.json';

const locales = {
  'zh-CN': zhCN,
  'en-US': enUS,
};

let currentLocale = 'zh-CN'; // 默认语言

export const setLocale = (locale) => {
  if (locales[locale]) {
    currentLocale = locale;
  } else {
    console.warn(`Locale '${locale}' not found, falling back to default.`);
  }
};

export const t = (key) => {
  const keys = key.split('.');
  let translation = locales[currentLocale];

  for (const k of keys) {
    translation = translation?.[k];
  }

  return translation || key; // 如果找不到翻译，则返回原始键名
};

export default locales;