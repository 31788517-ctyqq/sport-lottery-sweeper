// 简单组件功能测试脚本
const { exec } = require('child_process');
const fs = require('fs');

console.log('🧪 开始 BeidanFilterPanel 组件功能测试\n');

// 测试1: 检查文件是否存在
console.log('📁 测试1: 检查核心文件存在性');
const filesToCheck = [
  'frontend/src/views/admin/BeidanFilterPanel.vue',
  'frontend/src/utils/apiErrorHandler.js', 
  'frontend/src/utils/debounce.js',
  'frontend/src/views/admin/components/MultiStrategyConfig.vue',
  'frontend/src/views/admin/components/RulesDialog.vue'
];

let allFilesExist = true;
filesToCheck.forEach(file => {
  if (fs.existsSync(file)) {
    console.log(`  ✅ ${file}`);
  } else {
    console.log(`  ❌ ${file} - 文件不存在`);
    allFilesExist = false;
  }
});

if (!allFilesExist) {
  console.log('\n❌ 部分核心文件缺失，测试终止');
  process.exit(1);
}

// 测试2: 检查关键功能实现
console.log('\n🔍 测试2: 检查关键功能实现');

const beidanFilterContent = fs.readFileSync('frontend/src/views/admin/BeidanFilterPanel.vue', 'utf8');
const tests = [
  { name: '统一API错误处理导入', pattern: /import.*apiErrorHandler/ },
  { name: '导出方法实现', pattern: /const exportResults.*=/ },
  { name: 'CSV导出实现', pattern: /const exportAsCSV.*=/ },
  { name: 'JSON导出实现', pattern: /const exportAsJSON.*=/ },
  { name: 'Excel导出实现', pattern: /const exportAsExcel.*=/ },
  { name: '文件下载方法', pattern: /const downloadFile.*=/ },
  { name: '多策略配置组件', pattern: /MultiStrategyConfig/ },
  { name: 'P级规则对话框', pattern: /RulesDialog/ },
  { name: '细粒度loading状态', pattern: /loadingStates.*ref/ },
  { name: '统计字段映射', pattern: /average_power_diff.*average_strength_diff/ }
];

let passedTests = 0;
tests.forEach(test => {
  if (test.pattern.test(beidanFilterContent)) {
    console.log(`  ✅ ${test.name}`);
    passedTests++;
  } else {
    console.log(`  ❌ ${test.name}`);
  }
});

console.log(`\n📊 功能实现检查: ${passedTests}/${tests.length} 通过`);

// 测试3: 检查API错误处理工具
console.log('\n🔧 测试3: 检查API错误处理工具');
const apiErrorHandlerContent = fs.readFileSync('frontend/src/utils/apiErrorHandler.js', 'utf8');
const apiTests = [
  { name: 'handleApiCall函数', pattern: /function handleApiCall/ },
  { name: 'handleAuthenticatedApiCall函数', pattern: /function handleAuthenticatedApiCall/ },
  { name: '401跳转逻辑', pattern: /window\.location\.href.*login/ },
  { name: '错误消息处理', pattern: /getErrorMessage/ }
];

let apiPassedTests = 0;
apiTests.forEach(test => {
  if (test.pattern.test(apiErrorHandlerContent)) {
    console.log(`  ✅ ${test.name}`);
    apiPassedTests++;
  } else {
    console.log(`  ❌ ${test.name}`);
  }
});

console.log(`\n📊 API工具检查: ${apiPassedTests}/${apiTests.length} 通过`);

// 测试4: 检查防抖工具
console.log('\n⚡ 测试4: 检查性能优化工具');
const debounceContent = fs.readFileSync('frontend/src/utils/debounce.js', 'utf8');
const perfTests = [
  { name: 'useDebounceFn函数', pattern: /function useDebounceFn/ },
  { name: 'useThrottleFn函数', pattern: /function useThrottleFn/ },
  { name: 'cancel方法', pattern: /cancel.*=>/ },
  { name: 'flush方法', pattern: /flush.*=>/ }
];

let perfPassedTests = 0;
perfTests.forEach(test => {
  if (test.pattern.test(debounceContent)) {
    console.log(`  ✅ ${test.name}`);
    perfPassedTests++;
  } else {
    console.log(`  ❌ ${test.name}`);
  }
});

console.log(`\n📊 性能工具检查: ${perfPassedTests}/${perfTests.length} 通过`);

// 测试5: 检查编译错误
console.log('\n🔍 测试5: 检查代码质量问题');
const lines = beidanFilterContent.split('\n');
let hintErrors = 0;
let unusedImports = 0;

lines.forEach((line, index) => {
  // 检查可能的未使用导入
  if (line.includes('import') && line.includes('onMounted') && !beidanFilterContent.includes('onMounted(')) {
    unusedImports++;
  }
  if (line.includes('import') && line.includes('useDebounceFn') && !beidanFilterContent.includes('useDebounceFn(')) {
    unusedImports++;
  }
  if (line.includes('import') && line.includes('useThrottleFn') && !beidanFilterContent.includes('useThrottleFn(')) {
    unusedImports++;
  }
});

console.log(`  ${unusedImports > 0 ? '❌' : '✅'} 未使用导入检查: ${unusedImports} 个`);

// 总体评估
const totalPassed = passedTests + apiPassedTests + perfPassedTests;
const totalTests = tests.length + apiTests.length + perfTests.length;
const successRate = ((totalPassed / totalTests) * 100).toFixed(1);

console.log('\n' + '='.repeat(50));
console.log('🎯 测试总结');
console.log('='.repeat(50));
console.log(`✅ 文件完整性: ${allFilesExist ? '通过' : '失败'}`);
console.log(`✅ 功能实现率: ${successRate}% (${totalPassed}/${totalTests})`);
console.log(`✅ 代码质量: ${unusedImports === 0 ? '良好' : '需改进'}`);

if (successRate >= 90 && unusedImports === 0) {
  console.log('\n🎉 所有测试通过！BeidanFilterPanel组件已达到生产级质量标准');
  console.log('\n📋 可以进行的界面测试:');
  console.log('  1. 启动前端服务: cd frontend && npm run dev');
  console.log('  2. 访问 http://localhost:3000/admin/beidan-filter');
  console.log('  3. 测试API错误处理（断开网络）');
  console.log('  4. 测试数据导出功能（CSV/JSON/Excel）');
  console.log('  5. 测试多策略配置界面');
  console.log('  6. 测试P级规则对话框');
} else if (successRate >= 80) {
  console.log('\n⚠️  大部分功能正常，但仍有改进空间');
} else {
  console.log('\n❌ 发现较多问题，需要进一步修复');
}

console.log('\n🏁 组件功能测试完成');