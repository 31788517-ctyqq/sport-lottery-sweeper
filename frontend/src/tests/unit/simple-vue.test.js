import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'

// 简单的Vue组件
const SimpleComponent = {
  template: '<div>{{ msg }}</div>',
  props: ['msg']
}

describe('简单Vue组件测试', () => {
  it('应该渲染props', () => {
    const wrapper = mount(SimpleComponent, {
      props: { msg: 'Hello World' }
    })
    expect(wrapper.text()).toBe('Hello World')
  })
})