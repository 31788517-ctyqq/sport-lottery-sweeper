/**
 * 日志管理模块测试执行脚本
 * 运行日志管理模块的所有测试
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('开始运行日志管理模块测试...\n');

// 检查测试文件是否存在
const testFiles = [
  './frontend/tests/unit/log_management.test.js',
  './frontend/tests/e2e/log_management.test.js',
  './frontend/tests/integration/log_api.test.js'
];

// 验证测试文件是否存在
for (const file of testFiles) {
  if (!fs.existsSync(file)) {
    console.error(`❌ 错误: 测试文件不存在: ${file}`);
    process.exit(1);
  }
}

console.log('✅ 所有测试文件都存在\n');

// 定义测试任务
const testTasks = [
  {
    name: '单元测试',
    command: 'cd frontend && npm test -- tests/unit/log_management.test.js',
    description: '测试日志管理模块的各个组件功能'
  },
  {
    name: 'API集成测试',
    command: 'cd frontend && npm test -- tests/integration/log_api.test.js',
    description: '测试日志管理模块的API交互功能'
  },
  {
    name: 'E2E测试',
    command: 'cd frontend && npm test -- tests/e2e/log_management.test.js',
    description: '端到端测试用户操作流程'
  }
];

// 运行测试
let passedTests = 0;
let failedTests = 0;

for (const task of testTasks) {
  console.log(`🚀 开始运行: ${task.name}`);
  console.log(`📝 描述: ${task.description}`);
  console.log(`🔧 命令: ${task.command}\n`);

  try {
    // 运行测试命令
    const startTime = Date.now();
    execSync(task.command, { stdio: 'inherit' });
    const endTime = Date.now();
    
    console.log(`✅ ${task.name} 通过! (耗时: ${(endTime - startTime)/1000}s)\n`);
    passedTests++;
  } catch (error) {
    console.error(`❌ ${task.name} 失败!\n`);
    failedTests++;
  }
}

// 输出测试总结
console.log('='.repeat(50));
console.log('📊 测试总结:');
console.log(`✅ 通过: ${passedTests} 个`);
console.log(`❌ 失败: ${failedTests} 个`);
console.log(`📈 通过率: ${passedTests > 0 ? Math.round((passedTests/(passedTests+failedTests))*100) : 0}%`);
console.log('='.repeat(50));

// 根据测试结果退出
process.exit(failedTests > 0 ? 1 : 0);