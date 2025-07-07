# LLM区块链项目启动指南

## 项目概述
这是一个基于区块链的AI智能体学习系统，包含：
- **前端**: React应用 (端口: 3000)
- **后端**: FastAPI服务 (端口: 8001) 
- **区块链**: Ganache本地测试网 (端口: 8545)
- **智能合约**: 7个已部署的合约
- **IPFS**: 分布式存储 (端口: 5001)

## 快速启动

### 一键启动（推荐）
```bash
# 在项目根目录执行
./scripts/start_system.sh
```

### 只启动前端查看界面
```bash
# 如果只想看前端界面（使用模拟数据）
cd frontend && npm start
```

## 手动启动步骤

### 1. 启动Ganache区块链
```bash
npx ganache --host 0.0.0.0 --port 8545 --chain.chainId 1337 --accounts 10 --deterministic > ganache.log 2>&1 &
echo $! > ganache.pid
```

### 2. 部署智能合约
```bash
./scripts/auto_deploy.py
```

### 3. 启动后端API
```bash
# 确保虚拟环境已安装依赖
source backend/venv/bin/activate
pip install -r backend/requirements.txt

# 启动后端
backend/venv/bin/python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload > backend.log 2>&1 &
echo $! > backend.pid
```

### 4. 启动前端
```bash
cd frontend
npm install  # 首次运行需要
npm start
```

## 访问地址
- **前端界面**: http://localhost:3000
- **后端API文档**: http://localhost:8001/docs
- **区块链RPC**: http://localhost:8545

## 停止服务
```bash
./scripts/stop_system.sh
```

## 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 检查端口占用
   lsof -i :3000  # 前端
   lsof -i :8001  # 后端
   lsof -i :8545  # Ganache
   
   # 杀死进程
   kill -9 <PID>
   ```

2. **Ganache无法启动**
   ```bash
   # 确保Node.js已安装
   node --version
   npm --version
   
   # 全局安装Ganache
   npm install -g ganache
   ```

3. **后端启动失败**
   ```bash
   # 检查Python环境
   source backend/venv/bin/activate
   pip install -r backend/requirements.txt
   
   # 查看错误日志
   tail -f backend.log
   ```

4. **合约连接失败**
   ```bash
   # 重新部署合约
   ./scripts/auto_deploy.py
   ```

### 重置整个系统
```bash
# 停止所有服务
./scripts/stop_system.sh

# 清理进程文件
rm -f *.pid *.log

# 重新启动
./scripts/start_system.sh
```

## 项目结构
```
llm-blockchain/
├── frontend/          # React前端
├── backend/           # FastAPI后端
├── contracts/         # 智能合约源码
├── scripts/           # 自动化脚本
├── artifacts-clean/   # 编译后的合约ABI
└── README.md
```

## 开发指南

### 添加新智能合约
1. 在 `contracts/` 目录添加Solidity文件
2. 运行 `npx hardhat compile` 编译
3. 更新 `deploy.js` 部署脚本
4. 运行 `./scripts/auto_deploy.py` 重新部署

### 修改API接口
1. 编辑 `backend/routers/` 下的路由文件
2. 后端会自动重载（--reload 模式）

### 修改前端界面
1. 编辑 `frontend/src/` 下的组件文件
2. 前端会自动热重载

## 系统监控

### 查看服务状态
```bash
# 检查所有服务
ps aux | grep -E "(ganache|uvicorn|react-scripts)"

# 检查端口
netstat -an | grep -E "(3000|8001|8545)"
```

### 查看日志
```bash
tail -f ganache.log    # 区块链日志
tail -f backend.log    # 后端日志
```

## 数据状态

### 当前已部署的合约地址：
- AgentRegistry: 0xe78A0F7E598Cc8b0Bb87894B0F60dD2a88d6a8Ab
- ActionLogger: 0x5b1869D9A4C187F2EAa108f3062412ecf0526b24  
- IncentiveEngine: 0xCfEB869F69431e42cdB54A4F4f105C19C080A601
- TaskManager: 0xC89Ce4735882C9F0f0FE26686c53074E09B0D550
- BidAuction: 0xD833215cBcc3f914bD1C9ece3EE7BF8B14f841bb
- MessageHub: 0x0290FB167208Af455bB137780163b7B7a9a10C16
- Learning: 0x9b1f7F645351AF3631a656421eD2e40f2802E6c0

### 查看区块链数据
```bash
# 通过API查看
curl http://localhost:8001/blockchain/stats
curl http://localhost:8001/blockchain/transactions
```