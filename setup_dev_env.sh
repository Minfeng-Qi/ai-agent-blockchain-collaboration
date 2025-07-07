#!/bin/bash
# Setup development environment for Agent Learning System

echo "Setting up development environment for Agent Learning System..."

# Check Node.js version
NODE_VERSION=$(node -v)
if [[ $NODE_VERSION != v18* ]]; then
  echo "Warning: Current Node.js version is $NODE_VERSION, but project requires v18.x"
  echo "Please install Node.js v18.x using nvm or another version manager"
  echo "Example: nvm install 18 && nvm use 18"
fi

# Install Ganache CLI
echo "Installing Ganache CLI..."
npm install -g ganache

# Install IPFS if not already installed
echo "Checking IPFS installation..."
if ! command -v ipfs &> /dev/null; then
  echo "Installing IPFS via Homebrew..."
  if command -v brew &> /dev/null; then
    brew install ipfs
  else
    echo "Homebrew not found. Please install IPFS manually:"
    echo "https://docs.ipfs.tech/install/"
    exit 1
  fi
else
  echo "IPFS already installed. Checking version..."
  IPFS_VERSION=$(ipfs version --number 2>/dev/null | cut -d. -f1,2)
  if [ -n "$IPFS_VERSION" ]; then
    if [ "$(printf '%s\n' "0.35" "$IPFS_VERSION" | sort -V | head -n1)" = "0.35" ] && [ "$IPFS_VERSION" != "0.35" ]; then
      echo "Upgrading IPFS to latest version..."
      brew upgrade ipfs
    fi
  fi
fi

# Initialize IPFS if not already done
if [ ! -d "$HOME/.ipfs" ]; then
  echo "Initializing IPFS..."
  ipfs init
fi

# Create Python virtual environment
echo "Creating Python virtual environment..."
python -m venv venv
source venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Install Hardhat and related dependencies
echo "Installing Hardhat and related dependencies..."
npm install --save-dev hardhat @nomiclabs/hardhat-ethers ethers@^5.0.0 @nomiclabs/hardhat-waffle ethereum-waffle chai

echo "Setup complete!"
echo ""
echo "To start the development environment, run:"
echo "./start_dev.sh"
echo ""
echo "Or manually start services:"
echo "1. Activate Python virtual environment: source venv/bin/activate"
echo "2. Start IPFS daemon: ipfs daemon"
echo "3. Start Ganache: npx ganache --port 8545 --chain.chainId 1337"
echo "4. Deploy contracts: npx hardhat run contracts/scripts/deploy.js --network ganache"
echo "5. Start backend: python run_backend.py"
echo "6. Start frontend: cd frontend && npm start"
echo ""
echo "IPFS Web UI will be available at: http://127.0.0.1:5001/webui"
echo "Frontend will be available at: http://localhost:3000"