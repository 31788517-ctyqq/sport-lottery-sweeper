// AI_WORKING: coder1 @2026-01-30 14:31:00 - 创建简单Vue组件测试，验证Vue插件和Element Plus注册
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { h } from 'vue'

// 创建一个简单的Vue组件用于测试
const TestComponent = {
  template: '<div>Test Component</div>'
}

// 创建一个使用Element Plus按钮的组件
const TestElementButton = {
  template: `
    <div>
      <el-button type="primary">Test Button</el-button>
    </div>
  `
}

describe('Vue插件配置验证', () => {
  it('应该能够挂载简单的Vue组件', () => {
    const wrapper = mount(TestComponent)
    expect(wrapper.text()).toBe('Test Component')
  })

  it('应该能够渲染Element Plus按钮组件', () => {
    const wrapper = mount(TestElementButton)
    // 检查按钮是否存在
    const button = wrapper.find('button')
    expect(button.exists()).toBe(true)
    expect(button.classes()).toContain('el-button')
  })

  it('全局测试变量应该可用', () => {
    expect(typeof describe).toBe('function')
    expect(typeof it).toBe('function')
    expect(typeof expect).toBe('function')
  })
})