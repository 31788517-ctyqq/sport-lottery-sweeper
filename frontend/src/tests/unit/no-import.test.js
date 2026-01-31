// 不使用任何导入，依赖全局变量
// 如果globals: true生效，这些变量应该可用

// 检查全局变量是否存在
console.log('Global describe:', typeof describe)
console.log('Global it:', typeof it)
console.log('Global expect:', typeof expect)
console.log('Global test:', typeof test)

// 使用全局describe和it
describe('No import test suite', () => {
  it('should work without imports', () => {
    expect(true).toBe(true)
  })
  
  it('should have global functions', () => {
    expect(typeof describe).toBe('function')
    expect(typeof it).toBe('function')
    expect(typeof expect).toBe('function')
  })
})