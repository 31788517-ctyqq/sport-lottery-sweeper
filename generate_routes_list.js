const fs = require('fs');

// 读取路由配置文件
const routerContent = fs.readFileSync('./frontend/src/router/index.js', 'utf-8');

// 提取所有路由定义
const routePattern = /\{\s*\n(?:\s*path:\s*['"]([^'"]+)['"],?\s*\n(?:[^,}]*(?:,\n|\n))*?name:\s*['"]([^'"]+)['"],?\s*\n)?/g;
let match;
const routes = [];

while ((match = routePattern.exec(routerContent)) !== null) {
  if (match[1] && match[2]) {
    routes.push({ path: match[1], name: match[2] });
  }
}

console.log('竞彩足球扫盘系统 - 完整路由地址列表');
console.log('='.repeat(50));

// 按路径排序
routes.sort((a, b) => a.path.localeCompare(b.path));

routes.forEach(route => {
  console.log(`${route.path.padEnd(35)} -> ${route.name}`);
});

console.log('\n总路由数量:', routes.length);