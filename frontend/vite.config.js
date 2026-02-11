import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'apple-touch-icon.png'],
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
    port: 3000,           // 设置默认端口为3000
    host: '0.0.0.0',      // 允许外部访问
    proxy: {              // 配置代理
      '/api': {
        target: 'http://127.0.0.1:8000',  // 修改后端API地址为正确的端口8000
        changeOrigin: true,
        // 保留/api前缀，因为后端路由是以/api开头的
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