// Smart Data Service - 智能数据服务
// 自动检测后端状态并在真实数据和mock数据之间切换

import { enhancedMockData } from './enhancedMockData';
import { api } from './api';

class SmartDataService {
  constructor() {
    this.isBackendOnline = false;
    this.lastCheckTime = 0;
    this.checkInterval = 30000; // 30秒检查一次
    this.cache = new Map();
    this.cacheExpiry = 5000; // 5秒缓存
    this.listeners = new Set();
    
    // 初始化时检查后端状态
    this.checkBackendStatus();
    
    // 定期检查后端状态
    setInterval(() => {
      this.checkBackendStatus();
    }, this.checkInterval);
  }

  // 添加状态变化监听器
  addStatusListener(callback) {
    this.listeners.add(callback);
    return () => this.listeners.delete(callback);
  }

  // 通知所有监听器状态变化
  notifyStatusChange(status) {
    this.listeners.forEach(callback => {
      try {
        callback(status);
      } catch (error) {
        console.error('Error notifying status listener:', error);
      }
    });
  }

  // 检查后端状态
  async checkBackendStatus() {
    try {
      const response = await fetch('http://localhost:8000/health', {
        method: 'GET',
        timeout: 5000,
        signal: AbortSignal.timeout(5000)
      });
      
      const wasOnline = this.isBackendOnline;
      this.isBackendOnline = response.ok;
      
      if (wasOnline !== this.isBackendOnline) {
        console.log(`Backend status changed: ${this.isBackendOnline ? 'Online' : 'Offline'}`);
        this.notifyStatusChange({
          isOnline: this.isBackendOnline,
          timestamp: new Date().toISOString()
        });
      }
      
      this.lastCheckTime = Date.now();
      return this.isBackendOnline;
    } catch (error) {
      const wasOnline = this.isBackendOnline;
      this.isBackendOnline = false;
      
      if (wasOnline !== this.isBackendOnline) {
        console.log('Backend is offline:', error.message);
        this.notifyStatusChange({
          isOnline: this.isBackendOnline,
          timestamp: new Date().toISOString(),
          error: error.message
        });
      }
      
      this.lastCheckTime = Date.now();
      return false;
    }
  }

