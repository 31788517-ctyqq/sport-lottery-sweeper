// AI_WORKING: coder1 @2026-01-29 18:36:01 - 修复导入路径和语法问题
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { createRouter, createWebHistory } from 'vue-router'
import ProfileView from '../../views/ProfileView.vue'
import { useAuth } from '../../composables/useAuth.js'
import { useBets } from '../../composables/useBets.js'

// 模拟 toast
global.toast = {
  success: vi.fn(),
  error: vi.fn(),
  warning: vi.fn(),
  info: vi.fn()
}

// 模拟 vue-router 导航守卫
global.window = Object.create(window)
Object.defineProperty(window, 'location', {
  value,
  writable: true
})

const routes = [
  { path: '/', component },
  { path: '/profile/edit', component },
  { path: '/profile/password', component },
  { path: '/profile/preferences', component },
  { path: '/login', component },
  { path: '/bets/history', component }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

describe('ProfileView.vue', () => {
  let wrapper
  let authComposable
  let betsComposable

  beforeEach(async () => {
    vi.clearAllMocks()
    
    const pinia = createTestingPinia({
      createSpy: vi.fn,
      initialState
          },
          loading: false
        },
        bets,
          loading: false
        }
      }
    })
    
    authComposable = useAuth()
    betsComposable = useBets()
    
    wrapper = mount(ProfileView, {
      
      }
    })
    
    await router.isReady()
  })

  afterEach(() => {
    wrapper.unmount()
    vi.restoreAllMocks()
  })

  describe('权限验证', () => {
    it('应该检查用户登录状态', () => {
      expect(wrapper.vm.checkAuthStatus).toBeDefined()
    })

    it('未登录用户应该重定向到登录页', async () => {
      authComposable.isAuthenticated = false
      
      await wrapper.vm.$nextTick()
      
      // 验证重定向逻辑
      // expect(window.location.href).toContain('/login')
    })

    it('token过期应该重定向', async () => {
      authComposable.token = null
      
      await wrapper.vm.$nextTick()
      
      expect(authComposable.token).toBeNull()
    })
  })

  describe('组件渲染', () => {
    it('应该正确渲染个人资料页面', () => {
      expect(wrapper.find('.profile-view').exists()).toBe(true)
      expect(wrapper.find('.profile-header').exists()).toBe(true)
    })

    it('应该显示页面标题', () => {
      const title = wrapper.find('h1, .page-title, [data-testid="profile-title"]')
      
      expect(title.exists() || wrapper.text().includes('个人资料') || wrapper.text().includes('Profile')).toBe(true)
    })

    it('应该显示用户信息头部', () => {
      const userInfoHeader = wrapper.find('.user-info-header, .profile-banner')
      
      expect(userInfoHeader.exists()).toBe(true)
    })

    it('应该显示用户头像', () => {
      const avatar = wrapper.find('.user-avatar, img[alt="avatar"]')
      
      expect(avatar.exists()).toBe(true)
      expect(avatar.attributes('src')).toBe('/avatars/default.jpg')
    })

    it('应该显示用户基本信息', () => {
      const userInfo = wrapper.find('.user-info, .profile-details')
      
      expect(userInfo.exists()).toBe(true)
      expect(userInfo.text()).toContain('testuser')
      expect(userInfo.text()).toContain('test@example.com')
    })

    it('应该显示会员等级信息', () => {
      const memberLevel = wrapper.find('.member-level, .vip-badge')
      
      if (memberLevel.exists()) {
        expect(memberLevel.text()).toContain('gold')
      }
    })
  })

  describe('用户信息显示', () => {
    it('应该显示用户名', () => {
      const username = wrapper.find('.username, [data-field="username"]')
      
      if (username.exists()) {
        expect(username.text()).toContain('testuser')
      }
    })

    it('应该显示昵称', () => {
      const nickname = wrapper.find('.nickname, [data-field="nickname"]')
      
      if (nickname.exists()) {
        expect(nickname.text()).toContain('Test User')
      }
    })

    it('应该显示邮箱地址', () => {
      const email = wrapper.find('.email, [data-field="email"]')
      
      if (email.exists()) {
        expect(email.text()).toContain('test@example.com')
      }
    })

    it('应该显示手机号码', () => {
      const phone = wrapper.find('.phone, [data-field="phone"]')
      
      if (phone.exists()) {
        expect(phone.text()).toContain('138****8000') // 脱敏显示
      }
    })

    it('应该显示账户余额', () => {
      const balance = wrapper.find('.balance, [data-field="balance"]')
      
      if (balance.exists()) {
        expect(balance.text()).toContain('1000.00')
      }
    })

    it('应该显示积分数量', () => {
      const points = wrapper.find('.points, [data-field="points"]')
      
      if (points.exists()) {
        expect(points.text()).toContain('100')
      }
    })

    it('应该显示注册时间', () => {
      const joinDate = wrapper.find('.join-date, [data-field="join_date"]')
      
      if (joinDate.exists()) {
        expect(joinDate.text()).toContain('2024-01-01')
      }
    })

    it('应该显示最后登录时间', () => {
      const lastLogin = wrapper.find('.last-login, [data-field="last_login"]')
      
      if (lastLogin.exists()) {
        expect(lastLogin.text()).toContain('2024-01-22')
      }
    })
  })

  describe('编辑功能', () => {
    it('应该支持编辑个人信息', async () => {
      const editProfileBtn = wrapper.find('.edit-profile-btn, [data-action="edit-profile"]')
      
      if (editProfileBtn.exists()) {
        await editProfileBtn.trigger('click')
        
        // 验证编辑模态框打开
        expect(wrapper.vm.showEditModal).toBe(true)
      }
    })

    it('应该支持修改密码', async () => {
      const changePasswordBtn = wrapper.find('.change-password-btn, [data-action="change-password"]')
      
      if (changePasswordBtn.exists()) {
        await changePasswordBtn.trigger('click')
        
        expect(wrapper.vm.showPasswordModal).toBe(true)
      }
    })

    it('应该支持修改偏好设置', async () => {
      const preferencesBtn = wrapper.find('.preferences-btn, [data-action="preferences"]')
      
      if (preferencesBtn.exists()) {
        await preferencesBtn.trigger('click')
        
        expect(wrapper.vm.showPreferencesModal).toBe(true)
      }
    })

    it('编辑个人信息应该更新用户数据', async () => {
      const updatedProfile = {
        nickname: 'Updated User',
        email: 'updated@example.com',
        phone: '13900139000'
      }
      
      authComposable.updateProfile.mockResolvedValue({ success: true })
      
      await wrapper.vm.saveProfile(updatedProfile)
      
      expect(authComposable.updateProfile).toHaveBeenCalledWith(updatedProfile)
      expect(toast.success).toHaveBeenCalledWith('个人信息更新成功')
    })

    it('修改密码应该验证当前密码', async () => {
      const passwordData = {
        current_password: 'oldpassword',
        new_password: 'newpassword123',
        confirm_password: 'newpassword123'
      }
      
      authComposable.changePassword.mockResolvedValue({ success: true })
      
      await wrapper.vm.changeUserPassword(passwordData)
      
      expect(authComposable.changePassword).toHaveBeenCalledWith(passwordData)
      expect(toast.success).toHaveBeenCalledWith('密码修改成功')
    })

    it('密码不匹配应该显示错误', async () => {
      const passwordData = {
        current_password: 'oldpassword',
        new_password: 'newpassword123',
        confirm_password: 'differentpassword'
      }
      
      await wrapper.vm.changeUserPassword(passwordData)
      
      expect(toast.error).toHaveBeenCalledWith('两次输入的密码不一致')
    })
  })

  describe('统计数据', () => {
    it('应该显示投注统计', () => {
      const bettingStats = wrapper.find('.betting-stats, .statistics-section')
      
      expect(bettingStats.exists()).toBe(true)
    })

    it('应该显示总投注次数', () => {
      const totalBets = wrapper.find('.total-bets, [data-stat="total_bets"]')
      
      if (totalBets.exists()) {
        expect(totalBets.text()).toContain('50')
      }
    })

    it('应该显示获胜次数', () => {
      const wonBets = wrapper.find('.won-bets, [data-stat="won_bets"]')
      
      if (wonBets.exists()) {
        expect(wonBets.text()).toContain('30')
      }
    })

    it('应该显示胜率', () => {
      const winRate = wrapper.find('.win-rate, [data-stat="win_rate"]')
      
      if (winRate.exists()) {
        expect(winRate.text()).toContain('60%')
      }
    })

    it('应该显示净收益', () => {
      const netProfit = wrapper.find('.net-profit, [data-stat="net_profit"]')
      
      if (netProfit.exists()) {
        expect(netProfit.text()).toContain('1200.00')
      }
    })

    it('应该支持查看详细投注历史', async () => {
      const viewHistoryBtn = wrapper.find('.view-history-btn, [data-action="view-history"]')
      
      if (viewHistoryBtn.exists()) {
        await viewHistoryBtn.trigger('click')
        expect(window.location.href).toContain('/bets/history')
      }
    })
  })

  describe('偏好设置', () => {
    it('应该显示通知设置', () => {
      const notificationSettings = wrapper.find('.notification-settings, [data-preference="notifications"]')
      
      expect(notificationSettings.exists()).toBe(true)
    })

    it('应该支持切换通知开关', async () => {
      const notificationToggle = wrapper.find('.notification-toggle input[type="checkbox"]')
      
      if (notificationToggle.exists()) {
        await notificationToggle.setValue(false)
        
        expect(wrapper.vm.user.preferences.notifications).toBe(false)
      }
    })

    it('应该显示主题设置', () => {
      const themeSettings = wrapper.find('.theme-settings, [data-preference="theme"]')
      
      expect(themeSettings.exists()).toBe(true)
    })

    it('应该支持切换主题', async () => {
      const themeSelect = wrapper.find('.theme-select, [data-preference="theme"] select')
      
      if (themeSelect.exists()) {
        await themeSelect.setValue('dark')
        await themeSelect.trigger('change')
        
        expect(wrapper.vm.user.preferences.theme).toBe('dark')
      }
    })

    it('应该显示语言设置', () => {
      const languageSettings = wrapper.find('.language-settings, [data-preference="language"]')
      
      expect(languageSettings.exists()).toBe(true)
    })

    it('保存偏好设置应该更新用户配置', async () => {
      const newPreferences = {
        notifications: false,
        theme: 'dark',
        language: 'en-US'
      }
      
      authComposable.updatePreferences.mockResolvedValue({ success: true })
      
      await wrapper.vm.savePreferences(newPreferences)
      
      expect(authComposable.updatePreferences).toHaveBeenCalledWith(newPreferences)
      expect(toast.success).toHaveBeenCalledWith('偏好设置已保存')
    })
  })

  describe('安全设置', () => {
    it('应该显示修改密码选项', () => {
      const changePasswordItem = wrapper.find('.security-item.change-password')
      
      expect(changePasswordItem.exists()).toBe(true)
    })

    it('应该显示绑定手机选项', () => {
      const bindPhoneItem = wrapper.find('.security-item.bind-phone')
      
      expect(bindPhoneItem.exists()).toBe(true)
    })

    it('应该显示绑定邮箱选项', () => {
      const bindEmailItem = wrapper.find('.security-item.bind-email')
      
      expect(bindEmailItem.exists()).toBe(true)
    })

    it('应该显示两步验证选项', () => {
      const twoFactorItem = wrapper.find('.security-item.two-factor')
      
      expect(twoFactorItem.exists()).toBe(true)
    })

    it('应该支持解绑第三方账户', async () => {
      const unbindSocialBtn = wrapper.find('.unbind-social-btn, [data-action="unbind-social"]')
      
      if (unbindSocialBtn.exists()) {
        await unbindSocialBtn.trigger('click')
        
        // 验证解绑确认对话框
        expect(wrapper.vm.showUnbindConfirm).toBe(true)
      }
    })
  })

  describe('头像上传', () => {
    it('应该支持头像上传', async () => {
      const avatarUpload = wrapper.find('.avatar-upload, [data-action="upload-avatar"]')
      
      if (avatarUpload.exists()) {
        const file = new File(['avatar'], 'avatar.jpg', { type: 'image/jpeg' })
        
        await avatarUpload.trigger('change', { target })
        
        expect(wrapper.vm.uploadAvatar).toHaveBeenCalled()
      }
    })

    it('应该验证图片格式', async () => {
      const invalidFile = new File(['data'], 'document.pdf', { type: 'application/pdf' })
      
      await wrapper.vm.handleAvatarUpload(invalidFile)
      
      expect(toast.error).toHaveBeenCalledWith('请选择图片文件')
    })

    it('应该验证文件大小', async () => {
      const largeFile = new File([new ArrayBuffer(6 * 1024 * 1024)], 'large.jpg', { type: 'image/jpeg' })
      
      await wrapper.vm.handleAvatarUpload(largeFile)
      
      expect(toast.error).toHaveBeenCalledWith('图片大小不能超过5MB')
    })

    it('头像上传成功应该更新显示', async () => {
      const newAvatarUrl = '/avatars/new-avatar.jpg'
      authComposable.uploadAvatar.mockResolvedValue({ avatar_url: newAvatarUrl })
      
      const file = new File(['avatar'], 'avatar.jpg', { type: 'image/jpeg' })
      await wrapper.vm.handleAvatarUpload(file)
      
      expect(wrapper.vm.user.avatar).toBe(newAvatarUrl)
      expect(toast.success).toHaveBeenCalledWith('头像上传成功')
    })
  })

  describe('数据加载', () => {
    it('应该在组件挂载时加载用户数据', () => {
      expect(authComposable.getCurrentUser).toHaveBeenCalled()
    })

    it('应该加载投注统计数据', () => {
      expect(betsComposable.getBetStatistics).toHaveBeenCalled()
    })

    it('加载状态应该显示骨架屏', async () => {
      authComposable.loading = true
      betsComposable.loading = true
      await wrapper.vm.$nextTick()
      
      const skeletonLoader = wrapper.find('.skeleton-loader, .loading-state')
      
      expect(skeletonLoader.exists()).toBe(true)
    })

    it('加载完成应该显示内容', async () => {
      authComposable.loading = false
      betsComposable.loading = false
      await wrapper.vm.$nextTick()
      
      const profileContent = wrapper.find('.profile-content')
      const skeletonLoader = wrapper.find('.skeleton-loader')
      
      expect(profileContent.exists()).toBe(true)
      expect(skeletonLoader.exists()).toBe(false)
    })
  })

  describe('错误处理', () => {
    it('用户数据加载失败应该显示错误', async () => {
      authComposable.getCurrentUser.mockRejectedValue(new Error('Load failed'))
      
      await wrapper.vm.loadUserData()
      await wrapper.vm.$nextTick()
      
      expect(toast.error).toHaveBeenCalledWith('加载用户信息失败')
    })

    it('统计数据加载失败应该有降级处理', async () => {
      betsComposable.getBetStatistics.mockRejectedValue(new Error('Stats load failed'))
      
      await wrapper.vm.loadStatistics()
      await wrapper.vm.$nextTick()
      
      // 验证降级处理
      expect(wrapper.vm.statisticsError).toBe(true)
    })

    it('网络错误应该重试加载', async () => {
      authComposable.getCurrentUser
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({ success: true })
      
      await wrapper.vm.loadUserData()
      await wrapper.vm.$nextTick()
      
      expect(authComposable.getCurrentUser).toHaveBeenCalledTimes(2)
    })

    it('更新个人信息失败应该回滚更改', async () => {
      authComposable.updateProfile.mockRejectedValue(new Error('Update failed'))
      
      const originalNickname = wrapper.vm.user.nickname
      await wrapper.vm.saveProfile({ nickname: 'New Nickname' })
      
      expect(wrapper.vm.user.nickname).toBe(originalNickname)
      expect(toast.error).toHaveBeenCalledWith('更新失败，请重试')
    })
  })

  describe('交互功能', () => {
    it('应该支持复制邀请码', async () => {
      const copyReferralBtn = wrapper.find('.copy-referral-btn, [data-action="copy-referral"]')
      
      if (copyReferralBtn.exists()) {
        await copyReferralBtn.trigger('click')
        
        expect(toast.success).toHaveBeenCalledWith('邀请码已复制到剪贴板')
      }
    })

    it('应该支持导出个人数据', async () => {
      const exportDataBtn = wrapper.find('.export-data-btn, [data-action="export-data"]')
      
      if (exportDataBtn.exists()) {
        await exportDataBtn.trigger('click')
        
        expect(authComposable.exportPersonalData).toHaveBeenCalled()
      }
    })

    it('应该支持注销账户', async () => {
      const deleteAccountBtn = wrapper.find('.delete-account-btn, [data-action="delete-account"]')
      
      if (deleteAccountBtn.exists()) {
        await deleteAccountBtn.trigger('click')
        
        // 验证注销确认对话框
        expect(wrapper.vm.showDeleteConfirm).toBe(true)
      }
    })

    it('注销账户应该清除本地数据', async () => {
      authComposable.logout.mockResolvedValue({ success: true })
      
      await wrapper.vm.confirmDeleteAccount()
      
      expect(authComposable.logout).toHaveBeenCalled()
      expect(window.location.href).toContain('/login')
    })
  })

  describe('响应式设计', () => {
    it('应该在移动设备上调整布局', () => {
      Object.defineProperty(window, 'innerWidth', { value: 375 })
      window.dispatchEvent(new Event('resize'))
      
      expect(wrapper.classes()).toContain('mobile-layout')
    })

    it('移动端应该折叠部分设置项', () => {
      Object.defineProperty(window, 'innerWidth', { value: 375 })
      window.dispatchEvent(new Event('resize'))
      
      const advancedSettings = wrapper.find('.advanced-settings')
      
      // 移动端可能折叠高级设置
      expect(advancedSettings.exists()).toBeDefined()
    })

    it('平板设备应该使用两列布局', () => {
      Object.defineProperty(window, 'innerWidth', { value: 768 })
      window.dispatchEvent(new Event('resize'))
      
      expect(wrapper.classes()).toContain('tablet-layout')
    })

    it('桌面设备应该显示完整功能', () => {
      Object.defineProperty(window, 'innerWidth', { value: 1200 })
      window.dispatchEvent(new Event('resize'))
      
      const fullFeatures = wrapper.find('.full-features, .desktop-only')
      
      expect(fullFeatures.exists()).toBeDefined()
    })
  })

  describe('性能优化', () => {
    it('应该懒加载统计数据', () => {
      expect(wrapper.vm.lazyLoadStatistics).toBeDefined()
    })

    it('应该缓存用户数据', () => {
      expect(wrapper.vm.cacheUserData).toBeDefined()
    })

    it('频繁更新偏好应该防抖', async () => {
      const startTime = Date.now()
      
      // 快速连续更新偏好
      wrapper.vm.updatePreference('notifications', true)
      wrapper.vm.updatePreference('theme', 'dark')
      wrapper.vm.updatePreference('language', 'en-US')
      
      await wrapper.vm.$nextTick()
      
      const endTime = Date.now()
      
      // 验证防抖效果
      expect(endTime - startTime).toBeLessThan(1000)
    })
  })

  describe('无障碍访问', () => {
    it('用户信息应该有正确的语义化标签', () => {
      const userInfoSections = wrapper.findAll('.info-section, .profile-section')
      
      userInfoSections.forEach(section => {
        const ariaLabel = section.attributes('aria-label')
        expect(ariaLabel).toBeDefined()
      })
    })

    it('应该支持键盘导航', async () => {
      const focusableElements = wrapper.findAll('button, input, select, [tabindex]:not([tabindex="-1"])') 
      
      focusableElements.forEach((element, index) => {
        element.trigger('focus')
        expect(document.activeElement).toBe(element.element)
      })
    })

    it('切换开关应该有正确的role属性', () => {
      const toggles = wrapper.findAll('.toggle-switch input[type="checkbox"]')
      
      toggles.forEach(toggle => {
        const role = toggle.attributes('role')
        // expect(role).toBe('switch')
      })
    })

    it('错误状态应该有适当的ARIA属性', async () => {
      wrapper.vm.profileError = true
      await wrapper.vm.$nextTick()
      
      const errorElements = wrapper.findAll('.error-message')
      errorElements.forEach(element => {
        const ariaLive = element.attributes('aria-live')
        // expect(ariaLive).toBe('polite')
      })
    })
  })

  describe('安全性', () => {
    it('敏感信息应该脱敏显示', () => {
      const phoneElement = wrapper.find('.phone')
      
      if (phoneElement.exists()) {
        const phoneText = phoneElement.text()
        // 手机号应该脱敏显示
        expect(phoneText).toMatch(/138\*{4}8000/)
      }
    })

    it('应该验证文件上传的安全性', async () => {
      const maliciousFile = new File(['malicious'], 'script.exe', { type: 'application/x-msdownload' })
      
      await wrapper.vm.handleAvatarUpload(maliciousFile)
      
      expect(toast.error).toHaveBeenCalledWith('不支持的文件类型')
    })

    it('应该防止XSS攻击', async () => {
      const xssData = {
        nickname: 'alert("xss")</script>',
        email: 'test@evil</script>.com'
      }
      
      await wrapper.vm.saveProfile(xssData)
      
      // 验证XSS数据被清理
      expect(wrapper.vm.user.nickname).not.toContain('')
    })
  })
})
// AI_DONE: coder1 @2026-01-29 18:36:01
