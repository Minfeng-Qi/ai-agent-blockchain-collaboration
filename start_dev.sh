#!/bin/bash
# Start development environment for Agent Learning System

# Change to the project root directory
cd "$(dirname "$0")"

# Export PYTHONPATH to include the current directory
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Check if Python virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
  echo "Activating virtual environment..."
  if [ -d "venv" ]; then
    source venv/bin/activate
  else
    echo "Virtual environment not found. Creating one..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
  fi
else
  echo "Virtual environment already activated: $VIRTUAL_ENV"
fi

# 检查 IPFS 是否已安装
if ! command -v ipfs &> /dev/null; then
  echo "IPFS 未安装，正在尝试用 Homebrew 安装..."
  if command -v brew &> /dev/null; then
    brew install ipfs
  else
    echo "请手动安装 IPFS：https://docs.ipfs.tech/install/"
    exit 1
  fi
fi

# 检查 IPFS 版本并确保兼容性
IPFS_VERSION=$(ipfs version --number 2>/dev/null | cut -d. -f1,2)
if [ -n "$IPFS_VERSION" ]; then
  # 检查是否需要升级 IPFS
  if [ "$(printf '%s\n' "0.35" "$IPFS_VERSION" | sort -V | head -n1)" = "0.35" ] && [ "$IPFS_VERSION" != "0.35" ]; then
    echo "IPFS 版本过低 ($IPFS_VERSION)，正在升级到最新版本..."
    if command -v brew &> /dev/null; then
      brew upgrade ipfs
    else
      echo "请手动升级 IPFS：https://docs.ipfs.tech/install/"
      exit 1
    fi
  fi
fi

# 初始化 IPFS（如果还没初始化过）
if [ ! -d "$HOME/.ipfs" ]; then
  echo "正在初始化 IPFS..."
  ipfs init
fi

# 检查 IPFS 是否已在运行
if pgrep -f "ipfs daemon" > /dev/null; then
  echo "IPFS daemon 已在运行"
  IPFS_PID=$(pgrep -f "ipfs daemon")
else
  # 启动 IPFS daemon
  echo "启动 IPFS 服务..."
  ipfs daemon > ipfs.log 2>&1 &
  IPFS_PID=$!
  
  # 等待 IPFS 启动
  echo "等待 IPFS 服务启动..."
  sleep 3
  
  # 检查 IPFS 是否成功启动
  if ! pgrep -f "ipfs daemon" > /dev/null; then
    echo "IPFS 启动失败，请检查日志文件 ipfs.log"
    cat ipfs.log
    exit 1
  fi
  echo "IPFS 服务启动成功"
fi

# Check Node.js version
NODE_VERSION=$(node -v)
if [[ $NODE_VERSION != v18* ]]; then
  echo "Warning: Current Node.js version is $NODE_VERSION, but project requires v18.x"
  echo "Please install Node.js v18.x using nvm or another version manager"
  echo "Example: nvm install 18 && nvm use 18"
  exit 1
fi

# Start Ganache in background
echo "Starting Ganache local blockchain..."
npx ganache --port 8545 --chain.chainId 1337 --detach

# Wait for Ganache to start
sleep 2

# Deploy contracts
echo "Deploying smart contracts to local blockchain..."
npx hardhat run contracts/scripts/deploy.js --network ganache

# Start backend
echo "Starting backend server..."
python run_backend.py &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!

# Function to kill processes on exit
cleanup() {
  echo "Shutting down servers..."
  kill $BACKEND_PID
  kill $FRONTEND_PID
  kill $IPFS_PID
  echo "IPFS daemon stopped."
  exit 0
}

# Register the cleanup function for SIGINT and SIGTERM signals
trap cleanup SIGINT SIGTERM

# Keep the script running
echo "Development environment started. Press Ctrl+C to stop."
wait