import { describe, it, expect } from 'vitest'

describe('Minimal test suite', () => {
  it('should pass', () => {
    expect(1).toBe(1)
  })
  
  it('should fail', () => {
    expect(1).toBe(2)
  })
})