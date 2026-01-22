/**
 * 优化的前端启动脚本，包含时间监测功能
 */
import { spawn, execSync } from 'child_process';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { performance } from 'perf_hooks';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// 记录启动时间
const startTime = performance.now();
console.log(`🚀 启动前端性能监测脚本`);
console.log(`📅 时间: ${new Date().toISOString()}`);
console.log(`📍 路径: ${__dirname}`);
console.log('');

// 检查 Node.js 版本
const nodeVersion = process.version;
const majorVersion = parseInt(nodeVersion.split('.')[0].substring(1));
if (majorVersion < 18) {
  console.warn(`⚠️  警告: 检测到 Node.js 版本 ${nodeVersion}，建议使用 Node.js 18 或更高版本`);
} else {
  console.log(`✅ Node.js 版本: ${nodeVersion}`);
}

// 检查 pnpm 是否可用
let packageManager = 'npm';
try {
  execSync('pnpm --version', { stdio: 'pipe' });
  packageManager = 'pnpm';
  console.log(`✅ 包管理器: ${packageManager}`);
} catch (e) {
  try {
    execSync('yarn --version', { stdio: 'pipe' });
    packageManager = 'yarn';
    console.log(`✅ 包管理器: ${packageManager}`);
  } catch (e) {
    console.log(`✅ 包管理器: ${packageManager} (pnpm/yarn 未安装，使用 npm)`);
  }
}

console.log('');
console.log('🔍 启动时间监测:');
const devServerStartTime = performance.now();

// 启动开发服务器
const frontendPath = resolve(__dirname, '../frontend');
const devServer = spawn(packageManager, ['run', 'dev'], {
  cwd: frontendPath,
  stdio: 'inherit',
  shell: true
});

devServer.on('error', (err) => {
  console.error(`❌ 启动失败:`, err.message);
});

devServer.on('close', (code) => {
  const totalTime = performance.now() - startTime;
  console.log('');
  console.log('🏁 开发服务器已停止');
  console.log(`⏱️  总运行时间: ${(totalTime / 1000).toFixed(2)} 秒`);
  process.exit(code);
});

// 输出启动时间
setTimeout(() => {
  const devServerBootTime = performance.now() - devServerStartTime;
  console.log(`⚡ 开发服务器启动时间: ${devServerBootTime.toFixed(2)} 毫秒 (从执行命令开始计算)`);
}, 5000); // 延迟5秒以确保服务器已启动