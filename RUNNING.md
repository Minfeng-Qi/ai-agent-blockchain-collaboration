# 运行 Agent Learning System

本文档提供了在本地开发环境中运行 Agent Learning System 的详细说明。

## 环境要求

- Python 3.9+
- Node.js 18.x
- IPFS 0.35.0+ (自动安装和管理)
- MongoDB (可选，目前可以不使用)
- Homebrew (macOS) 或其他包管理器

## 安装步骤

### 1. 设置 Node.js 18.x

如果您使用 nvm (Node Version Manager)，可以运行以下命令：

```bash
nvm install 18
nvm use 18
```

或者直接从 [Node.js 官网](https://nodejs.org/) 下载并安装 Node.js 18.x 版本。

### 2. 创建 Python 虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# 在 macOS/Linux 上：
source venv/bin/activate
# 在 Windows 上：
# venv\Scripts\activate
```

### 3. 安装依赖

运行提供的安装脚本：

```bash
# 添加执行权限
chmod +x setup_dev_env.sh

# 运行安装脚本
./setup_dev_env.sh
```

或者手动安装依赖：

```bash
# 安装后端依赖
cd backend
pip install -r requirements.txt
cd ..

# 安装前端依赖
cd frontend
npm install
cd ..

# 安装项目根目录依赖
npm install
```

### 4. 配置环境变量

复制示例环境变量文件并根据需要进行修改：

```bash
cp .env.example .env
```

## 运行项目

### 方法 1：使用启动脚本

我们提供了便捷的启动脚本来运行整个项目：

```bash
# 确保 Python 虚拟环境已激活
source venv/bin/activate

# 运行开发环境
chmod +x start_dev.sh
./start_dev.sh
```

这将自动执行以下操作：
1. 检查并启动 IPFS 服务
2. 启动 Ganache 本地区块链
3. 部署智能合约
4. 启动后端服务
5. 启动前端服务

脚本会自动处理 IPFS 版本兼容性问题，如果检测到版本过低会自动升级。

### 方法 2：使用 npm 脚本

```bash
# 确保 Python 虚拟环境已激活
source venv/bin/activate

# 使用 npm 脚本启动所有服务
npm run dev
```

### 方法 3：分步启动

如果您想分步启动各个组件，可以按照以下步骤操作：

1. 启动 IPFS 服务：

```bash
# 检查 IPFS 是否已安装
ipfs version

# 如果未安装，使用 Homebrew 安装
brew install ipfs

# 初始化 IPFS（首次使用）
ipfs init

# 启动 IPFS daemon
ipfs daemon
```

2. 启动 Ganache 本地区块链：

```bash
npx ganache --port 8545 --chain.chainId 1337
```

3. 部署智能合约：

```bash
npx hardhat run contracts/scripts/deploy.js --network ganache
```

4. 启动后端服务：

```bash
# 确保 Python 虚拟环境已激活
source venv/bin/activate
python run_backend.py
```

5. 启动前端服务：

```bash
cd frontend
npm start
```

## 验证服务是否正常运行

### IPFS 服务

访问以下 URL 检查 IPFS 服务是否正常运行：

- IPFS Web UI：http://127.0.0.1:5001/webui
- IPFS API：http://127.0.0.1:5001/api/v0/id
- IPFS Gateway：http://127.0.0.1:8081/

### 后端 API

访问以下 URL 检查后端 API 是否正常运行：

- API 状态：http://localhost:8000/
- 健康检查：http://localhost:8000/health
- API 文档：http://localhost:8000/docs

### 前端

前端应用将在以下地址运行：

- http://localhost:3000

### 区块链服务

检查 Ganache 是否正常运行：

- Ganache RPC：http://127.0.0.1:8545
- 网络 ID：1337

## 常见问题

### 1. IPFS 相关问题

**IPFS 启动失败**：
- 检查 IPFS 版本：`ipfs version`
- 如果版本过低，升级 IPFS：`brew upgrade ipfs`
- 检查日志文件：`cat ipfs.log`

**IPFS 仓库版本不兼容**：
- 错误信息：`Your programs version (X) is lower than your repos (Y)`
- 解决方法：升级 IPFS 到最新版本

**IPFS 端口冲突**：
- 默认端口：4001 (swarm), 5001 (API), 8081 (gateway)
- 如有冲突，可修改 IPFS 配置或停止占用端口的服务

### 2. Ganache 连接问题

如果遇到 Ganache 连接问题，请确保：

- Ganache 已正确启动（端口 8545）
- 环境变量 `WEB3_PROVIDER_URI` 设置为 `http://127.0.0.1:8545`

### 3. 智能合约部署失败

如果智能合约部署失败，请检查：

- Ganache 是否正在运行
- Hardhat 配置是否正确
- 合约编译是否有错误（运行 `npx hardhat compile` 检查）

### 4. Node.js 版本问题

如果收到 Node.js 版本相关的错误，请确保您使用的是 Node.js 18.x 版本：

```bash
node -v  # 应显示 v18.x.x
```

如果版本不正确，请使用 nvm 或重新安装正确的 Node.js 版本。

### 5. Python 依赖问题

如果遇到 Python 依赖相关的错误，请确保：

- 已激活 Python 虚拟环境
- 已安装所有必要的依赖（`pip install -r backend/requirements.txt`）

### 6. 服务启动顺序问题

建议按以下顺序启动服务：
1. IPFS daemon
2. Ganache 区块链
3. 智能合约部署
4. 后端服务
5. 前端服务

使用 `./start_dev.sh` 脚本可以自动按正确顺序启动所有服务。