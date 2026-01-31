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
    setupFiles: './src/tests/setup.js',
    include: ['src/**/*.{test,spec}.{js,ts,vue}'],
    exclude: ['node_modules', 'dist'],
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