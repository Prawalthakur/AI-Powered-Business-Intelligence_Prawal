"""
Configuration and constants for the LLM project
Imports from secure environment module
"""

from env import (
    PROJECT_ROOT,
    DATA_DIR,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    UPLOADS_DIR,
    VECTOR_DB_DIR,
    OPENAI_API_KEY,
    LLM_MODEL,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    DEBUG,
    STREAMLIT_PAGE_CONFIG,
    SecretManager,
    validate_configuration
)

# Re-export for backward compatibility
__all__ = [
    'PROJECT_ROOT',
    'DATA_DIR',
    'RAW_DATA_DIR',
    'PROCESSED_DATA_DIR',
    'UPLOADS_DIR',
    'VECTOR_DB_DIR',
    'OPENAI_API_KEY',
    'LLM_MODEL',
    'EMBEDDING_MODEL',
    'CHUNK_SIZE',
    'CHUNK_OVERLAP',
    'DEBUG',
    'STREAMLIT_PAGE_CONFIG',
    'SecretManager',
    'validate_configuration'
]
