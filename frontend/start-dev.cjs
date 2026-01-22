#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

// 设置工作目录为 frontend
process.chdir(__dirname);

// 启动 vite 开发服务器
const vite = spawn('npx', ['vite', '--host', '--port', '3000'], {
  stdio: 'inherit',
  shell: true
});

vite.on('close', (code) => {
  process.exit(code);
});