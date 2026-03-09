// AI_WORKING: coder1 @2026-01-29 18:36:01 - 修复导入路径和语法问题
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref, onMounted, onUnmounted } from 'vue'
import { useWebSocket } from '../../composables/useWebSocket.js'

// 模拟 WebSocket
global.WebSocket = vi.fn(() => ({
  readyState: 1, // OPEN
  send: vi.fn(),
  close: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn()
}))

describe('useWebSocket.js', () => {
  let websocket
  let mockWs
  
  beforeEach(() => {
    vi.clearAllMocks()
    
    // 创建 mock WebSocket 实例
    mockWs = {
      readyState: 1,
      send: vi.fn(),
      close: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      url: 'ws://localhost:8080/ws'
    }
    
    WebSocket.mockReturnValue(mockWs)
    
    // Mock console methods
    vi.spyOn(console, 'log').mockImplementation(() => {})
    vi.spyOn(console, 'error').mockImplementation(() => {})
    vi.spyOn(console, 'warn').mockImplementation(() => {})
    
    websocket = useWebSocket('ws://localhost:8080/ws')
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('初始状态', () => {
    it('应该初始化正确的连接状态', () => {
      expect(websocket.isConnected.value).toBe(false)
      expect(websocket.connectionStatus.value).toBe('disconnected')
      expect(websocket.error.value).toBe('')
      expect(websocket.reconnectAttempts.value).toBe(0)
    })

    it('应该初始化空的消息队列和数据', () => {
      expect(websocket.messages.value).toEqual([])
      expect(websocket.lastMessage.value).toBeNull()
      expect(websocket.subscriptions.value).toEqual(new Set())
    })
  })

  describe('连接管理', () => {
    it('应该能够建立 WebSocket 连接', async () => {
      // 模拟成功的连接序列
      const connectHandler = vi.fn()
      mockWs.addEventListener.mockImplementation((event, handler) => {
        if (event === 'open') {
          setTimeout(() => handler(), 0)
        }
      })
      
      websocket.connect()
      
      expect(WebSocket).toHaveBeenCalledWith('ws://localhost:8080/ws')
      expect(websocket.connectionStatus.value).toBe('connecting')
      
      // 等待连接建立
      await new Promise(resolve => setTimeout(resolve, 10))
      
      expect(websocket.isConnected.value).toBe(true)
      expect(websocket.connectionStatus.value).toBe('connected')
      expect(websocket.reconnectAttempts.value).toBe(0)
    })

    it('连接失败时应该重试', async () => {
      // 模拟连接失败
      mockWs.addEventListener.mockImplementation((event, handler) => {
        if (event === 'error') {
          setTimeout(() => handler(), 0)
        }
      })
      
      websocket.connect()
      
      await new Promise(resolve => setTimeout(resolve, 10))
      
      expect(websocket.connectionStatus.value).toBe('error')
      expect(websocket.reconnectAttempts.value).toBe(1)
      expect(websocket.error.value).toContain('Connection failed')
    })

    it('应该能够断开连接', () => {
      websocket.connect()
      websocket.disconnect()
      
      expect(mockWs.close).toHaveBeenCalled()
      expect(websocket.isConnected.value).toBe(false)
      expect(websocket.connectionStatus.value).toBe('disconnected')
    })

    it('断开连接时应该清理事件监听器', () => {
      websocket.connect()
      websocket.disconnect()
      
      expect(mockWs.removeEventListener).toHaveBeenCalledWith('open', expect.any(Function))
      expect(mockWs.removeEventListener).toHaveBeenCalledWith('message', expect.any(Function))
      expect(mockWs.removeEventListener).toHaveBeenCalledWith('close', expect.any(Function))
      expect(mockWs.removeEventListener).toHaveBeenCalledWith('error', expect.any(Function))
    })
  })

  describe('重连机制', () => {
    it('应该支持指数退避重连', async () => {
      vi.useFakeTimers()
      
      mockWs.addEventListener.mockImplementation((event, handler) => {
        if (event === 'error') {
          setTimeout(() => handler(), 0)
        }
      })
      
      websocket.connect()
      
      // 第一次失败
      await new Promise(resolve => setTimeout(resolve, 10))
      expect(websocket.reconnectAttempts.value).toBe(1)
      
      // 快进到重连时间
      vi.advanceTimersByTime(1000)
      
      // 第二次失败  
      await new Promise(resolve => setTimeout(resolve, 10))
      expect(websocket.reconnectAttempts.value).toBe(2)
      
      // 快进到更长的重连时间
      vi.advanceTimersByTime(2000)
      
      expect(mockWs.close).toHaveBeenCalled()
      
      vi.useRealTimers()
    })

    it('达到最大重连次数后应该停止', async () => {
      vi.useFakeTimers()
      
      mockWs.addEventListener.mockImplementation((event, handler) => {
        if (event === 'error') {
          setTimeout(() => handler(), 0)
        }
      })
      
      websocket.connect()
      
      // 模拟达到最大重连次数
      for (let i = 0; i < 6; i++) {
        await new Promise(resolve => setTimeout(resolve, 10))
        vi.advanceTimersByTime(Math.pow(2, i) * 1000)
      }
      
      expect(websocket.connectionStatus.value).toBe('failed')
      expect(websocket.error.value).toContain('Max reconnection attempts reached')
      
      vi.useRealTimers()
    })

    it('连接成功后应该重置重连计数', async () => {
      // 先失败几次
      mockWs.addEventListener.mockImplementation((event, handler) => {
        if (event === 'error') {
          setTimeout(() => handler(), 0)
        }
      })
      
      websocket.connect()
      await new Promise(resolve => setTimeout(resolve, 10))
      expect(websocket.reconnectAttempts.value).toBe(1)
      
      // 然后成功连接
      mockWs.addEventListener.mockImplementation((event, handler) => {
        if (event === 'open') {
          setTimeout(() => handler(), 0)
        }
      })
      
      websocket.connect()
      await new Promise(resolve => setTimeout(resolve, 10))
      
      expect(websocket.reconnectAttempts.value).toBe(0)
    })
  })

  describe('消息处理', () => {
    it('应该能够发送消息', () => {
      websocket.connect()
      mockWs.readyState = 1 // OPEN
      
      websocket.send({ type: 'subscribe', channel: 'matches' })
      
      expect(mockWs.send).toHaveBeenCalledWith(
        JSON.stringify({ type: 'subscribe', channel: 'matches' })
      )
    })

    it('连接未建立时应该将消息加入队列', () => {
      mockWs.readyState = 0 // CONNECTING
      
      websocket.send({ type: 'test', data: 'hello' })
      
      expect(mockWs.send).not.toHaveBeenCalled()
      expect(websocket.messageQueue.value).toContainEqual(
        JSON.stringify({ type: 'test', data: 'hello' })
      )
    })

    it('连接建立后应该发送队列中的消息', async () => {
      mockWs.readyState = 0 // CONNECTING
      
      websocket.send({ type: 'queued', data: 'first' })
      websocket.send({ type: 'queued', data: 'second' })
      
      expect(websocket.messageQueue.value).toHaveLength(2)
      
      // 建立连接
      mockWs.addEventListener.mockImplementation((event, handler) => {
        if (event === 'open') {
          setTimeout(() => handler(), 0)
        }
      })
      
      websocket.connect()
      await new Promise(resolve => setTimeout(resolve, 10))
      
      expect(mockWs.send).toHaveBeenCalledTimes(2)
      expect(websocket.messageQueue.value).toHaveLength(0)
    })

    it('应该处理接收到的消息', async () => {
      const messageHandler = vi.fn()
      websocket.onMessage(messageHandler)
      
      // 模拟接收消息
      const testMessage = { type: 'match_update', data }
      const messageEvent = { data: JSON.stringify(testMessage) }
      
      mockWs.addEventListener.mockImplementation((event, handler) => {
        if (event === 'message') {
          setTimeout(() => handler(messageEvent), 0)
        }
      })
      
      websocket.connect()
      await new Promise(resolve => setTimeout(resolve, 10))
      
      expect(websocket.messages.value).toContainEqual(testMessage)
      expect(websocket.lastMessage.value).toEqual(testMessage)
      expect(messageHandler).toHaveBeenCalledWith(testMessage)
    })

    it('应该过滤重复消息', async () => {
      websocket.connect()
      
      const message1 = { type: 'update', id: 1, data: 'same' }
      const message2 = { type: 'update', id: 1, data: 'same' } // 相同ID的消息
      
      // 发送第一条消息
      mockWs.addEventListener.mockImplementation((event, handler) => {
        if (event === 'message') {
          setTimeout(() => {
            handler({ data: JSON.stringify(message1) })
            // 立即发送第二条相同消息
            handler({ data: JSON.stringify(message2) })
          }, 0)
        }
      })
      
      await new Promise(resolve => setTimeout(resolve, 10))
      
      // 应该只有一条消息（去重后）
      expect(websocket.messages.value.filter(m => m.id === 1)).toHaveLength(1)
    })
  })

  describe('订阅管理', () => {
    it('应该能够订阅频道', () => {
      websocket.subscribe('matches')
      
      expect(websocket.subscriptions.value.has('matches')).toBe(true)
      expect(mockWs.send).toHaveBeenCalledWith(
        JSON.stringify({ type: 'subscribe', channels: ['matches'] })
      )
    })

    it('应该能够取消订阅频道', () => {
      websocket.subscriptions.value.add('matches')
      websocket.unsubscribe('matches')
      
      expect(websocket.subscriptions.value.has('matches')).toBe(false)
      expect(mockWs.send).toHaveBeenCalledWith(
        JSON.stringify({ type: 'unsubscribe', channels: ['matches'] })
      )
    })

    it('应该支持批量订阅', () => {
      websocket.subscribe(['matches', 'scores', 'news'])
      
      expect(websocket.subscriptions.value.has('matches')).toBe(true)
      expect(websocket.subscriptions.value.has('scores')).toBe(true)
      expect(websocket.subscriptions.value.has('news')).toBe(true)
    })

    it('连接断开时应该清空订阅', () => {
      websocket.subscriptions.value.add('matches')
      websocket.subscriptions.value.add('scores')
      
      websocket.disconnect()
      
      expect(websocket.subscriptions.value.size).toBe(0)
    })
  })

  describe('心跳检测', () => {
    it('应该定期发送心跳消息', async () => {
      vi.useFakeTimers()
      
      websocket.connect()
      mockWs.addEventListener.mockImplementation((event, handler) => {
        if (event === 'open') {
          setTimeout(() => handler(), 0)
        }
      })
      
      await new Promise(resolve => setTimeout(resolve, 10))
      
      // 快进30秒（心跳间隔）
      vi.advanceTimersByTime(30000)
      
      expect(mockWs.send).toHaveBeenCalledWith(
        JSON.stringify({ type: 'ping' })
      )
      
      vi.useRealTimers()
    })

    it('应该处理心跳超时', async () => {
      vi.useFakeTimers()
      
      websocket.connect()
      
      // 不模拟收到 pong 响应
      mockWs.addEventListener.mockImplementation((event, handler) => {
        if (event === 'open') {
          setTimeout(() => handler(), 0)
        }
      })
      
      await new Promise(resolve => setTimeout(resolve, 10))
      
      // 快进到心跳超时时间
      vi.advanceTimersByTime(90000) // 90秒超时
      
      expect(websocket.connectionStatus.value).toBe('error')
      expect(mockWs.close).toHaveBeenCalled()
      
      vi.useRealTimers()
    })
  })

  describe('错误处理', () => {
    it('应该处理连接错误', async () => {
      const error = new Error('Connection refused')
      mockWs.addEventListener.mockImplementation((event, handler) => {
        if (event === 'error') {
          setTimeout(() => handler({ error }), 0)
        }
      })
      
      websocket.connect()
      await new Promise(resolve => setTimeout(resolve, 10))
      
      expect(websocket.error.value).toContain('Connection refused')
      expect(console.error).toHaveBeenCalled()
    })

    it('应该处理消息解析错误', async () => {
      mockWs.addEventListener.mockImplementation((event, handler) => {
        if (event === 'message') {
          setTimeout(() => handler({ data: 'invalid json' }), 0)
        }
      })
      
      websocket.connect()
      await new Promise(resolve => setTimeout(resolve, 10))
      
      expect(console.warn).toHaveBeenCalledWith('Failed to parse WebSocket message:', expect.any(Error))
    })

    it('应该处理连接关闭', async () => {
      mockWs.addEventListener.mockImplementation((event, handler) => {
        if (event === 'close') {
          setTimeout(() => handler({ code: 1000, reason: 'Normal closure' }), 0)
        }
      })
      
      websocket.connect()
      await new Promise(resolve => setTimeout(resolve, 10))
      
      expect(websocket.isConnected.value).toBe(false)
      expect(websocket.connectionStatus.value).toBe('disconnected')
    })
  })

  describe('性能优化', () => {
    it('应该限制消息历史记录数量', async () => {
      websocket.connect()
      
      // 发送超过限制的100条消息
      mockWs.addEventListener.mockImplementation((event, handler) => {
        if (event === 'message') {
          for (let i = 0; i < 150; i++) {
            setTimeout(() => {
              handler({ data: JSON.stringify({ type: 'update', id: i }) })
            }, 0)
          }
        }
      })
      
      await new Promise(resolve => setTimeout(resolve, 50))
      
      expect(websocket.messages.value.length).toBeLessThanOrEqual(100)
    })

    it('应该及时清理事件监听器避免内存泄漏', () => {
      const initialRemoveCalls = mockWs.removeEventListener.mock.calls.length
      
      websocket.connect()
      websocket.disconnect()
      
      expect(mockWs.removeEventListener.mock.calls.length).toBeGreaterThan(initialRemoveCalls)
    })
  })
})
// AI_DONE: coder1 @2026-01-29 18:36:01
