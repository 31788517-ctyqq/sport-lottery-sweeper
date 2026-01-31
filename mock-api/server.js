import express from 'express'
import cors from 'cors'

const app = express()
const PORT = 3000

app.use(cors())
app.use(express.json())

// 模拟用户数据
const mockUsers = [
  { username: 'admin', password: '123456', role: 'admin' },
  { username: 'demo', password: 'demo', role: 'user' }
]

// 登录接口
app.post('/api/auth/login', (req, res) => {
  const { username, password } = req.body
  const user = mockUsers.find(u => u.username === username && u.password === password)
  if (user) {
    return res.json({ code: 200, data: { token: 'mock-jwt-token', userInfo: { username: user.username, role: 'admin' } } })
  }
  return res.status(401).json({ code: 401, message: '用户名或密码错误' })
})

// 获取用户信息
app.get('/api/auth/profile', (req, res) => {
  const token = req.headers.authorization?.split(' ')[1]
  if (token === 'mock-jwt-token') {
    return res.json({ code: 200, data: { username: 'admin', role: 'admin' } })
  }
  return res.status(401).json({ code: 401, message: '未授权' })
})

// 仪表板统计数据
app.get('/api/dashboard/summary', (req, res) => {
  return res.json({
    code: 200,
    data: {
      totalMatches: 1256,
      todayMatches: 32,
      activeUsers: 568,
      systemHealth: 98.5
    }
  })
})

// 情报模块示例数据
app.get('/api/intelligence/screening/list', (req, res) => {
  return res.json({
    code: 200,
    data: {
      items: [
        { id: 1, name: '初筛规则A', status: 'active', matchCount: 120 },
        { id: 2, name: '冷门检测B', status: 'paused', matchCount: 45 }
      ],
      total: 2
    }
  })
})

// 兜底 404
app.use((req, res) => {
  res.status(404).json({ code: 404, message: '接口不存在' })
})

app.listen(PORT, () => {
  console.log(`Mock API Server running at http://localhost:${PORT}`)
})