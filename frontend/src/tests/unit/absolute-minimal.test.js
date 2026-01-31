// 绝对最小测试 - 不使用任何导入，依赖全局变量
// 如果globals: true生效，这些变量应该可用

// 直接调用全局函数
globalThis.describe('Absolute minimal test', () => {
  globalThis.it('should work', () => {
    globalThis.expect(1).toBe(1)
  })
})