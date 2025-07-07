# LLM区块链智能体学习系统

基于区块链的AI智能体任务管理和学习系统，支持智能体注册、任务分配、协作学习和激励机制。

## 🚀 快速开始

### 一键启动
```bash
./quick_start.sh
```

### 手动启动
详见 [启动指南](STARTUP_GUIDE.md)

## 📋 系统组件

- **前端** (React): http://localhost:3000
- **后端** (FastAPI): http://localhost:8001 
- **区块链** (Ganache): http://localhost:8545
- **智能合约**: 7个部署的合约

## 🏗️ 项目结构

```
llm-blockchain/
├── frontend/          # React前端应用
├── backend/           # FastAPI后端服务
├── contracts-clean/   # 智能合约源码
├── artifacts-clean/   # 编译后的合约ABI
├── scripts/           # 自动化脚本
├── quick_start.sh     # 快速启动脚本
└── STARTUP_GUIDE.md   # 详细启动指南
```

## 🔧 核心功能

### 智能合约
- **AgentRegistry**: 智能体注册管理
- **TaskManager**: 任务创建和分配
- **Learning**: 学习事件记录
- **IncentiveEngine**: 激励机制
- **BidAuction**: 竞价拍卖
- **MessageHub**: 消息通信
- **ActionLogger**: 行为日志

### 前端界面
- 📊 实时数据仪表板
- 🔍 区块链浏览器
- 👥 智能体管理
- 📝 任务管理
- 📈 学习可视化

### 后端API
- RESTful API接口
- 区块链数据集成
- 智能合约交互
- 实时数据获取

## 🛠️ 开发

### 启动开发环境
```bash
# 启动区块链和后端
echo "3" | ./quick_start.sh

# 启动前端开发服务器
cd frontend && npm start
```

### API文档
访问 http://localhost:8001/docs 查看完整API文档

## 📦 部署

### 合约部署
```bash
./scripts/auto_deploy.py
```

### 服务管理
```bash
./scripts/start_system.sh  # 启动所有服务
./scripts/stop_system.sh   # 停止所有服务
```

## 🔍 监控

- **区块链状态**: Ganache控制台
- **后端日志**: `tail -f backend.log`  
- **前端**: 浏览器开发者工具

## 📄 许可证

MIT License