// frontend/tests/unit/utils/authUtils.test.js
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { 
  validateEmail, 
  validatePassword, 
  calculatePasswordStrength, 
  generateCaptchaText, 
  validateCaptcha, 
  setAuthToken, 
  getAuthToken, 
  removeAuthToken, 
  isTokenExpired, 
  getUserInfo, 
  setUserInfo, 
  removeUserInfo,
  formatLastLoginTime,
  debounce,
  throttle,
  deepClone
} from '@/utils/authUtils'

describe('authUtils', () => {
  beforeEach(() => {
    // 清理所有存储
    localStorage.clear()
    sessionStorage.clear()
    vi.clearAllMocks()
  })

  afterEach(() => {
    localStorage.clear()
    sessionStorage.clear()
  })

  describe('邮箱验证', () => {
    it('应该验证有效的邮箱地址', () => {
      const validEmails = [
        'test@example.com',
        'user.name@domain.co.uk',
        'test123@gmail.com',
        'admin@company.org'
      ]

      validEmails.forEach(email => {
        expect(validateEmail(email)).toBe(true)
      })
    })

    it('应该拒绝无效的邮箱地址', () => {
      const invalidEmails = [
        '',
        'invalid-email',
        '@domain.com',
        'user@',
        'user@@domain.com',
        null,
        undefined
      ]

      invalidEmails.forEach(email => {
        expect(validateEmail(email)).toBe(false)
      })
    })
  })

  describe('密码验证', () => {
    it('应该验证有效密码', () => {
      const validPasswords = [
        'MySecureP@ssw0rd123!',
        'Complex#Pass2024$Word',
        'Str0ng&Prec1se#Pass',
        'Aa123456!@#'
      ]

      validPasswords.forEach(password => {
        const result = validatePassword(password)
        expect(result.isValid).toBe(true)
        expect(result.errors.length).toBe(0)
      })
    })

    it('应该拒绝无效密码', () => {
      const invalidPasswords = [
        { password: '', expectedErrors: ['密码长度至少8位'] },
        { password: 'short', expectedErrors: ['密码长度至少8位'] },
        { password: 'nouppercase123!', expectedErrors: ['密码必须包含至少一个大写字母'] },
        { password: 'NOLOWERCASE123!', expectedErrors: ['密码必须包含至少一个小写字母'] },
        { password: 'NoNumbers!', expectedErrors: ['密码必须包含至少两个数字'] },
        { password: 'NoSpecial123', expectedErrors: ['密码必须包含至少一个特殊字符'] },
        { password: 'Aa1!', expectedErrors: ['密码长度至少8位', '密码必须包含至少两个数字'] }
      ]

      invalidPasswords.forEach(({ password, expectedErrors }) => {
        const result = validatePassword(password)
        expect(result.isValid).toBe(false)
        expectedErrors.forEach(error => {
          expect(result.errors.some(e => e.includes(error))).toBe(true)
        })
      })
    })
  })

  describe('密码强度计算', () => {
    it('应该正确计算密码强度', () => {
      const testCases = [
        { password: '12345', expectedScore: 1, expectedLevel: '很弱' },
        { password: 'abcdef', expectedScore: 1, expectedLevel: '很弱' },
        { password: 'Abcdef1', expectedScore: 3, expectedLevel: '一般' },
        { password: 'Abcdefg1!', expectedScore: 4, expectedLevel: '强' },
        { password: 'MySecureP@ssw0rd123!', expectedScore: 5, expectedLevel: '很强' }
      ]

      testCases.forEach(({ password, expectedScore, expectedLevel }) => {
        const result = calculatePasswordStrength(password)
        expect(result.score).toBe(expectedScore)
        expect(result.level).toBe(expectedLevel)
      })
    })

    it('应该返回正确的颜色类名', () => {
      expect(calculatePasswordStrength('12345').colorClass).toBe('bg-red-500')
      expect(calculatePasswordStrength('Abcdefg1!').colorClass).toBe('bg-green-500')
    })
  })

  describe('验证码生成和验证', () => {
    it('应该生成指定长度的验证码', () => {
      const captcha = generateCaptchaText(4)
      expect(captcha).toHaveLength(4)
      expect(/^[A-Z0-9]+$/.test(captcha)).toBe(true)

      const captcha6 = generateCaptchaText(6)
      expect(captcha6).toHaveLength(6)
    })

    it('应该验证正确的验证码', () => {
      const captcha = 'ABCD123'
      expect(validateCaptcha('ABCD123', captcha)).toBe(true)
      expect(validateCaptcha('abcd123', captcha)).toBe(true) // 大小写不敏感
    })

    it('应该拒绝错误的验证码', () => {
      const captcha = 'ABCD123'
      expect(validateCaptcha('WRONG', captcha)).toBe(false)
      expect(validateCaptcha('', captcha)).toBe(false)
      expect(validateCaptcha(null, captcha)).toBe(false)
    })
  })

  describe('Token管理', () => {
    it('应该正确设置和获取token', () => {
      const token = 'test-jwt-token'
      setAuthToken(token)
      expect(getAuthToken()).toBe(token)
    })

    it('应该使用sessionStorage当rememberMe为false', () => {
      const token = 'session-token'
      setAuthToken(token, false)
      expect(sessionStorage.getItem('auth_token')).toBe(token)
      expect(localStorage.getItem('auth_token')).toBeNull()
    })

    it('应该使用localStorage当rememberMe为true', () => {
      const token = 'persistent-token'
      setAuthToken(token, true)
      expect(localStorage.getItem('auth_token')).toBe(token)
      expect(sessionStorage.getItem('auth_token')).toBeNull()
    })

    it('应该移除token', () => {
      setAuthToken('test-token', true)
      removeAuthToken()
      expect(getAuthToken()).toBeNull()
    })

    it('应该检测token过期', () => {
      const expiredPayload = { exp: Math.floor(Date.now() / 1000) - 3600 } // 1小时前过期
      const expiredToken = `header.${btoa(JSON.stringify(expiredPayload))}.signature`
      
      expect(isTokenExpired(expiredToken)).toBe(true)

      const validPayload = { exp: Math.floor(Date.now() / 1000) + 3600 } // 1小时后过期
      const validToken = `header.${btoa(JSON.stringify(validPayload))}.signature`
      
      expect(isTokenExpired(validToken)).toBe(false)
    })

    it('应该处理无效的token格式', () => {
      expect(isTokenExpired('invalid-token')).toBe(true)
      expect(isTokenExpired('')).toBe(true)
    })
  })

  describe('用户信息管理', () => {
    it('应该设置和获取用户信息', () => {
      const userInfo = {
        id: 1,
        email: 'test@example.com',
        role: 'user',
        nickname: 'Test User'
      }

      setUserInfo(userInfo)
      const retrieved = getUserInfo()
      
      expect(retrieved).toEqual(userInfo)
    })

    it('应该移除用户信息', () => {
      setUserInfo({ id: 1, email: 'test@example.com' })
      removeUserInfo()
      expect(getUserInfo()).toBeNull()
    })

    it('应该返回null当没有用户信息时', () => {
      expect(getUserInfo()).toBeNull()
    })
  })

  describe('时间格式化', () => {
    it('应该正确格式化时间', () => {
      const testDate = new Date('2024-01-15T10:30:00Z')
      
      // 由于时区问题，我们只测试返回的字符串不为空且包含基本格式
      const formatted = formatLastLoginTime(testDate.toISOString())
      expect(formatted).toBeTruthy()
      expect(typeof formatted).toBe('string')
    })

    it('应该处理相对时间', () => {
      const now = new Date()
      const recentTime = new Date(now.getTime() - 30000).toISOString() // 30秒前
      
      const formatted = formatLastLoginTime(recentTime)
      expect(formatted).toContain('刚刚')
    })

    it('应该处理无效时间', () => {
      expect(formatLastLoginTime('')).toBe('未知时间')
      expect(formatLastLoginTime(null)).toBe('未知时间')
      expect(formatLastLoginTime('invalid-date')).toBe('未知时间')
    })
  })

  describe('防抖函数', () => {
    it('应该延迟执行函数', async () => {
      const mockFn = vi.fn()
      const debouncedFn = debounce(mockFn, 100)

      debouncedFn('test')
      debouncedFn('test') // 第二次调用应该重置计时器
      
      expect(mockFn).not.toHaveBeenCalled()

      await new Promise(resolve => setTimeout(resolve, 150))
      
      expect(mockFn).toHaveBeenCalledTimes(1)
      expect(mockFn).toHaveBeenCalledWith('test')
    })
  })

  describe('节流函数', () => {
    it('应该限制函数执行频率', async () => {
      const mockFn = vi.fn()
      const throttledFn = throttle(mockFn, 100)

      throttledFn('call1')
      throttledFn('call2')
      throttledFn('call3')
      
      expect(mockFn).toHaveBeenCalledTimes(1)
      expect(mockFn).toHaveBeenCalledWith('call1')

      await new Promise(resolve => setTimeout(resolve, 150))
      
      throttledFn('call4')
      expect(mockFn).toHaveBeenCalledTimes(2)
    })
  })

  describe('深拷贝', () => {
    it('应该正确深拷贝对象', () => {
      const original = {
        a: 1,
        b: {
          c: 2,
          d: [3, 4, 5]
        },
        e: 'string'
      }

      const cloned = deepClone(original)
      
      expect(cloned).toEqual(original)
      expect(cloned).not.toBe(original)
      expect(cloned.b).not.toBe(original.b)
      expect(cloned.b.d).not.toBe(original.b.d)
    })

    it('应该处理循环引用', () => {
      const obj = { a: 1 }
      obj.self = obj
      
      // 深拷贝遇到循环引用应该抛出错误或处理 gracefully
      expect(() => deepClone(obj)).not.toThrow()
    })

    it('应该处理null和undefined', () => {
      expect(deepClone(null)).toBeNull()
      expect(deepClone(undefined)).toBeUndefined()
    })
  })

  describe('边界情况和错误处理', () => {
    it('应该处理localStorage不可用的情况', () => {
      // 模拟localStorage不可用
      const originalLocalStorage = window.localStorage
      Object.defineProperty(window, 'localStorage', {
        value: null,
        writable: true
      })

      // 这些操作不应该抛出错误
      expect(() => setAuthToken('test')).not.toThrow()
      expect(() => getAuthToken()).not.toThrow()

      // 恢复localStorage
      window.localStorage = originalLocalStorage
    })

    it('应该处理JSON解析错误', () => {
      // 在localStorage中设置一个无效的JSON字符串
      localStorage.setItem('user_info', 'invalid-json{')
      
      // getUserInfo应该优雅处理错误并返回null
      expect(getUserInfo()).toBeNull()
    })
  })
})