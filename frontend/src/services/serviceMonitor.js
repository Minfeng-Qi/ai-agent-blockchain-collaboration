/**
 * 服务监控器 - 负责检测后端服务状态并管理自动回退
 */

class ServiceMonitor {
  constructor() {
    this.backendAvailable = null; // null表示未知，true表示可用，false表示不可用
    this.lastCheckTime = null;
    this.checkInterval = 30000; // 30秒检查一次
    this.intervalId = null;
    this.listeners = new Set(); // 状态变化监听器
    
    // 立即执行一次检查
    this.checkServiceStatus();
    
    // 启动定期检查
    this.startPeriodicCheck();
  }

  /**
   * 检查后端服务状态
   */
  async checkServiceStatus() {
    try {
      // 设置较短的超时时间来快速判断服务是否可用
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000); // 3秒超时
      
      const response = await fetch('http://localhost:8001/health', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        const data = await response.json();
        const newStatus = data.status === 'healthy';
        this.updateServiceStatus(newStatus);
        return newStatus;
      } else {
        this.updateServiceStatus(false);
        return false;
      }
    } catch (error) {
      // 网络错误、超时等都视为服务不可用
      console.warn('Backend service check failed:', error.message);
      this.updateServiceStatus(false);
      return false;
    }
  }

  /**
   * 更新服务状态
   */
  updateServiceStatus(isAvailable) {
    const previousStatus = this.backendAvailable;
    this.backendAvailable = isAvailable;
    this.lastCheckTime = Date.now();
    
    // 如果状态发生变化，通知所有监听器
    if (previousStatus !== isAvailable) {
      console.log(`Backend service status changed: ${previousStatus} -> ${isAvailable}`);
      this.notifyListeners(isAvailable, previousStatus);
    }
  }

  /**
   * 启动定期检查
   */
  startPeriodicCheck() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
    
    this.intervalId = setInterval(() => {
      this.checkServiceStatus();
    }, this.checkInterval);
  }

  /**
   * 停止定期检查
   */
  stopPeriodicCheck() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  /**
   * 添加状态变化监听器
   */
  addStatusListener(callback) {
    this.listeners.add(callback);
    
    // 如果已经有状态信息，立即调用回调
    if (this.backendAvailable !== null) {
      callback(this.backendAvailable, null);
    }
    
    // 返回移除监听器的函数
    return () => {
      this.listeners.delete(callback);
    };
  }

  /**
   * 通知所有监听器
   */
  notifyListeners(currentStatus, previousStatus) {
    this.listeners.forEach(callback => {
      try {
        callback(currentStatus, previousStatus);
      } catch (error) {
        console.error('Error in service status listener:', error);
      }
    });
  }

  /**
   * 获取当前服务状态
   */
  isBackendAvailable() {
    return this.backendAvailable === true;
  }

  /**
   * 强制刷新服务状态
   */
  async refreshStatus() {
    return await this.checkServiceStatus();
  }

  /**
   * 获取服务状态信息
   */
  getStatusInfo() {
    return {
      available: this.backendAvailable,
      lastCheck: this.lastCheckTime,
      checkInterval: this.checkInterval
    };
  }

  /**
   * 设置检查间隔
   */
  setCheckInterval(interval) {
    this.checkInterval = interval;
    this.startPeriodicCheck(); // 重启定期检查
  }

  /**
   * 销毁监控器
   */
  destroy() {
    this.stopPeriodicCheck();
    this.listeners.clear();
  }
}

// 创建全局单例
export const serviceMonitor = new ServiceMonitor();

// 导出类以便测试
export { ServiceMonitor };