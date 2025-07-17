# System Requirements

This document lists all system requirements and installation instructions for the LLM Blockchain project.

## System Dependencies

### 1. Node.js and npm
- **Version**: Node.js 18.x or higher
- **Installation**: 
  ```bash
  # macOS (using Homebrew)
  brew install node
  
  # Ubuntu/Debian
  curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
  sudo apt-get install -y nodejs
  
  # CentOS/RHEL
  curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
  sudo yum install -y nodejs
  ```

### 2. Python 3.8+
- **Version**: Python 3.8 or higher
- **Installation**:
  ```bash
  # macOS (using Homebrew)
  brew install python3
  
  # Ubuntu/Debian
  sudo apt-get update
  sudo apt-get install python3 python3-pip python3-venv
  
  # CentOS/RHEL
  sudo yum install python3 python3-pip
  ```

### 3. IPFS (InterPlanetary File System)
- **Version**: Kubo 0.35.0 or higher
- **Required for**: Decentralized storage of collaboration results

#### Installation Instructions:

##### macOS (using Homebrew):
```bash
brew install ipfs
```

##### Linux (Ubuntu/Debian):
```bash
# Download and install IPFS
wget https://dist.ipfs.tech/kubo/v0.35.0/kubo_v0.35.0_linux-amd64.tar.gz
tar -xzf kubo_v0.35.0_linux-amd64.tar.gz
cd kubo
sudo bash install.sh
```

##### Linux (CentOS/RHEL):
```bash
# Download and install IPFS
wget https://dist.ipfs.tech/kubo/v0.35.0/kubo_v0.35.0_linux-amd64.tar.gz
tar -xzf kubo_v0.35.0_linux-amd64.tar.gz
cd kubo
sudo bash install.sh
```

##### Windows:
1. Download the Windows installer from: https://dist.ipfs.tech/kubo/v0.35.0/kubo_v0.35.0_windows-amd64.zip
2. Extract and run the installer
3. Add IPFS to your PATH environment variable

#### IPFS Configuration:
After installation, initialize IPFS:
```bash
ipfs init
```

### 4. Git
- **Version**: Git 2.x or higher
- **Installation**:
  ```bash
  # macOS (using Homebrew)
  brew install git
  
  # Ubuntu/Debian
  sudo apt-get install git
  
  # CentOS/RHEL
  sudo yum install git
  ```

### 5. curl and jq
- **Required for**: API testing and JSON processing
- **Installation**:
  ```bash
  # macOS (using Homebrew)
  brew install curl jq
  
  # Ubuntu/Debian
  sudo apt-get install curl jq
  
  # CentOS/RHEL
  sudo yum install curl jq
  ```

## Ganache (Ethereum Development Network)

### Option 1: Ganache CLI (Recommended)
```bash
npm install -g ganache-cli
```

### Option 2: Ganache GUI
Download from: https://trufflesuite.com/ganache/

## Verification Commands

After installation, verify all components are working:

```bash
# Check Node.js and npm
node --version
npm --version

# Check Python
python3 --version
pip3 --version

# Check IPFS
ipfs --version

# Check Git
git --version

# Check curl and jq
curl --version
jq --version

# Check Ganache
ganache-cli --version
```

## Environment Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd llm-blockchain
   ```

2. **Install Python dependencies**:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies**:
   ```bash
   cd contracts-clean
   npm install
   
   cd ../frontend
   npm install
   ```

4. **Initialize IPFS** (if not done already):
   ```bash
   ipfs init
   ```

## Port Configuration

The following ports must be available:

- **3000**: React frontend
- **8001**: FastAPI backend
- **8545**: Ganache blockchain
- **5001**: IPFS API
- **8080**: IPFS Gateway
- **4001**: IPFS Swarm (P2P)

## OpenAI API Key

Set up your OpenAI API key:

```bash
# Create .env file in backend directory
cd backend
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

## Quick Start

After installing all dependencies:

```bash
# Start Ganache (in separate terminal)
ganache-cli --host 0.0.0.0 --port 8545 --chainId 1337

# Start the backend system (includes IPFS)
./start_backend.sh

# Start the frontend (in separate terminal)
cd frontend
npm start
```

## Troubleshooting

### Common Issues:

1. **IPFS connection refused**:
   - Ensure IPFS daemon is running: `ipfs daemon`
   - Check if port 5001 is available

2. **Ganache connection issues**:
   - Verify Ganache is running on port 8545
   - Check network configuration in contracts

3. **Python dependencies**:
   - Ensure virtual environment is activated
   - Update pip: `pip install --upgrade pip`

4. **Node.js version conflicts**:
   - Use nvm to manage Node.js versions
   - Ensure compatible versions for all packages

### Support

For additional help:
- Check the main README.md
- Review STARTUP_COMPLETE_GUIDE.md
- Check service logs in backend/backend.log and ipfs.log