#!/bin/bash

# Setup script for LLM Multi-Agent System

# Check if Python 3.8+ is installed
python_version=$(python3 --version 2>&1 | awk '{print $2}')
python_major=$(echo $python_version | cut -d. -f1)
python_minor=$(echo $python_version | cut -d. -f2)

if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 8 ]); then
    echo "Error: Python 3.8 or higher is required."
    echo "Current version: $python_version"
    exit 1
fi

echo "Python version $python_version detected. OK."

# Install required packages
echo "Installing required Python packages..."
pip install -r requirements.txt

# Check if .env file exists, create if not
if [ ! -f .env ]; then
    echo "Creating .env file with OpenAI API key..."
    echo "OPENAI_API_KEY=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" > .env
    echo ".env file created."
else
    echo ".env file already exists."
fi

# Make scripts executable
echo "Making scripts executable..."
chmod +x run_agents.py test_openai_integration.py openai_integration.py

# Check if contract_addresses.json exists
if [ ! -f contract_addresses.json ]; then
    echo "Creating default contract_addresses.json..."
    cat > contract_addresses.json << EOL
{
    "AgentRegistry": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
    "ActionLogger": "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512",
    "IncentiveEngine": "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0",
    "TaskManager": "0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9",
    "BidAuction": "0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9",
    "TaskMarketplace": "0xa513E6E4b8f2a923D98304ec87F64353C4D5C853",
    "MessageHub": "0x2279B7A0a67DB372996a5FaB50D91eAA73d2eBe6"
}
EOL
    echo "contract_addresses.json created with default addresses."
else
    echo "contract_addresses.json already exists."
fi

echo ""
echo "Setup complete! You can now run the agents:"
echo "  - Test OpenAI integration: ./test_openai_integration.py"
echo "  - Run multiple agents: ./run_agents.py --agents 3"
echo "  - Create example tasks: ./run_agents.py --create-tasks"
echo ""
echo "Make sure your local blockchain is running and contracts are deployed." 