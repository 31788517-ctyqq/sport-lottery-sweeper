import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';  // 导入路由

// 引入Element Plus
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import zhCn from 'element-plus/es/locale/lang/zh-cn';

// 引入全局样式 - 修正导入顺序和方式
import 'normalize.css/normalize.css';
import '../index.scss';  // 确保SCSS变量首先加载
import '@/styles/main-content.css';  // 然后加载主内容样式

// 创建Vue应用
const app = createApp(App);

// 创建Pinia实例
const pinia = createPinia();

// 使用插件
app.use(ElementPlus, { locale: zhCn });
app.use(pinia);
app.use(router);  // 使用路由

// 挂载应用
app.mount('#app');

// 挂载应用后再初始化WebSocket
// 使用动态导入确保Pinia已经安装
async function initWebSocket() {
  try {
    const { default: wsService } = await import('./services/websocket');
    wsService.connect();
  } catch (error) {
    console.warn('WebSocket服务初始化失败:', error.message);
  }
}

// 延迟初始化WebSocket,确保应用完全挂载
setTimeout(initWebSocket, 1000);

// 在应用卸载时断开WebSocket连接
window.addEventListener('beforeunload', () => {
  import('./services/websocket').then(ws => ws.default.disconnect());
});