// 本地策略辅助工具 - 临时解决API认证问题
// 用于在API不可用的情况下管理策略列表

const LOCAL_STRATEGIES_KEY = 'beidan_local_strategies'

// 获取本地策略列表
export const getLocalStrategies = () => {
  try {
    const stored = localStorage.getItem(LOCAL_STRATEGIES_KEY)
    return stored ? JSON.parse(stored) : []
  } catch (error) {
    console.error('读取本地策略失败:', error)
    return []
  }
}

// 保存本地策略列表
export const saveLocalStrategies = (strategies) => {
  try {
    localStorage.setItem(LOCAL_STRATEGIES_KEY, JSON.stringify(strategies))
  } catch (error) {
    console.error('保存本地策略失败:', error)
  }
}

// 添加新策略到本地列表
export const addLocalStrategy = (strategyName) => {
  const strategies = getLocalStrategies()
  if (!strategies.includes(strategyName)) {
    strategies.push(strategyName)
    saveLocalStrategies(strategies)
  }
  return strategies
}

// 从本地列表删除策略
export const removeLocalStrategy = (strategyName) => {
  const strategies = getLocalStrategies()
  const filtered = strategies.filter(name => name !== strategyName)
  saveLocalStrategies(filtered)
  return filtered
}