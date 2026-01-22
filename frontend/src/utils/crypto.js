/**
 * 加密解密工具类
 * 注：前端加密主要用于轻度安全需求，敏感数据应在后端加密
 */

/**
 * Base64编码
 * @param {string} str - 要编码的字符串
 * @returns {string} Base64编码结果
 */
export function base64Encode(str) {
  try {
    if (typeof btoa !== 'undefined') {
      return btoa(unescape(encodeURIComponent(str)));
    }
    
    // Node.js环境
    if (typeof Buffer !== 'undefined') {
      return Buffer.from(str, 'utf8').toString('base64');
    }
    
    throw new Error('Base64编码环境不支持');
  } catch (error) {
    console.error('Base64 encode error:', error);
    return '';
  }
}

/**
 * Base64解码
 * @param {string} str - Base64编码的字符串
 * @returns {string} 解码结果
 */
export function base64Decode(str) {
  try {
    if (typeof atob !== 'undefined') {
      return decodeURIComponent(escape(atob(str)));
    }
    
    // Node.js环境
    if (typeof Buffer !== 'undefined') {
      return Buffer.from(str, 'base64').toString('utf8');
    }
    
    throw new Error('Base64解码环境不支持');
  } catch (error) {
    console.error('Base64 decode error:', error);
    return '';
  }
}

/**
 * 简单的XOR加密
 * @param {string} str - 要加密的字符串
 * @param {string} key - 密钥
 * @returns {string} 加密结果（Base64）
 */
export function xorEncrypt(str, key) {
  try {
    let result = '';
    for (let i = 0; i < str.length; i++) {
      const charCode = str.charCodeAt(i) ^ key.charCodeAt(i % key.length);
      result += String.fromCharCode(charCode);
    }
    return base64Encode(result);
  } catch (error) {
    console.error('XOR encrypt error:', error);
    return '';
  }
}

/**
 * XOR解密
 * @param {string} encryptedStr - 加密的字符串（Base64）
 * @param {string} key - 密钥
 * @returns {string} 解密结果
 */
export function xorDecrypt(encryptedStr, key) {
  try {
    const str = base64Decode(encryptedStr);
    let result = '';
    for (let i = 0; i < str.length; i++) {
      const charCode = str.charCodeAt(i) ^ key.charCodeAt(i % key.length);
      result += String.fromCharCode(charCode);
    }
    return result;
  } catch (error) {
    console.error('XOR decrypt error:', error);
    return '';
  }
}

/**
 * 生成简单的哈希（不可逆）
 * @param {string} str - 要哈希的字符串
 * @returns {string} 哈希结果
 */
export function simpleHash(str) {
  let hash = 0;
  if (str.length === 0) return hash.toString();
  
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // 转换为32位整数
  }
  
  return Math.abs(hash).toString(16);
}

/**
 * 生成随机字符串
 * @param {number} length - 字符串长度
 * @returns {string} 随机字符串
 */
export function generateRandomString(length = 16) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  const crypto = window.crypto || window.msCrypto;
  
  if (crypto && crypto.getRandomValues) {
    const values = new Uint32Array(length);
    crypto.getRandomValues(values);
    for (let i = 0; i < length; i++) {
      result += chars[values[i] % chars.length];
    }
  } else {
    // 降级方案
    for (let i = 0; i < length; i++) {
      result += chars[Math.floor(Math.random() * chars.length)];
    }
  }
  
  return result;
}

/**
 * 生成UUID v4
 * @returns {string} UUID
 */
export function generateUUID() {
  try {
    if (typeof crypto !== 'undefined' && crypto.randomUUID) {
      return crypto.randomUUID();
    }
    
    // 兼容方案
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  } catch (error) {
    console.error('Generate UUID error:', error);
    return generateRandomString(32);
  }
}

/**
 * 密码强度检查
 * @param {string} password - 密码
 * @returns {Object} 检查结果
 */
export function checkPasswordStrength(password) {
  const result = {
    score: 0,
    strength: '弱',
    suggestions: []
  };
  
  if (!password) return result;
  
  // 长度检查
  if (password.length >= 8) result.score += 1;
  if (password.length >= 12) result.score += 1;
  
  // 包含小写字母
  if (/[a-z]/.test(password)) result.score += 1;
  
  // 包含大写字母
  if (/[A-Z]/.test(password)) result.score += 1;
  
  // 包含数字
  if (/[0-9]/.test(password)) result.score += 1;
  
  // 包含特殊字符
  if (/[^A-Za-z0-9]/.test(password)) result.score += 1;
  
  // 确定强度级别
  if (result.score <= 2) {
    result.strength = '弱';
    result.suggestions = ['密码至少8位', '建议包含大小写字母和数字'];
  } else if (result.score <= 4) {
    result.strength = '中';
    result.suggestions = ['密码强度中等', '建议添加特殊字符'];
  } else {
    result.strength = '强';
    result.suggestions = ['密码强度足够'];
  }
  
  return result;
}

/**
 * 数据脱敏
 * @param {string} str - 原始字符串
 * @param {Object} options - 选项
 * @returns {string} 脱敏后的字符串
 */
export function maskData(str, options = {}) {
  const { 
    start = 0, 
    end = 4, 
    maskChar = '*',
    keepLength = true 
  } = options;
  
  if (!str || typeof str !== 'string') return str;
  
  const length = str.length;
  
  if (length <= start + end) {
    // 字符串太短，全部脱敏
    return maskChar.repeat(length);
  }
  
  if (keepLength) {
    const visibleStart = str.substring(0, start);
    const visibleEnd = str.substring(length - end);
    const maskLength = length - start - end;
    
    return visibleStart + maskChar.repeat(maskLength) + visibleEnd;
  } else {
    return str.substring(0, start) + maskChar.repeat(3);
  }
}

export default {
  base64Encode,
  base64Decode,
  xorEncrypt,
  xorDecrypt,
  simpleHash,
  generateRandomString,
  generateUUID,
  checkPasswordStrength,
  maskData
};