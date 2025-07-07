import json
import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path

import ipfshttpclient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IPFSClient:
    """
    Client for interacting with IPFS for decentralized storage
    """
    def __init__(self, api_url: str = "/ip4/127.0.0.1/tcp/5001"):
        """
        Initialize IPFS client
        
        Args:
            api_url: URL of IPFS API endpoint
        """
        self.api_url = api_url
        self.client = None
        self.connected = False
        
    def connect(self) -> bool:
        """
        Connect to IPFS daemon
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.client = ipfshttpclient.connect(self.api_url)
            self.connected = True
            logger.info("Connected to IPFS daemon")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to IPFS: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """
        Disconnect from IPFS daemon
        """
        if self.client and self.connected:
            try:
                self.client.close()
                self.connected = False
                logger.info("Disconnected from IPFS daemon")
            except Exception as e:
                logger.error(f"Error disconnecting from IPFS: {e}")
    
    def upload_json(self, data: Dict[str, Any]) -> Optional[str]:
        """
        Upload JSON data to IPFS
        
        Args:
            data: Dictionary to upload as JSON
            
        Returns:
            IPFS hash (CID) if successful, None otherwise
        """
        if not self.connected and not self.connect():
            return None
        
        try:
            # Convert data to JSON string
            json_data = json.dumps(data)
            
            # Upload to IPFS
            result = self.client.add_str(json_data)
            logger.info(f"Uploaded data to IPFS with hash: {result}")
            
            return result
        except Exception as e:
            logger.error(f"Error uploading JSON to IPFS: {e}")
            return None
    
    def upload_file(self, file_path: Union[str, Path]) -> Optional[str]:
        """
        Upload a file to IPFS
        
        Args:
            file_path: Path to file to upload
            
        Returns:
            IPFS hash (CID) if successful, None otherwise
        """
        if not self.connected and not self.connect():
            return None
        
        try:
            path = Path(file_path)
            if not path.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            # Upload file to IPFS
            result = self.client.add(str(path))
            file_hash = result["Hash"]
            logger.info(f"Uploaded file {file_path} to IPFS with hash: {file_hash}")
            
            return file_hash
        except Exception as e:
            logger.error(f"Error uploading file to IPFS: {e}")
            return None
    
    def download_json(self, ipfs_hash: str) -> Optional[Dict[str, Any]]:
        """
        Download and parse JSON data from IPFS
        
        Args:
            ipfs_hash: IPFS hash (CID) to download
            
        Returns:
            Parsed JSON data if successful, None otherwise
        """
        if not self.connected and not self.connect():
            return None
        
        try:
            # Download data from IPFS
            content = self.client.cat(ipfs_hash)
            
            # Parse JSON
            data = json.loads(content)
            
            return data
        except Exception as e:
            logger.error(f"Error downloading JSON from IPFS: {e}")
            return None
    
    def download_file(self, ipfs_hash: str, output_path: Union[str, Path]) -> bool:
        """
        Download a file from IPFS
        
        Args:
            ipfs_hash: IPFS hash (CID) to download
            output_path: Path to save downloaded file
            
        Returns:
            True if download successful, False otherwise
        """
        if not self.connected and not self.connect():
            return False
        
        try:
            # Create directory if it doesn't exist
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download file from IPFS
            content = self.client.cat(ipfs_hash)
            
            # Write to file
            with open(output_path, "wb") as f:
                f.write(content)
            
            logger.info(f"Downloaded {ipfs_hash} to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error downloading file from IPFS: {e}")
            return False
    
    def get_ipfs_url(self, ipfs_hash: str) -> str:
        """
        Get HTTP URL for IPFS content (using public gateway)
        
        Args:
            ipfs_hash: IPFS hash (CID)
            
        Returns:
            Public HTTP URL for the content
        """
        return f"https://ipfs.io/ipfs/{ipfs_hash}"