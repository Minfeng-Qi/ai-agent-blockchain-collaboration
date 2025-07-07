#!/usr/bin/env python3

"""
Simple script to run the backend server directly.
This avoids Python module import issues by running from the project root.
"""

import sys
import os
import importlib.util
import uvicorn

# Add the current directory to the Python path
sys.path.append(os.path.abspath("."))

# Import and run the FastAPI app
if __name__ == "__main__":
    print("Starting backend server on port 8000...")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True) 