  // 获取缓存的数据
  getCachedData(key) {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < this.cacheExpiry) {
      return cached.data;
    }
    return null;
  }

  // 设置缓存数据
  setCachedData(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
  }

  // 智能数据获取 - 根据后端状态自动选择数据源
  async getSmartData(endpoint, mockMethod, options = {}) {
    const cacheKey = `${endpoint}_${JSON.stringify(options)}`;
    
    // 先检查缓存
    if (!options.bypassCache) {
      const cached = this.getCachedData(cacheKey);
      if (cached) {
        return {
          data: cached,
          source: 'cache',
          isBackendOnline: this.isBackendOnline
        };
      }
    }

    // 如果需要强制检查后端状态
    if (options.forceStatusCheck || Date.now() - this.lastCheckTime > this.checkInterval) {
      await this.checkBackendStatus();
    }

    let data;
    let source;

    try {
      if (this.isBackendOnline) {
        // 尝试从后端获取数据
        const response = await api.get(endpoint, { timeout: 8000 });
        data = response.data;
        source = 'backend';
        
        // 缓存后端数据
        this.setCachedData(cacheKey, data);
      } else {
        throw new Error('Backend is offline');
      }
    } catch (error) {
      console.warn(`Failed to fetch from backend (${endpoint}):`, error.message);
      
      // 使用增强的mock数据
      if (typeof mockMethod === 'string') {
        data = enhancedMockData[mockMethod]();
      } else if (typeof mockMethod === 'function') {
        data = mockMethod();
      } else {
        data = mockMethod;
      }
      
      source = 'mock';
      
      // 标记后端为离线状态
      if (this.isBackendOnline) {
        this.isBackendOnline = false;
        this.notifyStatusChange({
          isOnline: false,
          timestamp: new Date().toISOString(),
          error: error.message
        });
      }
    }

    return {
      data,
      source,
      isBackendOnline: this.isBackendOnline,
      timestamp: new Date().toISOString()
    };
  }

  // Dashboard专用数据获取方法
  async getDashboardData() {
    const results = await Promise.allSettled([
      this.getSystemStatus(),
      this.getTaskStatusDistribution(),
      this.getAgentPerformanceData(),
      this.getTaskCompletionTrend(),
      this.getAgentCapabilitiesDistribution(),
      this.getEarningsAnalysis(),
      this.getRealTimeMetrics(),
      this.getAgentCapabilityRadar('top_agent')
    ]);

    const data = {};
    const methods = [
      'systemStatus', 'taskStatusDistribution', 'agentPerformance',
      'taskCompletionTrend', 'agentCapabilities', 'earningsAnalysis', 'realTimeMetrics', 'agentCapabilityRadar'
    ];

    results.forEach((result, index) => {
      if (result.status === 'fulfilled') {
        data[methods[index]] = result.value;
      } else {
        console.error(`Failed to fetch ${methods[index]}:`, result.reason);
        data[methods[index]] = { data: null, source: 'error', isBackendOnline: false };
      }
    });

    return {
      ...data,
      isBackendOnline: this.isBackendOnline,
      lastUpdate: new Date().toISOString()
    };
  }

  // 系统状态
  async getSystemStatus() {
    return this.getSmartData('/stats', 'getSystemStatus');
  }

  // 任务状态分布
  async getTaskStatusDistribution() {
    return this.getSmartData('/tasks/status-distribution', 'getTaskStatusDistribution');
  }

  // 代理表现数据
  async getAgentPerformanceData() {
    return this.getSmartData('/agents/performance', 'getAgentPerformanceData');
  }

  // 任务完成趋势
  async getTaskCompletionTrend() {
    return this.getSmartData('/tasks/completion-trend', 'getTaskCompletionTrend');
  }

  // 代理能力分布
  async getAgentCapabilitiesDistribution() {
    return this.getSmartData('/agents/capabilities-distribution', 'getAgentCapabilitiesDistribution');
  }

  // 收益分析
  async getEarningsAnalysis() {
    return this.getSmartData('/analytics/earnings', 'getEarningsAnalysis');
  }

  // 实时指标
  async getRealTimeMetrics() {
    return this.getSmartData('/real-time/metrics', 'getRealTimeTaskExecution');
  }

  // 学习事件
  async getLearningEvents() {
    return this.getSmartData('/learning/events', 'getLearningEvents');
  }

  // 网络活动热力图
  async getNetworkActivityHeatmap() {
    return this.getSmartData('/analytics/network-activity', 'getNetworkActivityHeatmap');
  }

  // 代理协作网络
  async getAgentCollaborationNetwork() {
    return this.getSmartData('/agents/collaboration-network', 'getAgentCollaborationNetwork');
  }

  // 质量评估指标
  async getQualityMetrics() {
    return this.getSmartData('/analytics/quality-metrics', 'getQualityMetrics');
  }

  // 预测分析
  async getPredictiveAnalytics() {
    return this.getSmartData('/analytics/predictive', 'getPredictiveAnalytics');
  }

  // 代理能力雷达图
  async getAgentCapabilityRadar(agentId) {
    return this.getSmartData(`/agents/${agentId}/capability-radar`, 
      () => enhancedMockData.getAgentCapabilityRadar(agentId));
  }

  // 智能合约交互数据
  async getContractInteractions() {
    return this.getSmartData('/blockchain/contract-interactions', 'getContractInteractions');
  }

  // 数据融合 - 当后端在线时，将实时数据与mock数据融合
  async getFusedData(endpoint, mockMethod, fusionStrategy = 'replace') {
    const result = await this.getSmartData(endpoint, mockMethod);
    
    if (result.source === 'backend' && fusionStrategy === 'enhance') {
      // 增强策略：用mock数据填充缺失的字段
      const mockData = typeof mockMethod === 'string' 
        ? enhancedMockData[mockMethod]() 
        : (typeof mockMethod === 'function' ? mockMethod() : mockMethod);
      
      result.data = this.enhanceWithMockData(result.data, mockData);
    }
    
    return result;
  }

  // 用mock数据增强实际数据
  enhanceWithMockData(realData, mockData) {
    if (Array.isArray(realData) && Array.isArray(mockData)) {
      // 如果实际数据较少，用mock数据填充
      if (realData.length < mockData.length) {
        const additional = mockData.slice(realData.length);
        return [...realData, ...additional];
      }
    } else if (typeof realData === 'object' && typeof mockData === 'object') {
      // 合并对象，优先使用实际数据
      return { ...mockData, ...realData };
    }
    
    return realData;
  }

  // 清理资源
  destroy() {
    this.listeners.clear();
    this.cache.clear();
  }
}

// 创建单例实例
export const smartDataService = new SmartDataService();
export default smartDataService;