# LLM区块链项目完整启动指南

## 📋 目录
1. [前置条件](#前置条件)
2. [启动步骤](#启动步骤)
3. [常见问题解决](#常见问题解决)
4. [服务验证](#服务验证)
5. [管理命令](#管理命令)
6. [故障排除](#故障排除)

## 🔧 前置条件

### 1. 环境要求
- **Node.js** (v18+)
- **Python** (v3.8+)
- **Ganache客户端** (推荐使用Ganache GUI)
- **Git**
- **curl** 和 **jq** (用于脚本验证)

### 2. 目录结构确认
```
llm-blockchain/code/
├── backend/
│   ├── venv/
│   ├── main.py
│   ├── requirements.txt
│   └── services/contract_service.py
├── contracts-clean/
│   ├── node_modules/
│   ├── package.json
│   └── scripts/deploy.js
├── frontend/
│   ├── node_modules/
│   ├── package.json
│   └── src/
└── start_backend_external_ganache.sh
```

## 🚀 启动步骤

### 步骤1：启动Ganache
1. 打开Ganache GUI客户端
2. 创建新的工作空间或打开现有工作空间
3. 确保配置：
   - **端口**: 8545
   - **网络ID**: 5777 (或 1377)
   - **账户**: 至少10个账户，每个账户有100 ETH
   - **Gas限制**: 6721975
   - **Gas价格**: 20000000000

### 步骤2：验证Ganache连接
```bash
# 检查Ganache是否运行
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' \
  http://localhost:8545
# 应该返回: {"id":1,"jsonrpc":"2.0","result":"0x539"} 或 {"id":1,"jsonrpc":"2.0","result":"0x1691"}
```

### 步骤3：检查依赖环境
```bash
# 检查Python虚拟环境
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# 检查合约依赖
cd ../contracts-clean
if [ ! -d "node_modules" ]; then
    npm install
fi
```

### 步骤4：启动后端服务
```bash
# 方法1：使用改进的启动脚本
./start_backend.sh

# 方法2：手动启动（如果脚本失败）
cd backend
source venv/bin/activate
python -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```

### 步骤5：验证服务状态
```bash
# 检查后端健康状态
curl -s http://localhost:8001/health | jq

# 期望输出：
{
  "status": "healthy",
  "services": {
    "api": "up",
    "blockchain": "up"
  },
  "blockchain_details": {
    "connected": true,
    "network_id": 1337,
    "latest_block": 11,
    "contracts": {
      "agent_registry": true,
      "task_manager": true,
      "learning": true
    }
  }
}
```

### 步骤6：启动前端服务 (可选)
```bash
cd frontend
npm start
# 前端将在 http://localhost:3000 启动
```

## ⚠️ 常见问题解决

### 问题1：合约部署失败
**症状**: 部署脚本报错或合约地址为空
**解决方案**:
```bash
# 1. 确保Ganache正在运行
curl -s http://localhost:8545

# 2. 检查Ganache账户余额
# 3. 重新启动Ganache
# 4. 清除并重新部署
cd contracts-clean
rm -rf artifacts/ cache/
npx hardhat run scripts/deploy.js --network localhost
```

### 问题2：后端服务无法连接区块链
**症状**: `/health` 接口显示 `"blockchain": "down"`
**解决方案**:
```bash
# 1. 检查 backend/services/contract_service.py 文件语法
python -m py_compile services/contract_service.py

# 2. 确保合约地址格式正确
# 3. 重启后端服务
pkill -f "uvicorn.*main:app"
cd backend
source venv/bin/activate
python -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```

### 问题3：端口被占用
**症状**: `Address already in use` 错误
**解决方案**:
```bash
# 查找并杀死占用端口的进程
lsof -ti:8001 | xargs kill -9  # 后端端口
lsof -ti:8545 | xargs kill -9  # Ganache端口
lsof -ti:3000 | xargs kill -9  # 前端端口
```

### 问题4：启动脚本卡住
**症状**: 脚本在某个步骤停止响应
**解决方案**:
```bash
# 使用 Ctrl+C 停止脚本，然后手动执行步骤
# 或者使用改进的启动脚本（见下方优化部分）
```

## 🔍 服务验证

### 1. 后端API测试
```bash
# 基本连接测试
curl -s http://localhost:8001/

# 健康检查
curl -s http://localhost:8001/health

# 获取代理列表
curl -s http://localhost:8001/agents/

# 获取任务列表
curl -s http://localhost:8001/tasks/
```

### 2. 区块链连接测试
```bash
# 检查区块链统计
curl -s http://localhost:8001/blockchain/stats

# 查看区块信息
curl -s http://localhost:8001/blockchain/blocks?limit=5
```

### 3. 前端测试
- 打开浏览器访问 http://localhost:3000
- 检查是否能看到仪表板
- 验证数据是否正确加载

## 🛠️ 管理命令

### 启动服务
```bash
# 启动后端（连接外部Ganache）
./start_backend_external_ganache.sh

# 启动前端
cd frontend && npm start
```

### 停止服务
```bash
# 停止后端
./stop_backend_only.sh
# 或者
pkill -f "uvicorn.*main:app"

# 停止前端
pkill -f "npm start"
```

### 重启服务
```bash
# 重启后端
./stop_backend_only.sh
./start_backend_external_ganache.sh

# 重启前端
pkill -f "npm start"
cd frontend && npm start
```

### 查看日志
```bash
# 后端日志
tail -f backend/backend.log

# 前端日志（如果有）
tail -f frontend/frontend.log
```

## 🔧 故障排除

### 1. 完全重置环境
```bash
# 停止所有服务
pkill -f "uvicorn"
pkill -f "npm start"

# 清理缓存
cd contracts-clean
rm -rf artifacts/ cache/

# 重新部署合约
npx hardhat run scripts/deploy.js --network localhost

# 重新启动后端
cd ../backend
source venv/bin/activate
python -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```

### 2. 检查依赖
```bash
# 检查Python依赖
cd backend
source venv/bin/activate
pip list

# 检查Node.js依赖
cd ../contracts-clean
npm list --depth=0

cd ../frontend
npm list --depth=0
```

### 3. 环境变量检查
```bash
# 检查Python版本
python3 --version

# 检查Node.js版本
node --version
npm --version

# 检查虚拟环境
which python  # 应该指向 venv/bin/python
```

## 📊 服务状态监控

### 持续监控脚本
```bash
#!/bin/bash
# 创建 monitor.sh 文件
echo "监控服务状态..."

while true; do
    echo "$(date): 检查服务状态"
    
    # 检查后端
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo "✅ 后端服务正常"
    else
        echo "❌ 后端服务异常"
    fi
    
    # 检查Ganache
    if curl -s http://localhost:8545 > /dev/null 2>&1; then
        echo "✅ Ganache正常"
    else
        echo "❌ Ganache异常"
    fi
    
    echo "---"
    sleep 30
done
```

## 🎯 快速启动检查清单

启动前请确认：
- [ ] Ganache客户端已启动并运行在8545端口
- [ ] Python虚拟环境已创建并激活
- [ ] Node.js依赖已安装
- [ ] 端口8001和8545未被占用
- [ ] 网络连接正常

启动后验证：
- [ ] `curl http://localhost:8001/health` 返回健康状态
- [ ] 区块链连接状态为 `"blockchain": "up"`
- [ ] 所有合约状态为 `true`
- [ ] API文档可访问: http://localhost:8001/docs

## 📝 注意事项

1. **Ganache必须先启动**: 后端服务依赖Ganache连接
2. **合约地址自动更新**: 每次部署后会自动更新合约地址
3. **开发模式**: 使用`--reload`参数，代码更改会自动重启
4. **日志监控**: 定期检查日志文件排除问题
5. **端口冲突**: 确保所需端口未被占用

## 🆘 紧急恢复

如果遇到严重问题，请按以下步骤恢复：

1. **完全停止所有服务**
2. **重启Ganache** (清除所有数据)
3. **删除合约artifacts**
4. **重新部署合约**
5. **重新启动后端服务**

这个过程通常可以解决95%的启动问题。