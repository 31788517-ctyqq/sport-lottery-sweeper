// 简单的测试运行器
import { describe, it, expect } from 'vitest'

console.log('Starting test runner...')

describe('基础测试套件', () => {
  it('测试1: 基础数学运算', () => {
    console.log('Running test 1...')
    expect(1 + 1).toBe(2)
    console.log('✓ Test 1 passed')
  })

  it('测试2: 字符串比较', () => {
    console.log('Running test 2...')
    expect('hello world').toBe('hello world')
    console.log('✓ Test 2 passed')
  })

  it('测试3: 数组包含', () => {
    console.log('Running test 3...')
    expect([1, 2, 3, 4, 5]).toContain(3)
    console.log('✓ Test 3 passed')
  })
})

console.log('Test suite defined, running tests...')