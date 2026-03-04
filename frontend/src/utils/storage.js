/**
 * 本地存储工具类
 * 封装 localStorage 和 sessionStorage，提供类型安全的API
 */

/**
 * 存储类型枚举
 */
export const StorageType = {
  LOCAL: 'localStorage',
  SESSION: 'sessionStorage'
};

/**
 * 获取存储对象
 * @param {string} type - 存储类型
 * @returns {Storage} 存储对象
 */
function getStorage(type) {
  if (typeof window === 'undefined') {
    return null;
  }
  
  return type === StorageType.LOCAL 
    ? window.localStorage 
    : window.sessionStorage;
}

/**
 * 设置存储项
 * @param {string} key - 键名
 * @param {any} value - 值
 * @param {Object} options - 选项
 * @param {string} options.type - 存储类型，默认为 localStorage
 * @param {number} options.expire - 过期时间（毫秒）
 */
export function setItem(key, value, options = {}) {
  try {
    const { type = StorageType.LOCAL, expire } = options;
    const storage = getStorage(type);
    
    if (!storage) return false;
    
    const item = {
      value,
      timestamp: Date.now(),
      expire: expire ? Date.now() + expire : null
    };
    
    storage.setItem(key, JSON.stringify(item));
    return true;
  } catch (error) {
    console.error('Storage setItem error:', error);
    return false;
  }
}

/**
 * 获取存储项
 * @param {string} key - 键名
 * @param {string} type - 存储类型，默认为 localStorage
 * @returns {any} 存储的值
 */
export function getItem(key, type = StorageType.LOCAL) {
  try {
    const storage = getStorage(type);
    if (!storage) return null;
    
    const itemStr = storage.getItem(key);
    if (!itemStr) return null;
    
    const item = JSON.parse(itemStr);
    
    // 检查是否过期
    if (item.expire && Date.now() > item.expire) {
      storage.removeItem(key);
      return null;
    }
    
    return item.value;
  } catch (error) {
    console.error('Storage getItem error:', error);
    return null;
  }
}

/**
 * 删除存储项
 * @param {string} key - 键名
 * @param {string} type - 存储类型
 */
export function removeItem(key, type = StorageType.LOCAL) {
  try {
    const storage = getStorage(type);
    if (!storage) return;
    
    storage.removeItem(key);
  } catch (error) {
    console.error('Storage removeItem error:', error);
  }
}

/**
 * 清空存储
 * @param {string} type - 存储类型
 */
export function clear(type = StorageType.LOCAL) {
  try {
    const storage = getStorage(type);
    if (!storage) return;
    
    storage.clear();
  } catch (error) {
    console.error('Storage clear error:', error);
  }
}

/**
 * 获取所有键名
 * @param {string} type - 存储类型
 * @returns {string[]} 键名数组
 */
export function keys(type = StorageType.LOCAL) {
  try {
    const storage = getStorage(type);
    if (!storage) return [];
    
    return Object.keys(storage);
  } catch (error) {
    console.error('Storage keys error:', error);
    return [];
  }
}

/**
 * 获取存储大小（字节）
 * @param {string} type - 存储类型
 * @returns {number} 存储大小
 */
export function size(type = StorageType.LOCAL) {
  try {
    const storage = getStorage(type);
    if (!storage) return 0;
    
    let total = 0;
    for (let i = 0; i < storage.length; i++) {
      const key = storage.key(i);
      const value = storage.getItem(key);
      total += (key.length + value.length) * 2; // 每个字符2字节
    }
    
    return total;
  } catch (error) {
    console.error('Storage size error:', error);
    return 0;
  }
}

/**
 * 检查存储是否可用
 * @returns {boolean} 是否可用
 */
export function isStorageAvailable() {
  try {
    const testKey = '__storage_test__';
    const storage = window.localStorage;
    
    storage.setItem(testKey, 'test');
    storage.removeItem(testKey);
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * 带命名空间的存储
 */
export class NamespacedStorage {
  constructor(namespace, type = StorageType.LOCAL) {
    this.namespace = namespace;
    this.type = type;
  }
  
  getKey(key) {
    return `${this.namespace}:${key}`;
  }
  
  set(key, value, options = {}) {
    return setItem(this.getKey(key), value, { ...options, type: this.type });
  }
  
  get(key) {
    return getItem(this.getKey(key), this.type);
  }
  
  remove(key) {
    return removeItem(this.getKey(key), this.type);
  }
  
  clearAll() {
    const storage = getStorage(this.type);
    if (!storage) return;
    
    const prefix = `${this.namespace}:`;
    for (let i = 0; i < storage.length; i++) {
      const key = storage.key(i);
      if (key.startsWith(prefix)) {
        storage.removeItem(key);
        i--; // 因为删除后数组长度变化
      }
    }
  }
}

export default {
  StorageType,
  setItem,
  getItem,
  removeItem,
  clear,
  keys,
  size,
  isStorageAvailable,
  NamespacedStorage
};