"""
__init__.py for environment module
Exports the SecretManager and configuration
"""

from env.secrets import SecretManager
from env.config import (
    PROJECT_ROOT,
    DATA_DIR,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    UPLOADS_DIR,
    VECTOR_DB_DIR,
    ENV_DIR,
    OPENAI_API_KEY,
    LLM_MODEL,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    DEBUG,
    STREAMLIT_PAGE_CONFIG,
    validate_configuration
)

__all__ = [
    'SecretManager',
    'PROJECT_ROOT',
    'DATA_DIR',
    'RAW_DATA_DIR',
    'PROCESSED_DATA_DIR',
    'UPLOADS_DIR',
    'VECTOR_DB_DIR',
    'ENV_DIR',
    'OPENAI_API_KEY',
    'LLM_MODEL',
    'EMBEDDING_MODEL',
    'CHUNK_SIZE',
    'CHUNK_OVERLAP',
    'DEBUG',
    'STREAMLIT_PAGE_CONFIG',
    'validate_configuration'
]
