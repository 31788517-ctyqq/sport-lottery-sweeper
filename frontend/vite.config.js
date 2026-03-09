import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import { resolve } from 'path'

const apiProxyTarget = process.env.VITE_API_PROXY_TARGET || 'http://localhost:8000'

// https://vitejs.dev/config/
export default defineConfig({
  root: __dirname,
  appType: 'spa',
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png'],
      workbox: {
        navigateFallbackAllowlist: [/^\/$/, /^\/admin(?:\/.*)?$/, /^\/m(?:\/.*)?$/]
      },
      devOptions: {
        enabled: true,
        navigateFallbackAllowlist: [/^\/$/, /^\/admin(?:\/.*)?$/, /^\/m(?:\/.*)?$/]
      },
      manifest: {
        name: '体育彩票扫盘系统',
        short_name: '体育扫盘系统',
        description: '用于体育彩票数据分析和智能扫盘的管理系统',
        start_url: '/',
        display: 'standalone',
        background_color: '#ffffff',
        theme_color: '#409eff',
        icons: [
          {
            src: '/favicon.ico',
            sizes: '64x64 32x32 24x24 16x16',
            type: 'image/x-icon'
          }
        ]
      }
    })
  ],
  server: {
    port: 3000,
    host: '0.0.0.0',
    strict: false, // 启用历史 API 回退，对于 SPA 应用
    fs: {
      allow: [
        // 允许访问前端目录
        process.cwd(),
        // 允许访问项目根目录
        resolve(__dirname, '..'),
      ]
    },
    proxy: {
      '/api/v1': {
        target: apiProxyTarget,
        changeOrigin: true
      },
      '/api': {
        target: apiProxyTarget,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api/v1')
      }
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),      // 配置@符号指向src目录
    }
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@use "@/styles/variables.css" as *;`  // 全局CSS变量
      }
    }
  }
})
