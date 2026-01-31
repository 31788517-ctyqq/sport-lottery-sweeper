// 测试globals是否可用
describe('Global availability test', () => {
  it('should have global expect', () => {
    expect(1).toBe(1)
  })
  
  it('should have global test', () => {
    test('nested test', () => {
      expect(2).toBe(2)
    })
  })
})

// 直接测试console
console.log('Test file loaded')