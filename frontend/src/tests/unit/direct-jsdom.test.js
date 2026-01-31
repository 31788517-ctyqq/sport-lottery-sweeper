// AI_WORKING: coder1 @2026-01-30 15:06:00 - 直接测试jsdom环境
import { describe, it, expect, vi } from 'vitest'
import { JSDOM } from 'jsdom'

// 手动创建jsdom环境
const dom = new JSDOM('<!DOCTYPE html><html><body></body></html>', {
  url: 'http://localhost',
  pretendToBeVisual: true,
  resources: 'usable'
})

global.window = dom.window
global.document = window.document
global.localStorage = window.localStorage
global.HTMLElement = window.HTMLElement

describe('手动jsdom环境测试', () => {
  it('应该有window对象', () => {
    expect(typeof window).toBe('object')
    console.log('Window created:', !!window)
  })

  it('应该有document对象', () => {
    expect(typeof document).toBe('object')
    console.log('Document created:', !!document)
  })

  it('应该能够创建DOM元素', () => {
    const div = document.createElement('div')
    div.textContent = 'Test'
    document.body.appendChild(div)
    expect(document.querySelector('div').textContent).toBe('Test')
  })
})