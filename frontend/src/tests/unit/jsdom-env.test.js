// @vitest-environment jsdom
// AI_WORKING: coder1 @2026-01-30 15:05:00 - 测试jsdom环境指令
import { describe, it, expect } from 'vitest'

describe('jsdom环境测试 (使用指令)', () => {
  it('应该有window对象', () => {
    expect(typeof window).toBe('object')
    console.log('window.constructor.name:', window.constructor.name)
  })

  it('应该有document对象', () => {
    expect(typeof document).toBe('object')
    console.log('document.constructor.name:', document.constructor.name)
  })

  it('应该有localStorage', () => {
    expect(typeof localStorage).toBe('object')
  })

  it('应该能够操作DOM', () => {
    const div = document.createElement('div')
    div.id = 'test'
    div.textContent = 'Hello jsdom'
    document.body.appendChild(div)
    
    const found = document.getElementById('test')
    expect(found).toBeTruthy()
    expect(found.textContent).toBe('Hello jsdom')
  })
})