import { describe, it, expect } from 'vitest'

describe('release smoke', () => {
  it('runs vitest in release mode', () => {
    expect(true).toBe(true)
  })

  it('keeps runtime basics available', () => {
    expect(typeof Promise).toBe('function')
    expect(typeof Date.now).toBe('function')
  })
})
