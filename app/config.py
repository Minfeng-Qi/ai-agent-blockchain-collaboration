"""
Configuration settings for the Agent Learning System API.
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# API settings
API_V1_STR = "/api/v1"
PROJECT_NAME = "Agent Learning System API"
DESCRIPTION = "API for blockchain-based agent task management and learning"
VERSION = "0.1.0"

# Web3 settings
WEB3_PROVIDER_URI = os.getenv("WEB3_PROVIDER_URI", "http://localhost:8545")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")

# Contract addresses
CONTRACT_ADDRESSES = {
    "AgentRegistry": os.getenv("AGENT_REGISTRY_ADDRESS", ""),
    "IncentiveEngine": os.getenv("INCENTIVE_ENGINE_ADDRESS", ""),
    "BidAuction": os.getenv("BID_AUCTION_ADDRESS", ""),
    "TaskManager": os.getenv("TASK_MANAGER_ADDRESS", ""),
    "TaskMarketplace": os.getenv("TASK_MARKETPLACE_ADDRESS", ""),
    "MessageHub": os.getenv("MESSAGE_HUB_ADDRESS", ""),
}

# ABI directory
ABI_DIR = BASE_DIR / "abis"

# CORS settings
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",  # React frontend
    "http://localhost:8000",  # API itself
]

# Database settings (for future use)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# Learning model settings
MODELS_DIR = BASE_DIR / "models"
DEFAULT_LEARNING_RATE = 0.001
DEFAULT_DISCOUNT_FACTOR = 0.95
DEFAULT_EXPLORATION_RATE = 0.1