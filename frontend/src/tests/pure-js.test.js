// 纯JavaScript测试，无任何依赖
import { describe, it, expect } from 'vitest'

describe('纯JavaScript测试套件', () => {
  it('纯JavaScript测试应该工作', () => {
    console.log('纯JS测试运行中...')
    expect(true).toBe(true)
  })

  it('数学运算', () => {
    expect(2 + 2).toBe(4)
  })
})