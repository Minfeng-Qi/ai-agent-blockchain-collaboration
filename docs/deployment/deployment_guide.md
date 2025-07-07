# Deployment Guide

This guide provides instructions for deploying the Agent Learning System in various environments.

## Prerequisites

- Python 3.9+
- Node.js 16+
- Docker and Docker Compose (optional)
- Ethereum node access (Infura, Alchemy, or local node)
- MongoDB 4.4+

## Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/agent-learning-system.git
cd agent-learning-system
```

### 2. Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# Backend Configuration
API_PORT=8000
DEBUG=False
LOG_LEVEL=INFO
SECRET_KEY=your_secret_key_here

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/agent_learning

# Blockchain Configuration
WEB3_PROVIDER_URI=https://mainnet.infura.io/v3/your_infura_key
CHAIN_ID=1
CONTRACT_OWNER_ADDRESS=0x...
CONTRACT_OWNER_PRIVATE_KEY=your_private_key_here

# Smart Contract Addresses
AGENT_REGISTRY_ADDRESS=0x...
TASK_MANAGER_ADDRESS=0x...
TASK_MARKETPLACE_ADDRESS=0x...
BID_AUCTION_ADDRESS=0x...
INCENTIVE_ENGINE_ADDRESS=0x...
MESSAGE_HUB_ADDRESS=0x...
ACTION_LOGGER_ADDRESS=0x...

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
```

## Deployment Options

### Option 1: Local Development Deployment

#### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup

```bash
cd frontend
npm install
npm start
```

### Option 2: Docker Deployment

```bash
docker-compose up -d
```

This will start the following services:
- Backend API (accessible on port 8000)
- Frontend (accessible on port 3000)
- MongoDB (accessible on port 27017)

### Option 3: Production Deployment

#### Backend Deployment with Gunicorn

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

#### Frontend Production Build

```bash
cd frontend
npm install
npm run build
```

Serve the built files using Nginx or another web server.

#### Nginx Configuration Example

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        root /path/to/frontend/build;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Smart Contract Deployment

### 1. Compile Contracts

```bash
cd contracts
npx hardhat compile
```

### 2. Deploy Contracts

```bash
npx hardhat run scripts/deploy.js --network mainnet
```

Replace `mainnet` with your desired network (e.g., `rinkeby`, `goerli`, `localhost`).

### 3. Update Contract Addresses

After deployment, update the contract addresses in your `.env` file.

## Monitoring and Maintenance

### Logging

Logs are stored in the `logs` directory. Configure log rotation for production environments.

### Database Backups

Set up regular MongoDB backups:

```bash
mongodump --uri="mongodb://localhost:27017/agent_learning" --out=/path/to/backup/directory
```

### Health Checks

The API provides a health check endpoint at `/health` that can be used for monitoring.

## Scaling Considerations

- Use a load balancer for the backend API in high-traffic environments
- Consider using a managed MongoDB service for the database
- Implement caching with Redis for frequently accessed data
- Use a CDN for serving frontend static assets