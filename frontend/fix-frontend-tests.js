#!/usr/bin/env node

/**
 * 前端测试批量修复脚本
 * 修复以下问题：
 * 1. TypeScript语法在JS文件中（as类型断言）
 * 2. 导入路径错误（相对路径 vs 别名）
 * 3. 缺少Pinia store模拟
 * 4. Element Plus组件重复注册警告
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 测试文件目录
const TEST_DIR = path.join(__dirname, 'src/tests');
const COMPONENTS_DIR = path.join(__dirname, 'src/components');
const STORES_DIR = path.join(__dirname, 'src/stores');

// 已知问题文件列表
const KNOWN_ISSUES = {
  // 语法问题
  'BottomNav.test.js': {
    issues: ['TypeScript类型断言'],
    fix: (content) => {
      // 移除 as MockRouterPush
      return content.replace(/push:\s*vi\.fn\(\)\s+as\s+[A-Z][a-zA-Z]+/g, 'push: vi.fn()');
    }
  },
  
  // 导入路径问题
  'HeaderComponent.test.js': {
    issues: ['导入路径错误'],
    fix: (content) => {
      // 检查导入路径是否正确
      const importLine = `import HeaderComponent from '../../../components/HeaderComponent.vue'`;
      const correctImport = `import HeaderComponent from '@/components/HeaderComponent.vue'`;
      
      if (content.includes(importLine)) {
        console.log('  修复 HeaderComponent 导入路径');
        return content.replace(importLine, correctImport);
      }
      return content;
    }
  },
  
  // 缺少Pinia模拟
  'LoginModal.test.js': {
    issues: ['缺少useAppStore模拟'],
    fix: (content) => {
      // 在vue-i18n模拟后添加Pinia模拟
      const vueI18nMock = `vi.mock('vue-i18n', () => ({`;
      const piniaMock = `
// 模拟Pinia store
vi.mock('@/stores', () => ({
  useAppStore: () => ({
    showLoginModal: false,
    setShowLoginModal: vi.fn(),
    user: null,
    isLoggedIn: false
  })
}));`;
      
      if (content.includes(vueI18nMock) && !content.includes('useAppStore')) {
        console.log('  添加 useAppStore 模拟');
        // 在vue-i18n模拟后添加
        const lines = content.split('\n');
        const newLines = [];
        let added = false;
        
        for (let i = 0; i < lines.length; i++) {
          newLines.push(lines[i]);
          if (lines[i].includes(vueI18nMock) && !added) {
            // 找到vue-i18n模拟的结束位置（下一个空行或describe）
            let j = i + 1;
            while (j < lines.length && lines[j].trim() !== '' && !lines[j].includes('describe(')) {
              j++;
            }
            // 在j处插入
            newLines.push(piniaMock);
            added = true;
          }
        }
        
        return newLines.join('\n');
      }
      return content;
    }
  },
  
  // MainView测试
  'MainView.test.js': {
    issues: ['可能缺少store模拟'],
    fix: (content) => {
      // 检查是否已经有store模拟
      if (!content.includes('useAppStore') && !content.includes('@/stores')) {
        console.log('  添加 useAppStore 模拟到 MainView 测试');
        
        // 在mock部分后添加store模拟
        const mockSection = `vi.mock('@/components/MainContent.vue', () => ({`;
        const storeMock = `
// 模拟Pinia store
vi.mock('@/stores', () => ({
  useAppStore: () => ({
    currentView: 'home',
    setCurrentView: vi.fn(),
    theme: 'light'
  })
}));`;
        
        if (content.includes(mockSection)) {
          const lines = content.split('\n');
          const newLines = [];
          let added = false;
          
          for (let i = 0; i < lines.length; i++) {
            newLines.push(lines[i]);
            if (lines[i].includes(mockSection) && !added) {
              // 找到mock部分的结束位置（下一个空行或describe）
              let j = i + 1;
              while (j < lines.length && lines[j].trim() !== '' && !lines[j].includes('describe(')) {
                j++;
              }
              // 在j处插入
              newLines.push(storeMock);
              added = true;
            }
          }
          
          return newLines.join('\n');
        }
      }
      return content;
    }
  }
};

// 遍历目录查找所有测试文件
function findTestFiles(dir) {
  const testFiles = [];
  
  function scan(currentDir) {
    const entries = fs.readdirSync(currentDir, { withFileTypes: true });
    
    for (const entry of entries) {
      const fullPath = path.join(currentDir, entry.name);
      
      if (entry.isDirectory()) {
        scan(fullPath);
      } else if (entry.isFile() && 
                (entry.name.endsWith('.test.js') || 
                 entry.name.endsWith('.spec.js') ||
                 entry.name.endsWith('.test.ts') ||
                 entry.name.endsWith('.spec.ts'))) {
        testFiles.push(fullPath);
      }
    }
  }
  
  scan(dir);
  return testFiles;
}

// 修复单个文件
function fixFile(filePath) {
  const fileName = path.basename(filePath);
  const relativePath = path.relative(__dirname, filePath);
  
  console.log(`检查文件: ${relativePath}`);
  
  let content = fs.readFileSync(filePath, 'utf8');
  const originalContent = content;
  
  // 应用已知修复（如果文件在KNOWN_ISSUES中）
  if (KNOWN_ISSUES[fileName]) {
    console.log(`  发现已知问题: ${KNOWN_ISSUES[fileName].issues.join(', ')}`);
    content = KNOWN_ISSUES[fileName].fix(content);
  }
  
  // 通用修复：移除TypeScript类型断言
  content = content.replace(/\s+as\s+[A-Z][a-zA-Z]+(?=\s*[,)])/g, '');
  
  // 通用修复：修复常见的相对路径导入
  if (relativePath.includes('src/tests/unit/components')) {
    // 将../../../components 替换为 @/components
    content = content.replace(/from\s+'(\.\.\/){3}components\//g, "from '@/components/");
  }
  
  if (relativePath.includes('src/tests/unit/')) {
    // 将../../stores 替换为 @/stores
    content = content.replace(/from\s+'(\.\.\/){2}stores\//g, "from '@/stores/");
    // 将../../components 替换为 @/components
    content = content.replace(/from\s+'(\.\.\/){2}components\//g, "from '@/components/");
  }
  
  // 检查是否需要添加Pinia store模拟
  if (content.includes('useAppStore') && !content.includes("vi.mock('@/stores'")) {
    console.log('  警告: 文件使用 useAppStore 但缺少模拟');
  }
  
  if (content !== originalContent) {
    fs.writeFileSync(filePath, content, 'utf8');
    console.log('  文件已修复');
    return true;
  }
  
  console.log('  无需修复');
  return false;
}

// 清理测试缓存
function cleanTestCache() {
  console.log('清理测试缓存...');
  
  const cacheDirs = [
    '.pytest_cache',
    '.vitest',
    'node_modules/.vite',
    'test-results'
  ];
  
  let cleaned = false;
  
  for (const cacheDir of cacheDirs) {
    const fullPath = path.join(__dirname, cacheDir);
    if (fs.existsSync(fullPath)) {
      console.log(`  删除: ${cacheDir}`);
      try {
        fs.rmSync(fullPath, { recursive: true, force: true });
        cleaned = true;
      } catch (err) {
        console.log(`  删除失败: ${err.message}`);
      }
    }
  }
  
  return cleaned;
}

// 主函数
async function main() {
  console.log('开始修复前端测试问题...\n');
  
  // 1. 清理缓存
  cleanTestCache();
  
  // 2. 查找并修复测试文件
  console.log('\n查找测试文件...');
  const testFiles = findTestFiles(TEST_DIR);
  console.log(`找到 ${testFiles.length} 个测试文件\n`);
  
  let fixedCount = 0;
  
  for (const file of testFiles) {
    try {
      if (fixFile(file)) {
        fixedCount++;
      }
    } catch (err) {
      console.log(`  错误处理文件 ${file}: ${err.message}`);
    }
  }
  
  // 3. 修复 vitest.setup.js 中的重复注册问题
  const setupFile = path.join(__dirname, 'src/tests/setup.js');
  if (fs.existsSync(setupFile)) {
    console.log('\n检查 vitest.setup.js...');
    let setupContent = fs.readFileSync(setupFile, 'utf8');
    
    // 检查是否有多余的Element Plus注册
    if (setupContent.includes('app.use(ElementPlus)')) {
      console.log('  警告: setup.js 中包含 ElementPlus 注册，可能重复注册');
    }
  }
  
  console.log(`\n修复完成。共检查 ${testFiles.length} 个文件，修复了 ${fixedCount} 个文件。`);
  console.log('\n建议下一步:');
  console.log('1. 运行测试: npm run test:run');
  console.log('2. 如果仍有问题，检查控制台输出并针对性修复');
  console.log('3. 考虑更新测试配置确保正确模拟依赖项');
}

// 执行主函数
main().catch(err => {
  console.error('修复过程中发生错误:', err);
  process.exit(1);
});