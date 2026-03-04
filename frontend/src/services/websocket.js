import { useAppStore } from '../stores';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.store = null; // 延迟初始化store
    this.reconnectInterval = 10000; // 10秒重连间隔
    this.maxReconnectAttempts = 3; // 最多重连3次
    this.reconnectAttempts = 0;
    this.isConnecting = false; // 防止并发连接
  }

  getStore() {
    // 懒加载store,确保Pinia已安装
    if (!this.store) {
      try {
        this.store = useAppStore();
      } catch (error) {
        console.warn('无法获取store:', error.message);
        return null;
      }
    }
    return this.store;
  }

  connect() {
    try {
      // 防止重复连接
      if (this.isConnecting) {
        console.log('WebSocket正在连接中...');
        return;
      }

      // 检查是否需要连接WebSocket (仅当有后端服务时连接)
      if (!this.shouldConnect()) {
        console.log('WebSocket未启用,跳过连接');
        return;
      }

      // 确保store已初始化
      const store = this.getStore();
      if (!store) {
        console.warn('Store未初始化,WebSocket连接已跳过');
        return;
      }

      // AI_WORKING: coder1 @2026-01-28T03:30:00Z - 修复WebSocket硬编码端口
      this.isConnecting = true;
      this.socket = new WebSocket('/ws/matches');
      // AI_DONE: coder1 @2026-01-28T03:30:00Z

      this.socket.onopen = () => {
        console.log('✅ WebSocket连接已建立');
        this.reconnectAttempts = 0; // 连接成功，重置重连次数
        this.isConnecting = false;
      };

      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      };

      this.socket.onerror = (error) => {
        console.warn('⚠️  WebSocket连接失败 (后端WebSocket服务未启动，页面功能不受影响)');
        this.isConnecting = false;
      };

      this.socket.onclose = () => {
        this.isConnecting = false;
        
        // 尝试重连
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          console.log(`🔄 WebSocket将在 ${this.reconnectInterval/1000} 秒后重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
          setTimeout(() => {
            this.connect();
          }, this.reconnectInterval);
        } else {
          console.log('ℹ️  WebSocket已停止重连，应用将使用静态数据模式');
        }
      };
    } catch (error) {
      console.warn('WebSocket初始化失败:', error.message);
    }
  }

  shouldConnect() {
    // 如果是开发环境且没有明确的后端URL,则不连接WebSocket
    return !import.meta.env.DEV || window.location.hostname === 'localhost';
  }

  handleMessage(data) {
    // 处理接收到的数据
    console.log('收到WebSocket数据:', data);
    
    // 这里可以根据实际数据格式更新store中的数据
    if (data.type === 'match_update') {
      // 更新比赛数据
      this.updateMatchData(data.payload);
    } else if (data.type === 'intel_update') {
      // 更新情报数据
      this.updateIntelData(data.payload);
    } else {
      // 默认处理整个数据集
      this.updateAllData(data);
    }
  }

  updateMatchData(matchData) {
    const store = this.getStore();
    if (!store) return;

    // 更新store中的比赛数据
    const updatedMatches = store.matches.map(match => {
      if (match.id === matchData.id) {
        return { ...match, ...matchData };
      }
      return match;
    });

    store.matches = updatedMatches;
  }

  updateIntelData(intelData) {
    const store = this.getStore();
    if (!store) return;

    // 更新store中的情报数据
    if (store.intelligence[intelData.matchId]) {
      // 如果已有该比赛的情报，则更新
      store.intelligence[intelData.matchId] = [
        ...store.intelligence[intelData.matchId],
        intelData
      ];
    } else {
      // 否则创建新的情报数组
      store.intelligence[intelData.matchId] = [intelData];
    }
  }

  updateAllData(data) {
    const store = this.getStore();
    if (!store) return;

    // 如果数据是完整的比赛列表
    if (Array.isArray(data)) {
      // 更新整个比赛列表
      store.matches = data;
    } else {
      // 处理其他数据格式
      console.warn('未知的数据格式:', data);
    }
  }

  send(message) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    } else {
      console.error('WebSocket未连接，无法发送消息');
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

// 创建全局实例
const wsService = new WebSocketService();

export default wsService;