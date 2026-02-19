"""
Utility functions for data processing and common tasks
"""

import pandas as pd
from pathlib import Path
from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR


def load_csv(file_path: str) -> pd.DataFrame:
    """Load CSV file into DataFrame"""
    return pd.read_csv(file_path)


def save_csv(df: pd.DataFrame, file_name: str, folder: str = "processed"):
    """Save DataFrame to CSV"""
    if folder == "raw":
        save_path = RAW_DATA_DIR / file_name
    else:
        save_path = PROCESSED_DATA_DIR / file_name
    
    df.to_csv(save_path, index=False)
    return save_path


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> list:
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    
    return chunks
