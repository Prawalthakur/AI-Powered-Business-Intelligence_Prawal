"""
Environment configuration module
Securely loads settings from environment and secrets files
"""

import logging
from pathlib import Path
import sys
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Load environment variables
ENV_FILE = Path(__file__).parent.parent / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)

# Import SecretManager after loading .env
if __package__ is None and str(Path(__file__).parent.parent) not in sys.path:
    # Allow running this file directly.
    sys.path.insert(0, str(Path(__file__).parent.parent))

from env.secrets import SecretManager

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
UPLOADS_DIR = DATA_DIR / "uploads"
VECTOR_DB_DIR = PROJECT_ROOT / "vector_db"
ENV_DIR = PROJECT_ROOT / "env"

# API Configuration (loaded from secrets)
try:
    OPENAI_API_KEY = SecretManager.get_openai_api_key()
except ValueError as e:
    OPENAI_API_KEY = None
    logging.warning(str(e))

# LLM Configuration
LLM_MODEL = "gpt-4"
EMBEDDING_MODEL = "text-embedding-3-small"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

# Debug Configuration
import os
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Streamlit Configuration
from typing import Any

STREAMLIT_PAGE_CONFIG: dict[str, Any] = {
    "page_title": "Capstone Sales Analysis",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "menu_items": {
        "Get Help": "https://streamlit.io",
        "Report a Bug": "https://github.com/",
        "About": "Sales Analysis with FAISS Vector DB"
    }
}

# Validate that API keys are available
def validate_configuration() -> bool:
    """Validate that all required configuration is available"""
    if not OPENAI_API_KEY:
        logging.error("OPENAI_API_KEY not configured. Please set it in .env file")
        return False
    return True
