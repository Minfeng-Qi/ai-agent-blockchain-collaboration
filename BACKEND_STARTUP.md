# LLM区块链后端启动指南

## 🚀 一键启动后端

根据你的Ganache设置，选择合适的启动方式：

### 方式1: 自动启动Ganache + 后端 (完全自动化)
```bash
./start_backend.sh
```
**适用场景**: 
- 没有运行Ganache
- 希望脚本自动管理整个环境

**包含功能**:
- ✅ 自动启动Ganache (ChainID: 5777)
- ✅ 部署所有智能合约
- ✅ 启动后端API服务
- ✅ 自动配置合约地址

### 方式2: 连接外部Ganache + 后端 (推荐)
```bash
./start_backend_external_ganache.sh
```
**适用场景**:
- 已经启动了自己的Ganache客户端
- Ganache ChainID为5777或1337
- 希望保持对Ganache的完全控制

**包含功能**:
- ✅ 连接到外部Ganache
- ✅ 部署所有智能合约
- ✅ 启动后端API服务
- ✅ 自动配置合约地址

## 🛑 停止服务

### 停止完整后端系统 (包括Ganache)
```bash
./stop_backend.sh
```

### 仅停止后端服务 (保留外部Ganache)
```bash
./stop_backend_only.sh
```

## 🔧 通过quick_start.sh启动

你也可以使用交互式启动脚本：
```bash
./quick_start.sh
```
然后选择:
- **选项4**: 仅启动后端 (一键启动，推荐)

## 📋 启动后的服务信息

启动成功后，你可以访问：

- **后端API**: http://localhost:8001
- **API文档**: http://localhost:8001/docs
- **健康检查**: http://localhost:8001/health
- **系统统计**: http://localhost:8001/stats

## 🔍 验证启动状态

### 检查服务状态
```bash
# 检查后端健康状态
curl http://localhost:8001/health

# 检查API根路径
curl http://localhost:8001/

# 检查智能体列表
curl http://localhost:8001/agents/

# 检查任务列表
curl http://localhost:8001/tasks/
```

### 检查进程状态
```bash
# 查看后端进程
ps aux | grep uvicorn

# 查看Ganache进程 (如果自动启动)
ps aux | grep ganache

# 检查端口占用
lsof -i :8001 -i :8545
```

## 🚨 故障排除

### 问题1: 无法连接到Ganache
```bash
# 检查Ganache是否运行
curl http://localhost:8545

# 检查ChainID
curl -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' \
  http://localhost:8545
```

### 问题2: 合约部署失败
**原因**: Ganache账户余额不足
**解决**: 确保Ganache启动时设置了足够余额：
```bash
ganache --defaultBalanceEther 1000
```

### 问题3: 后端启动失败
```bash
# 查看后端日志
tail -f backend/backend.log

# 检查Python环境
source backend/venv/bin/activate
pip install -r backend/requirements.txt
```

### 问题4: 端口被占用
```bash
# 查看端口占用
lsof -i :8001
lsof -i :8545

# 强制停止服务
pkill -f uvicorn
pkill -f ganache
```

## 📁 文件结构

启动脚本文件：
```
├── start_backend.sh                    # 完整后端启动 (含Ganache)
├── start_backend_external_ganache.sh   # 连接外部Ganache
├── stop_backend.sh                     # 停止完整系统
├── stop_backend_only.sh                # 仅停止后端
├── quick_start.sh                      # 交互式启动脚本
└── BACKEND_STARTUP.md                  # 本文档
```

## 💡 最佳实践

1. **开发环境**: 使用 `start_backend_external_ganache.sh`，手动管理Ganache
2. **测试环境**: 使用 `start_backend.sh`，让脚本管理整个环境
3. **生产环境**: 参考这些脚本配置相应的服务

## 🔄 重启流程

如需重启整个后端系统：
```bash
# 方式1: 使用对应的停止脚本
./stop_backend_only.sh
./start_backend_external_ganache.sh

# 方式2: 直接重新运行启动脚本 (会自动停止现有服务)
./start_backend_external_ganache.sh
```