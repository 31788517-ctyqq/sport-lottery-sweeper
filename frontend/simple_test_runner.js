#!/usr/bin/env node

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

console.log('🧪 开始运行前端测试...\n');

const testFiles = [
  'src/tests/unit/utils/date.test.js',
  'src/tests/unit/utils/number.test.js', 
  'src/tests/unit/utils/string.test.js',
  'src/tests/unit/utils/formatters.test.js',
  'src/tests/unit/utils/beidanFilterUtils.test.js',
  'src/tests/unit/components/BeidanFilterPanel.test.js',
  'src/tests/unit/components/BeidanFilterPanel.api.test.js',
  'src/tests/unit/store/auth.test.js',
  'src/tests/unit/router/beidanFilterRoute.test.js'
];

async function runTestFile(testFile) {
  return new Promise((resolve) => {
    console.log(`\n📋 运行测试: ${testFile}`);
    console.log('─'.repeat(50));
    
    const vitest = spawn('npx', ['vitest', 'run', testFile, '--reporter=basic'], {
      cwd: __dirname,
      stdio: 'inherit',
      shell: true
    });
    
    vitest.on('close', (code) => {
      if (code === 0) {
        console.log(`✅ ${testFile} 通过`);
      } else {
        console.log(`❌ ${testFile} 失败 (退出码: ${code})`);
      }
      resolve(code);
    });
  });
}

async function runAllTests() {
  let passed = 0;
  let failed = 0;
  
  for (const testFile of testFiles) {
    const result = await runTestFile(testFile);
    if (result === 0) {
      passed++;
    } else {
      failed++;
    }
  }
  
  console.log('\n' + '='.repeat(60));
  console.log('📊 测试结果汇总:');
  console.log(`✅ 通过: ${passed}`);
  console.log(`❌ 失败: ${failed}`);
  console.log(`📋 总计: ${testFiles.length}`);
  console.log('='.repeat(60));
  
  if (failed > 0) {
    process.exit(1);
  }
}

runAllTests().catch(console.error);