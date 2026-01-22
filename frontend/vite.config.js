import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { createSvgIconsPlugin } from 'vite-plugin-svg-icons'
// import { VitePWA } from 'vite-plugin-pwa'  // 暂时注释掉PWA插件
// import compression from 'vite-plugin-compression'  // 暂时注释掉压缩插件

// 添加代理配置
export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    // 项目根目录 - 使用相对路径
    root: './',
    
    // 基础路径
    base: '/',
    
    // 插件
    plugins: [
      vue(),
      createSvgIconsPlugin({
        iconDirs: [resolve(process.cwd(), 'src/assets/icons')],
        symbolId: 'icon-[dir]-[name]',
        inject: 'body-last',
        customDomId: '__svg__icons__dom__'
      }),
      // VitePWA({
      //   registerType: 'autoUpdate',
      //   includeAssets: ['favicon.ico', 'robots.txt', 'apple-touch-icon.png'],
      //   manifest: {
      //     name: '竞彩足球扫盘系统',
      //     short_name: '足球扫盘',
      //     theme_color: '#1e40af',
      //     icons: [
      //       {
      //         src: '/pwa-192x192.png',
      //         sizes: '192x192',
      //         type: 'image/png'
      //       },
      //       {
      //         src: '/pwa-512x512.png',
      //         sizes: '512x512',
      //         type: 'image/png'
      //       }
      //     ]
      //   },
      //   workbox: {
      //     globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
      //     runtimeCaching: [
      //       {
      //         urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
      //         handler: 'CacheFirst',
      //         options: {
      //           cacheName: 'google-fonts-cache',
      //           expiration: {
      //             maxEntries: 10,
      //             maxAgeSeconds: 60 * 60 * 24 * 365 // 一年
      //           },
      //           cacheableResponse: {
      //             statuses: [0, 200]
      //           }
      //         }
      //       }
      //     ]
      //   }
      // }),
      // compression({
      //   algorithm: 'gzip',
      //   ext: '.gz',
      //   threshold: 10240,
      //   deleteOriginFile: false
      // })
    ],
    
    // 禁用PostCSS以避免解析错误
    css: {
      postcss: false
    },
    
    // 解析配置
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
        '@components': resolve(__dirname, 'src/components'),
        '@views': resolve(__dirname, 'src/views'),
      }
    },
    
    // 服务器配置
    server: {
      host: '0.0.0.0',
      port: 3000,
      open: true,
      cors: true,
      // 修正重写规则，将 /api 路径重写为 /api/v1
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '/api/v1')  // 修正重写规则
        },
        '/ws': {
          target: env.VITE_WS_BASE_URL || 'ws://localhost:8000',
          ws: true,
          changeOrigin: true
        }
      },
      hmr: {
        overlay: true
      }
    }
  }
})