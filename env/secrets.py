"""
Secure secrets management for API keys and sensitive data
Loads environment variables from .env file and validates them
"""

import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file
ENV_FILE = Path(__file__).parent.parent / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
    logger.info(f"Loaded environment variables from {ENV_FILE}")
else:
    logger.warning(f".env file not found at {ENV_FILE}")


class SecretManager:
    """
    Securely manage and validate sensitive credentials
    """
    
    # Required secrets
    REQUIRED_SECRETS = {
        "OPENAI_API_KEY": "OpenAI API Key",
    }
    
    # Optional secrets
    OPTIONAL_SECRETS = {
        "SERPAPI_API_KEY": "SerpAPI Key (optional)",
        "ANTHROPIC_API_KEY": "Anthropic API Key (optional)",
        "HUGGINGFACE_API_KEY": "Hugging Face API Key (optional)",
    }
    
    @staticmethod
    def get_secret(key: str, required: bool = False, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieve a secret from environment variables
        
        Args:
            key: Secret key name
            required: Whether this secret is required
            default: Default value if not found
            
        Returns:
            Secret value or default
            
        Raises:
            ValueError: If required secret is missing
        """
        value = os.getenv(key, default)
        
        if value is None and required:
            raise ValueError(
                f"Required secret '{key}' not found in environment. "
                f"Please add it to .env file: {ENV_FILE}"
            )
        
        if value and key.endswith("_KEY"):
            # Log that we found a key (without showing the actual value)
            logger.info(f"✓ Secret '{key}' loaded successfully")
        
        return value
    
    @staticmethod
    def validate_secrets() -> dict:
        """
        Validate all required secrets are available
        
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "missing": [],
            "found": [],
            "optional": {}
        }
        
        # Check required secrets
        for key, description in SecretManager.REQUIRED_SECRETS.items():
            try:
                value = SecretManager.get_secret(key, required=True)
                results["found"].append(key)
            except ValueError as e:
                results["missing"].append(key)
                results["valid"] = False
                logger.error(str(e))
        
        # Check optional secrets
        for key, description in SecretManager.OPTIONAL_SECRETS.items():
            value = SecretManager.get_secret(key, required=False)
            results["optional"][key] = "found" if value else "missing"
        
        return results
    
    @staticmethod
    def get_openai_api_key() -> Optional[str]:
        """Get OpenAI API key (required)"""
        return SecretManager.get_secret("OPENAI_API_KEY", required=True)
    
    @staticmethod
    def get_anthropic_api_key() -> Optional[str]:
        """Get Anthropic API key (optional)"""
        return SecretManager.get_secret("ANTHROPIC_API_KEY", required=False)
    
    @staticmethod
    def get_huggingface_api_key() -> Optional[str]:
        """Get Hugging Face API key (optional)"""
        return SecretManager.get_secret("HUGGINGFACE_API_KEY", required=False)
    
    @staticmethod
    def get_serpapi_api_key() -> Optional[str]:
        """Get SerpAPI key (optional)"""
        return SecretManager.get_secret("SERPAPI_API_KEY", required=False)


# Validate secrets on import
try:
    validation = SecretManager.validate_secrets()
    if not validation["valid"]:
        logger.error(f"Missing required secrets: {validation['missing']}")
except Exception as e:
    logger.warning(f"Could not validate secrets: {e}")
