#!/bin/bash

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up Node.js environment for blockchain-based LLM Multi-Agent System${NC}"
echo ""

# Check if nvm is installed
if ! command -v nvm &> /dev/null; then
    echo -e "${RED}nvm (Node Version Manager) is not installed.${NC}"
    echo "Please install nvm first by running:"
    echo -e "${GREEN}curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash${NC}"
    echo "or"
    echo -e "${GREEN}wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash${NC}"
    echo ""
    echo "After installation, restart your terminal and run this script again."
    exit 1
fi

# Install Node.js v18 (LTS)
echo -e "${BLUE}Installing Node.js v18 (LTS)...${NC}"
nvm install 18
nvm use 18

# Verify installation
NODE_VERSION=$(node -v)
echo -e "${GREEN}Node.js ${NODE_VERSION} installed successfully.${NC}"

# Install project dependencies
echo -e "${BLUE}Installing project dependencies...${NC}"
npm install

echo ""
echo -e "${GREEN}Setup complete! You can now run the tests:${NC}"
echo -e "${BLUE}npx hardhat test${NC}"
echo ""
echo -e "${BLUE}Or run individual tests:${NC}"
echo -e "${BLUE}./test/run-individual-tests.sh${NC}" 