// 测试全局变量是否可用，不导入任何内容
// 如果globals: true生效，describe、it、expect应该全局可用

describe('Global variables test', () => {
  it('should have global describe function', () => {
    expect(typeof describe).toBe('function')
  })
  
  it('should have global it function', () => {
    expect(typeof it).toBe('function')
  })
  
  it('should have global expect function', () => {
    expect(typeof expect).toBe('function')
  })
  
  it('simple assertion', () => {
    expect(1 + 1).toBe(2)
  })
})