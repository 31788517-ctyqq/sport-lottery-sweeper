import { test, expect } from 'vitest'

test('basic test should work', () => {
  expect(1 + 1).toBe(2)
})

test('another test', () => {
  expect(typeof console).toBe('object')
})

console.log('Test file loaded successfully')