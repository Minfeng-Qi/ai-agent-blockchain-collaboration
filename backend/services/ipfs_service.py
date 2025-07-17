"""
IPFS Service for storing agent conversations
"""

import json
import os
import requests
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class IPFSService:
    """Service for interacting with IPFS for storing agent conversations"""
    
    def __init__(self):
        """Initialize IPFS service with configuration"""
        # 默认使用本地IPFS节点，也可以配置为使用Infura或Pinata等IPFS网关
        self.ipfs_api_url = os.environ.get('IPFS_API_URL', 'http://127.0.0.1:5001/api/v0')
        self.ipfs_gateway = os.environ.get('IPFS_GATEWAY_URL', 'http://127.0.0.1:8081/ipfs')
        
        # 如果使用Infura或Pinata等服务，可以设置项目ID和密钥
        self.project_id = os.environ.get('IPFS_PROJECT_ID', '')
        self.project_secret = os.environ.get('IPFS_PROJECT_SECRET', '')
        
        # 检查IPFS是否可用
        self.ipfs_available = self._check_ipfs_availability()
        
        # 模拟模式 - 当IPFS不可用时使用
        mock_mode_env = os.environ.get('IPFS_MOCK_MODE', 'False')
        self.mock_mode = mock_mode_env.lower() == 'true' if mock_mode_env else not self.ipfs_available
        self.mock_cids = {}  # 存储模拟CID的字典
        
        if self.mock_mode:
            logger.warning(f"IPFS service running in mock mode (available: {self.ipfs_available})")
        else:
            logger.info(f"IPFS service connected successfully (available: {self.ipfs_available})")
    
    def _check_ipfs_availability(self) -> bool:
        """Check if IPFS is available"""
        try:
            response = requests.post(f"{self.ipfs_api_url}/version", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"IPFS availability check failed: {str(e)}")
            return False
    
    async def upload_json(self, data: Dict) -> Dict[str, Any]:
        """Upload JSON data to IPFS and return result"""
        try:
            cid = self.add_json(data)
            return {
                "success": True,
                "cid": cid,
                "url": self.get_gateway_url(cid),
                "mode": "mock" if self.mock_mode else "real"
            }
        except Exception as e:
            logger.error(f"Failed to upload to IPFS: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "mode": "error"
            }
    
    def add_json(self, data: Dict) -> str:
        """Add JSON data to IPFS"""
        if self.mock_mode:
            # 在模拟模式下，生成一个假的CID并存储数据
            import hashlib
            mock_cid = f"Qm{hashlib.sha256(json.dumps(data).encode()).hexdigest()[:44]}"
            self.mock_cids[mock_cid] = data
            logger.info(f"Mock mode: Generated CID {mock_cid}")
            return mock_cid
            
        try:
            # 将数据转换为JSON字符串
            json_data = json.dumps(data)
            
            # 准备请求头和认证
            headers = {}
            auth = None
            if self.project_id and self.project_secret:
                auth = (self.project_id, self.project_secret)
            
            # 发送到IPFS
            files = {
                'file': ('conversation.json', json_data)
            }
            
            response = requests.post(
                f"{self.ipfs_api_url}/add", 
                files=files,
                auth=auth,
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"IPFS add failed: {response.text}")
                raise Exception(f"Failed to add to IPFS: {response.text}")
                
            result = response.json()
            return result['Hash']
            
        except Exception as e:
            logger.error(f"Error adding data to IPFS: {str(e)}")
            if self.mock_mode:
                # 如果实际调用失败但启用了模拟模式，回退到模拟
                import hashlib
                mock_cid = f"Qm{hashlib.sha256(json.dumps(data).encode()).hexdigest()[:44]}"
                self.mock_cids[mock_cid] = data
                logger.info(f"Fallback to mock mode: Generated CID {mock_cid}")
                return mock_cid
            raise
    
    def get_json(self, cid: str) -> Dict:
        """Get JSON data from IPFS by CID"""
        if self.mock_mode and cid in self.mock_cids:
            # 在模拟模式下，从内存中检索数据
            logger.info(f"Mock mode: Retrieved data for CID {cid}")
            return self.mock_cids[cid]
            
        try:
            # 准备请求头和认证
            headers = {}
            auth = None
            if self.project_id and self.project_secret:
                auth = (self.project_id, self.project_secret)
            
            # 从IPFS获取数据
            response = requests.post(
                f"{self.ipfs_api_url}/cat?arg={cid}",
                auth=auth,
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"IPFS cat failed: {response.text}")
                raise Exception(f"Failed to get from IPFS: {response.text}")
                
            return json.loads(response.text)
            
        except Exception as e:
            logger.error(f"Error getting data from IPFS: {str(e)}")
            if self.mock_mode and cid in self.mock_cids:
                # 如果实际调用失败但启用了模拟模式，回退到模拟
                logger.info(f"Fallback to mock mode: Retrieved data for CID {cid}")
                return self.mock_cids[cid]
            raise
    
    def get_gateway_url(self, cid: str) -> str:
        """Get the gateway URL for an IPFS CID"""
        return f"{self.ipfs_gateway}/{cid}"
    
    async def get_json_async(self, cid: str) -> Dict:
        """Async version of get_json"""
        return self.get_json(cid)

# 创建单例实例
ipfs_service = IPFSService()