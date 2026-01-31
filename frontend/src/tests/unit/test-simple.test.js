// 使用test而不是describe/it
import { test, expect } from 'vitest'

test('simple test with test function', () => {
  expect(1).toBe(1)
})

test('another test', () => {
  expect(2 + 2).toBe(4)
})