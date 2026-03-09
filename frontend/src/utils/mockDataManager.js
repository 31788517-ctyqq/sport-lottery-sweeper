// 模拟数据管理器 - 便于管理和清除模拟数据
class MockDataManager {
  constructor() {
    this.isMockEnabled = !!(import.meta.env.DEV || import.meta.env.MODE === 'development')
    this.storageKey = 'sport-lottery-mock-data'
  }

  /**
   * 检查是否启用模拟数据
   */
  isEnabled() {
    return this.isMockEnabled
  }

  /**
   * 启用模拟数据
   */
  enable() {
    this.isMockEnabled = true
    console.log('🎭 模拟数据已启用')
  }

  /**
   * 禁用模拟数据
   */
  disable() {
    this.isMockEnabled = false
    console.log('🎭 模拟数据已禁用')
  }

  /**
   * 清除所有模拟数据痕迹
   */
  clearAll() {
    // 清除localStorage中的模拟数据
    localStorage.removeItem(this.storageKey)
    localStorage.removeItem(`${this.storageKey}-timestamp`)
    
    // 清除sessionStorage中的模拟数据
    sessionStorage.removeItem(this.storageKey)
    
    console.log('🧹 所有模拟数据痕迹已清除')
  }

  /**
   * 获取模拟数据状态
   */
  getStatus() {
    return {
      enabled: this.isMockEnabled,
      storageKeys: [
        this.storageKey,
        `${this.storageKey}-timestamp`
      ],
      environment: import.meta.env.MODE
    }
  }

  /**
   * 导出模拟数据配置（便于备份/迁移）
   */
  exportConfig() {
    const config = {
      enabled: this.isMockEnabled,
      timestamp: new Date().toISOString(),
      version: '1.0.0'
    }
    return JSON.stringify(config, null, 2)
  }

  /**
   * 导入模拟数据配置
   */
  importConfig(configJson) {
    try {
      const config = JSON.parse(configJson)
      if (config.enabled !== undefined) {
        this.isMockEnabled = config.enabled
      }
      console.log('📥 模拟数据配置已导入')
      return true
    } catch (error) {
      console.error('❌ 导入配置失败:', error)
      return false
    }
  }
}

// 创建全局实例
export const mockDataManager = new MockDataManager()

// 开发环境下的全局控制命令
define global = globalThis
if (import.meta.env.DEV) {
  // 在浏览器控制台中可以使用的命令：
  // window.mockData.enable() - 启用模拟数据
  // window.mockData.disable() - 禁用模拟数据  
  // window.mockData.clear() - 清除所有模拟数据
  // window.mockData.status() - 查看状态
  window.mockData = {
    enable: () => mockDataManager.enable(),
    disable: () => mockDataManager.disable(),
    clear: () => mockDataManager.clearAll(),
    status: () => console.table(mockDataManager.getStatus()),
    export: () => console.log(mockDataManager.exportConfig()),
    import: (config) => mockDataManager.importConfig(config)
  }
  
  console.log('🎭 模拟数据管理器已加载！在控制台中使用 window.mockData 进行管理')
}