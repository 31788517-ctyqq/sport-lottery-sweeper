const i18n = createI18n({
  locale: 'zh-CN',
  fallbackLocale: 'zh-CN',
  messages: {
    'zh-CN': {
      // ... 翻译内容 ...
    }
  },
  // 移除或注释掉可能导致问题的配置
  // availableLocales: ['zh-CN', 'en-US'], // 这个属性可能是只读的
  // 其他配置...
})

export default i18n