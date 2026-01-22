const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3000;

console.log('🚀 启动简易前端服务器...');
console.log('📁 工作目录:', __dirname);

// 检查文件是否存在
const indexPath = path.join(__dirname, 'index.html');
const publicIndexPath = path.join(__dirname, 'public', 'index.html');

console.log('📄 检查 index.html 文件:');
console.log('  - 根目录 index.html:', fs.existsSync(indexPath) ? '✅ 存在' : '❌ 不存在');
console.log('  - public/index.html:', fs.existsSync(publicIndexPath) ? '✅ 存在' : '❌ 不存在');

// 设置静态文件目录
app.use(express.static(path.join(__dirname, 'public')));
app.use('/src', express.static(path.join(__dirname, 'src')));

// 主页路由 - 重定向到前端管理页面
app.get('/', (req, res) => {
  console.log('🏠 访问主页，重定向到前端管理页面');
  // 重定向到前端Vue应用的管理仪表板
  res.redirect('http://localhost:5173/admin/dashboard');
});

// 处理所有其他路由，返回主页面（SPA支持）
app.get('*', (req, res) => {
  console.log(`🌐 访问路径: ${req.path}`);
  if (req.path.startsWith('/api/')) {
    // API请求转发到后端
    res.status(404).json({ error: 'API endpoint not found', path: req.path });
  } else if (fs.existsSync(path.join(__dirname, 'public', req.path))) {
    // 静态文件存在
    res.sendFile(path.join(__dirname, 'public', req.path));
  } else {
    // SPA路由，返回主页面
    if (fs.existsSync(indexPath)) {
      res.sendFile(indexPath);
    } else {
      res.redirect('/');
    }
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`\n🎉 前端服务器启动成功！`);
  console.log(`📍 本地访问: http://localhost:${PORT}`);
  console.log(`🌐 网络访问: http://192.168.1.119:${PORT}`);
  console.log(`🔗 后端API: http://localhost:8001/api`);
  console.log(`\n按 Ctrl+C 停止服务器\n`);
});