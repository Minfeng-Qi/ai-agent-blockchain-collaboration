"""
Configuration settings for the Agent Learning System backend
"""

import os
import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to the path to make imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# API settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_change_in_production")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# CORS settings
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Database settings
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/agent_learning")

# Blockchain settings
WEB3_PROVIDER_URI = os.getenv("WEB3_PROVIDER_URI", "http://127.0.0.1:8545")  # Default Ganache port
CHAIN_ID = int(os.getenv("CHAIN_ID", "1337"))  # Default Ganache chain ID

# Try to load contract addresses from deployment file
CONTRACT_ADDRESSES = {}
deployment_file = BASE_DIR / "deployment-addresses.json"
if deployment_file.exists():
    try:
        with open(deployment_file, "r") as f:
            deployment_data = json.load(f)
            CONTRACT_ADDRESSES = {
                "AGENT_REGISTRY_ADDRESS": deployment_data.get("agentRegistry"),
                "TASK_MANAGER_ADDRESS": deployment_data.get("taskManager"),
                "TASK_MARKETPLACE_ADDRESS": deployment_data.get("taskMarketplace"),
                "BID_AUCTION_ADDRESS": deployment_data.get("bidAuction"),
                "INCENTIVE_ENGINE_ADDRESS": deployment_data.get("incentiveEngine"),
                "MESSAGE_HUB_ADDRESS": deployment_data.get("messageHub"),
                "ACTION_LOGGER_ADDRESS": deployment_data.get("actionLogger")
            }
    except Exception as e:
        print(f"Error loading deployment addresses: {e}")

# Override with environment variables if provided
CONTRACT_ADDRESSES["AGENT_REGISTRY_ADDRESS"] = os.getenv("AGENT_REGISTRY_ADDRESS", CONTRACT_ADDRESSES.get("AGENT_REGISTRY_ADDRESS"))
CONTRACT_ADDRESSES["TASK_MANAGER_ADDRESS"] = os.getenv("TASK_MANAGER_ADDRESS", CONTRACT_ADDRESSES.get("TASK_MANAGER_ADDRESS"))
CONTRACT_ADDRESSES["TASK_MARKETPLACE_ADDRESS"] = os.getenv("TASK_MARKETPLACE_ADDRESS", CONTRACT_ADDRESSES.get("TASK_MARKETPLACE_ADDRESS"))
CONTRACT_ADDRESSES["BID_AUCTION_ADDRESS"] = os.getenv("BID_AUCTION_ADDRESS", CONTRACT_ADDRESSES.get("BID_AUCTION_ADDRESS"))
CONTRACT_ADDRESSES["INCENTIVE_ENGINE_ADDRESS"] = os.getenv("INCENTIVE_ENGINE_ADDRESS", CONTRACT_ADDRESSES.get("INCENTIVE_ENGINE_ADDRESS"))
CONTRACT_ADDRESSES["MESSAGE_HUB_ADDRESS"] = os.getenv("MESSAGE_HUB_ADDRESS", CONTRACT_ADDRESSES.get("MESSAGE_HUB_ADDRESS"))
CONTRACT_ADDRESSES["ACTION_LOGGER_ADDRESS"] = os.getenv("ACTION_LOGGER_ADDRESS", CONTRACT_ADDRESSES.get("ACTION_LOGGER_ADDRESS"))

# OpenAI API settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Agent settings
DEFAULT_AGENT_CONFIDENCE = float(os.getenv("DEFAULT_AGENT_CONFIDENCE", "0.8"))
DEFAULT_AGENT_RISK_TOLERANCE = float(os.getenv("DEFAULT_AGENT_RISK_TOLERANCE", "0.5"))