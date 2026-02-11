import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'url'
import { dirname, resolve } from 'path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

// AI_WORKING: coder1 @2026-01-30 14:40:00 - 恢复jsdom环境和vue插件，验证globals
export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/tests/setup.js'],
    include: ['src/**/*.{test,spec}.{js,ts}', 'tests/**/*.{test,spec}.{js,ts}'],
    exclude: [
      'node_modules', 
      'dist',
      '**/*.md',           // 排除所有markdown文件
      '**/*.vue',         // 排除所有vue文件（除非在特定目录）
      'tests/e2e/**',     // 排除e2e测试目录
      'tests/unit/temp/**',  // 排除临时测试目录
      '**/backup/**',     // 排除备份目录
      '**/*.d.ts'         // 排除类型定义文件
    ],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html']
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@/components': resolve(__dirname, 'src/components'),
      '@/views': resolve(__dirname, 'src/views'),
      '@/api': resolve(__dirname, 'src/api'),
      '@/utils': resolve(__dirname, 'src/utils'),
      '@/styles': resolve(__dirname, 'src/styles'),
      '@/layout': resolve(__dirname, 'src/layout'),
      '@/router': resolve(__dirname, 'src/router'),
      '@/stores': resolve(__dirname, 'src/stores'),
      '@/config': resolve(__dirname, 'src/config')
    }
  },
  define: {
    __APP_VERSION__: JSON.stringify('1.0.0')
  }
})