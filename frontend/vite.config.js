import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import path from 'node:path'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  appType: 'spa',
  base: '/',
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      devOptions: {
        enabled: false  // 在开发阶段完全禁用PWA，避免各种PWA相关错误
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],  // 移除了对pwa相关图片的引用
      }
    })
  ],
  css: {
    preprocessorOptions: {
      scss: {
        // additionalData removed to avoid duplicate imports
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      '@/components': path.resolve(__dirname, 'src/components'),
      '@/views': path.resolve(__dirname, 'src/views'),
      '@/api': path.resolve(__dirname, 'src/api'),
      '@/utils': path.resolve(__dirname, 'src/utils'),
      '@/styles': path.resolve(__dirname, 'src/styles'),
      '@/layout': path.resolve(__dirname, 'src/layout'),
      '@/router': path.resolve(__dirname, 'src/router'),
      '@/stores': path.resolve(__dirname, 'src/stores'),
      '@/config': path.resolve(__dirname, 'src/config'),
    },
  },
  server: {
    port: 3000,
    host: '0.0.0.0',
    strictPort: false,
    strict: false,
    open: true,
    hmr: {
      overlay: true,
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // 后端FastAPI服务地址
        changeOrigin: true,
        secure: false,
      },
      '/ws': {  // WebSocket连接代理
        target: 'http://localhost:8000',
        changeOrigin: true,
        ws: true,
      },
      // AI_WORKING: coder1 @2026-01-29T12:00 - 禁用/admin代理规则避免前端路由被代理
      // 添加对admin路径的WebSocket代理支持（已禁用，避免前端路由被代理）
      // '/admin': {
      //   target: 'http://localhost:8000',
      //   changeOrigin: true,
      //   ws: true  // 支持WebSocket连接
      // }
      // AI_DONE: coder1 @2026-01-29T12:00
    },
    fs: {
      allow: [path.resolve(__dirname)]
    }
  },
  define: {
    __APP_VERSION__: JSON.stringify('1.0.0'),
  }
})