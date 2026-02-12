#!/usr/bin/env node

/**
 * 简化版 Vitest 测试运行器
 * 绕过 vitest watch 模式问题，直接执行测试
 * 基于 docs/TEST_GRANULARITY_GUIDE.md 测试颗粒度要求
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 启动简化版测试运行器...\n');

// 测试配置
const TEST_CONFIG = {
  testFiles: [
    'frontend/tests/unit/views/admin/BeidanFilterPanel.unit.spec.js',
    'frontend/tests/unit/views/admin/BeidanFilterPanel.unit.enhanced.spec.js',
    'frontend/tests/unit/views/admin/BeidanFilterPanel.functional.test.js',
    'frontend/tests/integration/views/admin/BeidanFilterPanel.integration.enhanced.spec.js'
  ],
  coverage: {
    enabled: true,
    threshold: {
      statements: 80,
      branches: 75,
      functions: 80,
      lines: 80
    }
  },
  reporters: ['verbose', 'json', 'html']
};

// 检查测试文件是否存在
function checkTestFiles() {
  console.log('📁 检查测试文件...');
  const missingFiles = [];
  
  TEST_CONFIG.testFiles.forEach(file => {
    const fullPath = path.resolve(process.cwd(), file);
    if (fs.existsSync(fullPath)) {
      console.log(`  ✅ ${file}`);
    } else {
      console.log(`  ❌ ${file} (缺失)`);
      missingFiles.push(file);
    }
  });
  
  if (missingFiles.length > 0) {
    console.log('\n⚠️  以下测试文件缺失，正在创建...');
    createMissingTestFiles(missingFiles);
  }
  
  return missingFiles.length === 0;
}

// 创建缺失的测试文件
function createMissingTestFiles(missingFiles) {
  const fs = require('fs');
  
  missingFiles.forEach(file => {
    if (file.includes('functional.test.js')) {
      console.log('  📝 创建功能测试文件...');
      // 这里可以复制之前创建的功能测试文件内容
    }
  });
}

// 运行单个测试文件
async function runSingleTest(testFile) {
  return new Promise((resolve, reject) => {
    console.log(`\n🧪 运行测试: ${testFile}`);
    console.log('=' .repeat(60));
    
    const args = [
      'vitest',
      'run',
      testFile,
      '--reporter=verbose',
      '--watch=false',
      '--run',
      '--threads=false'  // 禁用线程模式，避免watch模式问题
    ];
    
    if (TEST_CONFIG.coverage.enabled) {
      args.push('--coverage');
    }
    
    const vitestProcess = spawn('npx', args, {
      stdio: 'inherit',
      shell: true,
      cwd: process.cwd()
    });
    
    let hasErrors = false;
    
    vitestProcess.on('close', (code) => {
      if (code === 0) {
        console.log(`\n✅ ${testFile} 测试通过!`);
        resolve({ file: testFile, success: true, code });
      } else {
        console.log(`\n❌ ${testFile} 测试失败 (退出码: ${code})`);
        hasErrors = true;
        resolve({ file: testFile, success: false, code, hasErrors });
      }
    });
    
    vitestProcess.on('error', (error) => {
      console.error(`\n💥 ${testFile} 执行错误:`, error.message);
      reject(error);
    });
  });
}

// 生成测试报告
function generateTestReport(results) {
  console.log('\n📊 生成测试报告...\n');
  
  const passedTests = results.filter(r => r.success).length;
  const totalTests = results.length;
  const passRate = ((passedTests / totalTests) * 100).toFixed(1);
  
  const report = {
    timestamp: new Date().toISOString(),
    summary: {
      total: totalTests,
      passed: passedTests,
      failed: totalTests - passedTests,
      passRate: `${passRate}%`
    },
    details: results,
    recommendations: []
  };
  
  // 根据测试结果提供建议
  if (passRate < 80) {
    report.recommendations.push('测试通过率较低，建议检查组件基础功能');
  }
  
  if (results.some(r => r.hasErrors)) {
    report.recommendations.push('部分测试出现错误，建议检查测试环境配置');
  }
  
  // 保存报告
  const reportPath = 'test-report-beidan-filter.json';
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  
  console.log('📋 测试摘要:');
  console.log(`   总测试数: ${totalTests}`);
  console.log(`   通过: ${passedTests}`);
  console.log(`   失败: ${totalTests - passedTests}`);
  console.log(`   通过率: ${passRate}%`);
  console.log(`\n📄 详细报告已保存至: ${reportPath}`);
  
  return report;
}

// 主执行函数
async function main() {
  try {
    console.log('🎯 北单过滤面板测试执行器');
    console.log('基于 docs/TEST_GRANULARITY_GUIDE.md 标准\n');
    
    // 1. 检查测试文件
    const filesReady = checkTestFiles();
    if (!filesReady) {
      console.log('\n⚠️  部分测试文件缺失，但将继续执行可用测试');
    }
    
    // 2. 运行测试
    console.log('\n🚀 开始执行测试套件...\n');
    
    const results = [];
    for (const testFile of TEST_CONFIG.testFiles) {
      try {
        const result = await runSingleTest(testFile);
        results.push(result);
      } catch (error) {
        console.error(`执行 ${testFile} 时出错:`, error);
        results.push({ file: testFile, success: false, error: error.message });
      }
    }
    
    // 3. 生成报告
    const report = generateTestReport(results);
    
    // 4. 输出总结
    console.log('\n🎉 测试执行完成!');
    console.log('\n📝 后续建议:');
    console.log('   1. 查看详细测试报告了解具体问题');
    console.log('   2. 根据失败用例修复组件功能');
    console.log('   3. 重新运行测试验证修复效果');
    console.log('   4. 执行手动测试验证清单中的E2E测试');
    
    // 根据测试结果决定退出码
    const hasFailures = results.some(r => !r.success);
    process.exit(hasFailures ? 1 : 0);
    
  } catch (error) {
    console.error('💥 测试运行器执行失败:', error);
    process.exit(1);
  }
}

// 如果直接运行此文件
if (require.main === module) {
  main();
}

module.exports = {
  runSingleTest,
  generateTestReport,
  TEST_CONFIG
};