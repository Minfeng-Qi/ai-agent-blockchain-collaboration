import logging
from typing import Tuple, Optional

from eth_account.messages import encode_defunct
from eth_account import Account
from eth_keys import keys
from web3 import Web3

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SignatureVerifier:
    """
    Utilities for ECDSA signature verification and message signing
    """
    def __init__(self, web3_provider: str = "http://localhost:8545"):
        """
        Initialize SignatureVerifier
        
        Args:
            web3_provider: URL of Web3 provider
        """
        self.w3 = Web3(Web3.HTTPProvider(web3_provider))
    
    def verify_signature(self, message: str, signature: str, expected_address: str) -> bool:
        """
        Verify if a signature was created by the expected address
        
        Args:
            message: Original message that was signed
            signature: Signature as hex string (with 0x prefix)
            expected_address: Ethereum address that supposedly signed the message
            
        Returns:
            True if signature is valid and from expected_address, False otherwise
        """
        try:
            # Convert address to checksum address
            expected_address = self.w3.to_checksum_address(expected_address)
            
            # Prepare the message for recovery
            message_hash = encode_defunct(text=message)
            
            # Recover the address from the signature
            recovered_address = self.w3.eth.account.recover_message(message_hash, signature=signature)
            
            # Check if recovered address matches expected address
            return recovered_address.lower() == expected_address.lower()
        except Exception as e:
            logger.error(f"Error verifying signature: {e}")
            return False
    
    @staticmethod
    def generate_key_pair() -> Tuple[str, str]:
        """
        Generate a new ECDSA key pair
        
        Returns:
            Tuple of (private_key, address)
        """
        account = Account.create()
        return account.key.hex(), account.address
    
    @staticmethod
    def address_from_private_key(private_key: str) -> str:
        """
        Get Ethereum address from private key
        
        Args:
            private_key: Ethereum private key (hex string with or without 0x prefix)
            
        Returns:
            Ethereum address corresponding to private key
        """
        # Ensure private key has 0x prefix
        if not private_key.startswith('0x'):
            private_key = '0x' + private_key
            
        account = Account.from_key(private_key)
        return account.address
    
    def sign_message(self, message: str, private_key: str) -> Optional[str]:
        """
        Sign a message with a private key
        
        Args:
            message: Message to sign
            private_key: Private key to sign with (hex string with or without 0x prefix)
            
        Returns:
            Signature as hex string if successful, None otherwise
        """
        try:
            # Ensure private key has 0x prefix
            if not private_key.startswith('0x'):
                private_key = '0x' + private_key
                
            # Prepare the message
            message_hash = encode_defunct(text=message)
            
            # Sign the message
            signed_message = self.w3.eth.account.sign_message(message_hash, private_key=private_key)
            
            return signed_message.signature.hex()
        except Exception as e:
            logger.error(f"Error signing message: {e}")
            return None