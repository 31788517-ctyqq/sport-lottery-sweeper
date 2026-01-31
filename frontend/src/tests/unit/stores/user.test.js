// AI_WORKING: coder1 @2026-01-29 18:36:01 - 修复导入路径和语法问题
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '../../stores/user'

// Mock localStorage
global.localStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}

// Mock window.location
global.window = Object.create(window)
Object.defineProperty(window, 'location', {
  value,
  writable: true
})

describe('useUserStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    localStorage.getItem.mockClear()
    localStorage.setItem.mockClear()
    localStorage.removeItem.mockClear()
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('state initialization', () => {
    it('should initialize with default state', () => {
      const store = useUserStore()
      
      expect(store.user).toBeNull()
      expect(store.token).toBeNull()
      expect(store.refreshToken).toBeNull()
      expect(store.permissions).toEqual([])
      expect(store.roles).toEqual([])
      expect(store.isLoggedIn).toBe(false)
      expect(store.loading).toBe(false)
    })

    it('should load state from localStorage if available', () => {
      const mockUser = { id: 1, username: 'testuser' }
      const mockToken = 'test-token'
      const mockRefreshToken = 'refresh-token'
      const mockPermissions = ['user.view']
      const mockRoles = ['user']
      
      localStorage.getItem
        .mockReturnValueOnce(JSON.stringify(mockUser))
        .mockReturnValueOnce(mockToken)
        .mockReturnValueOnce(mockRefreshToken)
        .mockReturnValueOnce(JSON.stringify(mockPermissions))
        .mockReturnValueOnce(JSON.stringify(mockRoles))
      
      const store = useUserStore()
      
      expect(store.user).toEqual(mockUser)
      expect(store.token).toBe(mockToken)
      expect(store.refreshToken).toBe(mockRefreshToken)
      expect(store.permissions).toEqual(mockPermissions)
      expect(store.roles).toEqual(mockRoles)
      expect(store.isLoggedIn).toBe(true)
    })
  })

  describe('getters', () => {
    let store
    
    beforeEach(() => {
      store = useUserStore()
    })

    it('should compute isSuperAdmin correctly', () => {
      store.roles = []
      expect(store.isSuperAdmin).toBe(false)

      store.roles = ['user']
      expect(store.isSuperAdmin).toBe(false)

      store.roles = ['super_admin']
      expect(store.isSuperAdmin).toBe(true)

      store.roles = ['user', 'super_admin']
      expect(store.isSuperAdmin).toBe(true)
    })

    it('should compute isAdmin correctly', () => {
      store.roles = []
      expect(store.isAdmin).toBe(false)

      store.roles = ['user']
      expect(store.isAdmin).toBe(false)

      store.roles = ['admin']
      expect(store.isAdmin).toBe(true)

      store.roles = ['super_admin']
      expect(store.isAdmin).toBe(true)

      store.roles = ['user', 'admin']
      expect(store.isAdmin).toBe(true)
    })

    it('should compute userInfo computed property', () => {
      store.user = null
      expect(store.userInfo).toBeNull()

      const mockUser = { id: 1, username: 'testuser', nickname: 'Test User' }
      store.user = mockUser
      expect(store.userInfo).toEqual(mockUser)
    })
  })

  describe('actions', () => {
    let store
    
    beforeEach(() => {
      store = useUserStore()
    })

    describe('login', () => {
      it('should set user data and tokens on successful login', async () => {
        const mockResponse = {
          token: 'test-token',
          refresh_token: 'refresh-token',
          user,
          permissions: ['user.view', 'user.edit'],
          roles: ['user']
        }
        
        // Mock API call
        vi.doMock('../../api/auth', () => ({
          login: vi.fn().mockResolvedValue(mockResponse)
        }))
        
        await store.login({ username: 'testuser', password: 'password' })
        
        expect(store.token).toBe(mockResponse.token)
        expect(store.refreshToken).toBe(mockResponse.refresh_token)
        expect(store.user).toEqual(mockResponse.user)
        expect(store.permissions).toEqual(mockResponse.permissions)
        expect(store.roles).toEqual(mockResponse.roles)
        expect(store.isLoggedIn).toBe(true)
        
        expect(localStorage.setItem).toHaveBeenCalledWith('token', mockResponse.token)
        expect(localStorage.setItem).toHaveBeenCalledWith('refreshToken', mockResponse.refresh_token)
        expect(localStorage.setItem).toHaveBeenCalledWith('user', JSON.stringify(mockResponse.user))
        expect(localStorage.setItem).toHaveBeenCalledWith('permissions', JSON.stringify(mockResponse.permissions))
        expect(localStorage.setItem).toHaveBeenCalledWith('roles', JSON.stringify(mockResponse.roles))
      })

      it('should handle login failure', async () => {
        const mockError = new Error('Login failed')
        
        vi.doMock('../../api/auth', () => ({
          login: vi.fn().mockRejectedValue(mockError)
        }))
        
        await expect(store.login({ username: 'testuser', password: 'wrong' }))
          .rejects.toThrow('Login failed')
        
        expect(store.isLoggedIn).toBe(false)
        expect(store.token).toBeNull()
      })
    })

    describe('logout', () => {
      it('should clear user data and tokens', () => {
        // Setup initial state
        store.token = 'test-token'
        store.refreshToken = 'refresh-token'
        store.user = { id: 1, username: 'testuser' }
        store.permissions = ['user.view']
        store.roles = ['user']
        store.isLoggedIn = true
        
        store.logout()
        
        expect(store.token).toBeNull()
        expect(store.refreshToken).toBeNull()
        expect(store.user).toBeNull()
        expect(store.permissions).toEqual([])
        expect(store.roles).toEqual([])
        expect(store.isLoggedIn).toBe(false)
        
        expect(localStorage.removeItem).toHaveBeenCalledWith('token')
        expect(localStorage.removeItem).toHaveBeenCalledWith('refreshToken')
        expect(localStorage.removeItem).toHaveBeenCalledWith('user')
        expect(localStorage.removeItem).toHaveBeenCalledWith('permissions')
        expect(localStorage.removeItem).toHaveBeenCalledWith('roles')
        
        expect(window.location.href).toBe('/login')
      })
    })

    describe('updateProfile', () => {
      it('should update user profile', async () => {
        const mockUser = { id: 1, username: 'testuser' }
        store.user = mockUser
        
        const updateData = { nickname: 'Updated Name', email: 'new@example.com' }
        const mockResponse = { ...mockUser, ...updateData }
        
        vi.doMock('../../api/auth', () => ({
          updateProfile: vi.fn().mockResolvedValue(mockResponse)
        }))
        
        await store.updateProfile(updateData)
        
        expect(store.user).toEqual(mockResponse)
        expect(localStorage.setItem).toHaveBeenCalledWith('user', JSON.stringify(mockResponse))
      })
    })

    describe('changePassword', () => {
      it('should change password successfully', async () => {
        vi.doMock('../../api/auth', () => ({
          changePassword: vi.fn().mockResolvedValue({ success: true })
        }))
        
        const result = await store.changePassword('oldpass', 'newpass')
        
        expect(result.success).toBe(true)
      })

      it('should handle password change failure', async () => {
        const mockError = new Error('Password change failed')
        
        vi.doMock('../../api/auth', () => ({
          changePassword: vi.fn().mockRejectedValue(mockError)
        }))
        
        await expect(store.changePassword('oldpass', 'newpass'))
          .rejects.toThrow('Password change failed')
      })
    })

    describe('refreshToken', () => {
      it('should refresh token successfully', async () => {
        store.token = 'old-token'
        store.refreshToken = 'old-refresh-token'
        
        const mockResponse = {
          token: 'new-token',
          refresh_token: 'new-refresh-token'
        }
        
        vi.doMock('../../api/auth', () => ({
          refreshToken: vi.fn().mockResolvedValue(mockResponse)
        }))
        
        await store.refreshTokenAction()
        
        expect(store.token).toBe(mockResponse.token)
        expect(store.refreshToken).toBe(mockResponse.refresh_token)
        
        expect(localStorage.setItem).toHaveBeenCalledWith('token', mockResponse.token)
        expect(localStorage.setItem).toHaveBeenCalledWith('refreshToken', mockResponse.refresh_token)
      })

      it('should logout on refresh token failure', async () => {
        store.token = 'old-token'
        store.refreshToken = 'old-refresh-token'
        
        const mockError = new Error('Refresh failed')
        
        vi.doMock('../../api/auth', () => ({
          refreshToken: vi.fn().mockRejectedValue(mockError)
        }))
        
        await expect(store.refreshTokenAction()).rejects.toThrow('Refresh failed')
        
        expect(store.token).toBeNull()
        expect(store.isLoggedIn).toBe(false)
      })
    })

    describe('checkPermission', () => {
      it('should return true for super admin', () => {
        store.roles = ['super_admin']
        
        expect(store.checkPermission('any.permission')).toBe(true)
        expect(store.checkPermission(['perm1', 'perm2'])).toBe(true)
      })

      it('should return false for non-logged in user', () => {
        store.isLoggedIn = false
        
        expect(store.checkPermission('user.view')).toBe(false)
      })

      it('should check single permission correctly', () => {
        store.permissions = ['user.view', 'admin.users.view']
        store.isLoggedIn = true
        
        expect(store.checkPermission('user.view')).toBe(true)
        expect(store.checkPermission('user.delete')).toBe(false)
      })

      it('should check multiple permissions with requireAll option', () => {
        store.permissions = ['user.view', 'admin.users.view']
        store.isLoggedIn = true
        
        expect(store.checkPermission(['user.view', 'admin.users.view'], { requireAll: true })).toBe(true)
        expect(store.checkPermission(['user.view', 'user.delete'], { requireAll: true })).toBe(false)
        expect(store.checkPermission(['user.view', 'user.delete'], { requireAll: false })).toBe(true)
      })
    })

    describe('checkRole', () => {
      it('should return true for super admin', () => {
        store.roles = ['super_admin']
        
        expect(store.checkRole('any.role')).toBe(true)
        expect(store.checkRole(['role1', 'role2'])).toBe(true)
      })

      it('should return false for non-logged in user', () => {
        store.isLoggedIn = false
        
        expect(store.checkRole('user')).toBe(false)
      })

      it('should check single role correctly', () => {
        store.roles = ['user']
        store.isLoggedIn = true
        
        expect(store.checkRole('user')).toBe(true)
        expect(store.checkRole('admin')).toBe(false)
      })

      it('should check multiple roles with requireAll option', () => {
        store.roles = ['user', 'admin']
        store.isLoggedIn = true
        
        expect(store.checkRole(['user', 'admin'], { requireAll: true })).toBe(true)
        expect(store.checkRole(['user', 'super_admin'], { requireAll: true })).toBe(false)
        expect(store.checkRole(['user', 'super_admin'], { requireAll: false })).toBe(true)
      })
    })

    describe('initializeFromStorage', () => {
      it('should initialize state from localStorage', () => {
        const mockUser = { id: 1, username: 'testuser' }
        const mockToken = 'test-token'
        const mockRefreshToken = 'refresh-token'
        const mockPermissions = ['user.view']
        const mockRoles = ['user']
        
        localStorage.getItem
          .mockReturnValueOnce(JSON.stringify(mockUser))
          .mockReturnValueOnce(mockToken)
          .mockReturnValueOnce(mockRefreshToken)
          .mockReturnValueOnce(JSON.stringify(mockPermissions))
          .mockReturnValueOnce(JSON.stringify(mockRoles))
        
        store.initializeFromStorage()
        
        expect(store.user).toEqual(mockUser)
        expect(store.token).toBe(mockToken)
        expect(store.refreshToken).toBe(mockRefreshToken)
        expect(store.permissions).toEqual(mockPermissions)
        expect(store.roles).toEqual(mockRoles)
        expect(store.isLoggedIn).toBe(true)
      })

      it('should handle missing localStorage data', () => {
        localStorage.getItem.mockReturnValue(null)
        
        store.initializeFromStorage()
        
        expect(store.user).toBeNull()
        expect(store.token).toBeNull()
        expect(store.isLoggedIn).toBe(false)
      })
    })

    describe('setLoading', () => {
      it('should set loading state', () => {
        store.setLoading(true)
        expect(store.loading).toBe(true)

        store.setLoading(false)
        expect(store.loading).toBe(false)
      })
    })
  })
})
// AI_DONE: coder1 @2026-01-29 18:36:01
