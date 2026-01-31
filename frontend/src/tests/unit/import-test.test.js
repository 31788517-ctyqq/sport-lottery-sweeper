import { describe, it, expect } from 'vitest'

describe('Import test', () => {
  it('should work with imports', () => {
    expect(1).toBe(1)
  })
  
  it('should have console', () => {
    console.log('Test running')
    expect(typeof console.log).toBe('function')
  })
})