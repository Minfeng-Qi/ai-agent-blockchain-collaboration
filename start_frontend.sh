#!/bin/bash
# Start frontend for Agent Learning System

# Check Node.js version
NODE_VERSION=$(node -v)
if [[ $NODE_VERSION != v18* ]]; then
  echo "Warning: Current Node.js version is $NODE_VERSION, but project requires v18.x"
  echo "Please install Node.js v18.x using nvm or another version manager"
  echo "Example: nvm install 18 && nvm use 18"
  exit 1
fi

# Start frontend
echo "Starting frontend server..."
cd frontend
npm start