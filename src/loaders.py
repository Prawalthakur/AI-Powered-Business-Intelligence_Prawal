"""
Document loaders for PDF, CSV, and other file formats
Handles loading and preprocessing documents for RAG systems
"""

from pathlib import Path
from typing import List, Tuple, Optional
import logging

import pandas as pd
from langchain_community.document_loaders import (
    PyPDFLoader,
    CSVLoader,
    DirectoryLoader
)
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import CHUNK_SIZE, CHUNK_OVERLAP, RAW_DATA_DIR, UPLOADS_DIR

logger = logging.getLogger(__name__)


def load_pdf(file_path: str) -> List[Document]:
    """
    Load a PDF file and return as LangChain documents
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        List of Document objects
    """
    try:
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        logger.info(f"Loaded {len(documents)} pages from {file_path}")
        return documents
    except Exception as e:
        logger.error(f"Error loading PDF {file_path}: {e}")
        return []


def load_csv(file_path: str, source_column: Optional[str] = None) -> List[Document]:
    """
    Load a CSV file and return as LangChain documents
    
    Args:
        file_path: Path to CSV file
        source_column: Column to use as document source (optional)
        
    Returns:
        List of Document objects
    """
    try:
        loader = CSVLoader(
            file_path=file_path,
            source_column=source_column or "source"
        )
        documents = loader.load()
        logger.info(f"Loaded {len(documents)} rows from {file_path}")
        return documents
    except Exception as e:
        logger.error(f"Error loading CSV {file_path}: {e}")
        # Fallback: load with pandas
        try:
            df = pd.read_csv(file_path)
            documents = []
            for idx, row in df.iterrows():
                content = "\n".join([f"{col}: {val}" for col, val in row.items()])
                doc = Document(
                    page_content=content,
                    metadata={"source": file_path, "row": idx}
                )
                documents.append(doc)
            logger.info(f"Loaded {len(documents)} rows from {file_path} using pandas")
            return documents
        except Exception as e2:
            logger.error(f"Fallback CSV loading failed: {e2}")
            return []


def load_directory(directory_path: str, file_type: str = "pdf") -> List[Document]:
    """
    Load all files of a specific type from a directory
    
    Args:
        directory_path: Path to directory
        file_type: File type to load ("pdf" or "csv")
        
    Returns:
        List of Document objects
    """
    try:
        directory = Path(directory_path)
        documents = []
        
        if file_type.lower() == "pdf":
            # Manual PDF loading since DirectoryLoader doesn't support PyPDFLoader
            for pdf_file in directory.glob("**/*.pdf"):
                docs = load_pdf(str(pdf_file))
                documents.extend(docs)
        elif file_type.lower() == "csv":
            for csv_file in directory.glob("**/*.csv"):
                docs = load_csv(str(csv_file))
                documents.extend(docs)
        else:
            logger.error(f"Unsupported file type: {file_type}")
            return []
            
        logger.info(f"Loaded {len(documents)} documents from {directory_path}")
        return documents
    except Exception as e:
        logger.error(f"Error loading directory {directory_path}: {e}")
        return []


def split_documents(
    documents: List[Document],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> List[Document]:
    """
    Split documents into smaller chunks for embedding
    
    Args:
        documents: List of Document objects
        chunk_size: Size of each chunk
        chunk_overlap: Overlap between chunks
        
    Returns:
        List of split Document objects
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""]
    )
    split_docs = splitter.split_documents(documents)
    logger.info(f"Split {len(documents)} documents into {len(split_docs)} chunks")
    return split_docs


def load_and_split_pdf(file_path: str) -> List[Document]:
    """
    Convenience function: Load PDF and split into chunks
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        List of split Document objects
    """
    documents = load_pdf(file_path)
    return split_documents(documents)


def load_and_split_csv(file_path: str) -> List[Document]:
    """
    Convenience function: Load CSV and split into chunks
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        List of split Document objects
    """
    documents = load_csv(file_path)
    return split_documents(documents)


def load_uploaded_file(file_path: str) -> Tuple[List[Document], str]:
    """
    Load any supported file type based on extension
    
    Args:
        file_path: Path to file
        
    Returns:
        Tuple of (documents list, file type)
    """
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext == ".pdf":
        documents = load_and_split_pdf(file_path)
        return documents, "pdf"
    elif file_ext == ".csv":
        documents = load_and_split_csv(file_path)
        return documents, "csv"
    else:
        logger.error(f"Unsupported file type: {file_ext}")
        return [], "unknown"
