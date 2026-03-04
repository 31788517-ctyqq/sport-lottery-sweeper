import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 支持命令行参数指定端口，默认 3000
const PORT = parseInt(process.argv[2]) || 3000;
const MIME_TYPES = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'application/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.vue': 'text/x-vue'
};

const server = http.createServer((req, res) => {
  console.log(`${req.method} ${req.url}`);

  // 处理 favicon.ico 请求
  if (req.url === '/favicon.ico') {
    res.writeHead(204);
    res.end();
    return;
  }

  // 处理根路径，返回 index.html；去掉前导斜杠防止路径拼接错误
  let filePath = req.url === '/' ? 'index.html' : req.url.replace(/^\//, '');
  filePath = path.join(__dirname, filePath);

  // 安全检查，防止路径遍历攻击
  if (!filePath.startsWith(__dirname)) {
    res.writeHead(403);
    res.end('Forbidden');
    return;
  }

  const ext = path.extname(filePath);
  const contentType = MIME_TYPES[ext] || 'text/plain';

  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        // 文件不存在，返回 index.html（用于 SPA 路由）
        fs.readFile(path.join(__dirname, 'index.html'), (err, content) => {
          if (err) {
            res.writeHead(500);
            res.end('Internal Server Error');
          } else {
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.end(content, 'utf-8');
          }
        });
      } else {
        res.writeHead(500);
        res.end('Internal Server Error');
      }
    } else {
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content, 'utf-8');
    }
  });
});

server.on('error', (err) => {
  console.error('服务器启动错误:', err);
});

try {
  server.listen(PORT, '0.0.0.0', () => {
    console.log(`静态文件服务器运行在 http://localhost:${PORT}/`);
    console.log(`网络访问: http://192.168.56.1:${PORT}/ 或 http://192.168.1.119:${PORT}/`);
  });
} catch (err) {
  console.error('启动异常:', err);
}
