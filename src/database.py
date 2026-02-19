"""
Vector database management using FAISS
Handles document embeddings and similarity search
Supports managing complete vector database with multiple indexes
"""

from typing import List, Dict, Optional, Tuple, Any
import logging
import shutil
import json
from pathlib import Path
from datetime import datetime

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from src.config import VECTOR_DB_DIR
from src.llm import get_embeddings

logger = logging.getLogger(__name__)

# Metadata file for tracking indexes
METADATA_FILE = VECTOR_DB_DIR / "database_metadata.json"


def get_embeddings_for_faiss():
    """Get embeddings object for FAISS"""
    return get_embeddings()


def create_vector_store(documents: List[Document], index_name: str = "sales_documents") -> Optional[FAISS]:
    """
    Create a FAISS vector store from documents
    
    Args:
        documents: List of Document objects to embed
        index_name: Name for the vector store index
        
    Returns:
        FAISS vector store instance or None if failed
    """
    if not documents:
        logger.error("No documents provided to create vector store")
        return None
    
    try:
        embeddings = get_embeddings_for_faiss()
        
        # Create FAISS vector store
        vector_store = FAISS.from_documents(
            documents=documents,
            embedding=embeddings
        )
        logger.info(f"Created FAISS vector store with {len(documents)} documents")
        return vector_store
    except Exception as e:
        logger.error(f"Error creating FAISS vector store: {e}")
        raise


def save_vector_store(vector_store: FAISS, index_name: str = "sales_documents") -> str:
    """
    Save FAISS vector store to disk
    
    Args:
        vector_store: FAISS vector store instance
        index_name: Name for the saved index
        
    Returns:
        Path where the index was saved
    """
    try:
        # Ensure directory exists
        VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
        
        save_path = VECTOR_DB_DIR / index_name
        vector_store.save_local(str(save_path))
        logger.info(f"Saved FAISS vector store to {save_path}")
        return str(save_path)
    except Exception as e:
        logger.error(f"Error saving FAISS vector store: {e}")
        raise


def load_vector_store(index_name: str = "sales_documents") -> Optional[FAISS]:
    """
    Load FAISS vector store from disk
    
    Args:
        index_name: Name of the index to load
        
    Returns:
        FAISS vector store instance or None if not found
    """
    try:
        embeddings = get_embeddings_for_faiss()
        load_path = VECTOR_DB_DIR / index_name
        
        if not load_path.exists():
            logger.warning(f"Vector store not found at {load_path}")
            return None
        
        vector_store = FAISS.load_local(
            folder_path=str(load_path),
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
        logger.info(f"Loaded FAISS vector store from {load_path}")
        return vector_store
    except Exception as e:
        logger.error(f"Error loading FAISS vector store: {e}")
        return None


def add_documents_to_store(
    vector_store: FAISS,
    documents: List[Document]
) -> FAISS:
    """
    Add more documents to an existing FAISS vector store
    
    Args:
        vector_store: Existing FAISS vector store
        documents: Documents to add
        
    Returns:
        Updated vector store
    """
    try:
        if not documents:
            logger.warning("No documents to add")
            return vector_store
        
        vector_store.add_documents(documents)
        logger.info(f"Added {len(documents)} documents to FAISS vector store")
        return vector_store
    except Exception as e:
        logger.error(f"Error adding documents: {e}")
        raise


def similarity_search(
    vector_store: FAISS,
    query: str,
    k: int = 5,
    score_threshold: float = 0.0
) -> List[Tuple[Document, float]]:
    """
    Search for similar documents in FAISS vector store
    
    Args:
        vector_store: FAISS vector store
        query: Query text
        k: Number of results to return
        score_threshold: Minimum similarity score
        
    Returns:
        List of (document, score) tuples
    """
    try:
        results = vector_store.similarity_search_with_score(query, k=k)
        
        # Filter by score threshold if needed
        filtered_results = [
            (doc, score) for doc, score in results
            if score >= score_threshold
        ]
        
        logger.info(f"Found {len(filtered_results)} similar documents")
        return filtered_results
    except Exception as e:
        logger.error(f"Error during similarity search: {e}")
        return []


def similarity_search_documents_only(
    vector_store: FAISS,
    query: str,
    k: int = 5
) -> List[Document]:
    """
    Search and return only documents (without scores)
    
    Args:
        vector_store: FAISS vector store
        query: Query text
        k: Number of results
        
    Returns:
        List of Document objects
    """
    try:
        results = vector_store.similarity_search(query, k=k)
        logger.info(f"Retrieved {len(results)} documents")
        return results
    except Exception as e:
        logger.error(f"Error during search: {e}")
        return []


def get_retriever(vector_store: FAISS, k: int = 5):
    """
    Get a LangChain retriever from FAISS vector store
    
    Args:
        vector_store: FAISS vector store
        k: Number of results to return
        
    Returns:
        LangChain retriever object
    """
    return vector_store.as_retriever(search_kwargs={"k": k})


def delete_index(index_name: str = "sales_documents") -> bool:
    """
    Delete a FAISS vector store index
    
    Args:
        index_name: Name of the index to delete
        
    Returns:
        True if deletion was successful
    """
    try:
        index_path = VECTOR_DB_DIR / index_name
        
        if index_path.exists():
            shutil.rmtree(index_path)
            logger.info(f"Deleted FAISS index: {index_path}")
            return True
        else:
            logger.warning(f"Index not found: {index_path}")
            return False
    except Exception as e:
        logger.error(f"Error deleting index: {e}")
        return False


def list_indexes() -> List[str]:
    """
    List all available FAISS indexes
    
    Returns:
        List of index names
    """
    try:
        if not VECTOR_DB_DIR.exists():
            return []
        
        indexes = [d.name for d in VECTOR_DB_DIR.iterdir() if d.is_dir()]
        logger.info(f"Found {len(indexes)} FAISS indexes")
        return indexes
    except Exception as e:
        logger.error(f"Error listing indexes: {e}")
        return []


def merge_vector_stores(
    primary_store: FAISS,
    secondary_store: FAISS
) -> Optional[FAISS]:
    """
    Merge two FAISS vector stores
    
    Args:
        primary_store: Main vector store
        secondary_store: Vector store to merge in
        
    Returns:
        Merged vector store or None if failed
    """
    try:
        primary_store.merge_from(secondary_store)
        logger.info("Merged FAISS vector stores successfully")
        return primary_store
    except Exception as e:
        logger.error(f"Error merging vector stores: {e}")
        raise


def index_stats(vector_store: FAISS) -> Dict:
    """
    Get statistics about a FAISS index
    
    Args:
        vector_store: FAISS vector store
        
    Returns:
        Dictionary with index statistics
    """
    try:
        index_size = vector_store.index.ntotal
        
        stats = {
            "total_vectors": index_size,
            "index_type": type(vector_store.index).__name__,
            "embeddings_dimension": vector_store.index.d if hasattr(vector_store.index, 'd') else None
        }
        return stats
    except Exception as e:
        logger.error(f"Error getting index stats: {e}")
        return {}


def get_database_info() -> Dict:
    """
    Get comprehensive information about the entire vector database
    
    Returns:
        Dictionary with database statistics and metadata
    """
    try:
        indexes = list_indexes()
        total_vectors = 0
        total_size = 0
        index_details_list = []
        
        for index_name in indexes:
            index_path = VECTOR_DB_DIR / index_name
            
            # Get directory size
            size = sum(f.stat().st_size for f in index_path.rglob('*') if f.is_file())
            total_size += size
            
            # Load and get stats
            vector_store = load_vector_store(index_name)
            if vector_store:
                stats = index_stats(vector_store)
                total_vectors += stats.get('total_vectors', 0)
                index_details_list.append({
                    'name': index_name,
                    'vectors': stats.get('total_vectors', 0),
                    'size_bytes': size,
                    'size_mb': round(size / (1024 * 1024), 2)
                })
        
        database_info = {
            'location': str(VECTOR_DB_DIR),
            'total_indexes': len(indexes),
            'total_vectors': total_vectors,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'indexes': index_details_list,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Database info: {len(indexes)} indexes, {total_vectors} vectors, {round(total_size / (1024 * 1024), 2)} MB")
        return database_info
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        return {}


def index_details(index_name: str) -> Optional[Dict]:
    """
    Get detailed information about a specific index
    
    Args:
        index_name: Name of the index
        
    Returns:
        Dictionary with detailed index information
    """
    try:
        index_path = VECTOR_DB_DIR / index_name
        
        if not index_path.exists():
            logger.warning(f"Index not found: {index_name}")
            return None
        
        # Get directory size
        size = sum(f.stat().st_size for f in index_path.rglob('*') if f.is_file())
        
        # Load and get stats
        vector_store = load_vector_store(index_name)
        if not vector_store:
            return None
        
        stats = index_stats(vector_store)
        
        details = {
            'name': index_name,
            'path': str(index_path),
            'created': datetime.fromtimestamp(index_path.stat().st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(index_path.stat().st_mtime).isoformat(),
            'total_vectors': stats.get('total_vectors', 0),
            'index_type': stats.get('index_type', 'Unknown'),
            'embeddings_dimension': stats.get('embeddings_dimension', 0),
            'size_bytes': size,
            'size_mb': round(size / (1024 * 1024), 2)
        }
        
        return details
    except Exception as e:
        logger.error(f"Error getting index details: {e}")
        return None


def clear_database() -> bool:
    """
    Clear entire vector database (delete all indexes)
    
    Returns:
        True if successful
    """
    try:
        if VECTOR_DB_DIR.exists():
            shutil.rmtree(VECTOR_DB_DIR)
            VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
            logger.info("Cleared entire FAISS vector database")
            return True
        return False
    except Exception as e:
        logger.error(f"Error clearing database: {e}")
        return False


def export_index(index_name: str, export_path: str) -> bool:
    """
    Export a specific index to another location
    
    Args:
        index_name: Name of the index to export
        export_path: Path where to export the index
        
    Returns:
        True if successful
    """
    try:
        index_path = VECTOR_DB_DIR / index_name
        
        if not index_path.exists():
            logger.warning(f"Index not found: {index_name}")
            return False
        
        export_dir = Path(export_path)
        export_dir.mkdir(parents=True, exist_ok=True)
        
        target_path = export_dir / index_name
        shutil.copytree(index_path, target_path, dirs_exist_ok=True)
        
        logger.info(f"Exported index '{index_name}' to {target_path}")
        return True
    except Exception as e:
        logger.error(f"Error exporting index: {e}")
        return False


def import_index(index_name: str, import_path: str) -> bool:
    """
    Import an index from another location
    
    Args:
        index_name: Name for the imported index
        import_path: Path where the index is located
        
    Returns:
        True if successful
    """
    try:
        import_dir = Path(import_path)
        
        if not import_dir.exists():
            logger.warning(f"Import path not found: {import_path}")
            return False
        
        VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
        target_path = VECTOR_DB_DIR / index_name
        
        if target_path.exists():
            logger.warning(f"Index '{index_name}' already exists, overwriting...")
            shutil.rmtree(target_path)
        
        shutil.copytree(import_dir, target_path)
        
        logger.info(f"Imported index '{index_name}' from {import_dir}")
        return True
    except Exception as e:
        logger.error(f"Error importing index: {e}")
        return False


def rename_index(old_name: str, new_name: str) -> bool:
    """
    Rename a FAISS index
    
    Args:
        old_name: Current index name
        new_name: New index name
        
    Returns:
        True if successful
    """
    try:
        old_path = VECTOR_DB_DIR / old_name
        new_path = VECTOR_DB_DIR / new_name
        
        if not old_path.exists():
            logger.warning(f"Index not found: {old_name}")
            return False
        
        if new_path.exists():
            logger.warning(f"Index already exists: {new_name}")
            return False
        
        old_path.rename(new_path)
        logger.info(f"Renamed index from '{old_name}' to '{new_name}'")
        return True
    except Exception as e:
        logger.error(f"Error renaming index: {e}")
        return False


def backup_database(backup_path: str) -> bool:
    """
    Create a backup of the entire vector database
    
    Args:
        backup_path: Path where to create the backup
        
    Returns:
        True if successful
    """
    try:
        if not VECTOR_DB_DIR.exists():
            logger.warning("Vector database directory not found")
            return False
        
        backup_dir = Path(backup_path)
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_destination = backup_dir / f"vector_db_backup_{timestamp}"
        
        shutil.copytree(VECTOR_DB_DIR, backup_destination)
        
        logger.info(f"Created database backup at {backup_destination}")
        return True
    except Exception as e:
        logger.error(f"Error creating database backup: {e}")
        return False


def get_index_summary() -> Dict[str, Any]:
    """
    Get summary information of all indexes
    
    Returns:
        Dictionary with summary data
    """
    try:
        indexes = list_indexes()
        summary = {
            'total_indexes': len(indexes),
            'indexes': {},
            'timestamp': datetime.now().isoformat()
        }
        
        for index_name in indexes:
            vector_store = load_vector_store(index_name)
            if vector_store:
                stats = index_stats(vector_store)
                summary['indexes'][index_name] = {
                    'vectors': stats.get('total_vectors', 0),
                    'type': stats.get('index_type', 'Unknown')
                }
        
        return summary
    except Exception as e:
        logger.error(f"Error getting index summary: {e}")
        return {}


def get_aggregated_metrics() -> Dict:
    """
    Get aggregated metrics and statistics for dashboard display
    
    Returns:
        Dictionary with aggregated metrics in tabular format
    """
    try:
        db_info = get_database_info()
        indexes = list_indexes()
        
        # Build aggregated metrics
        metrics = {
            'summary': {
                'total_indexes': db_info.get('total_indexes', 0),
                'total_vectors': db_info.get('total_vectors', 0),
                'total_size_mb': db_info.get('total_size_mb', 0),
                'timestamp': db_info.get('timestamp', '')
            },
            'by_index': [],
            'statistics': {
                'avg_vectors_per_index': 0,
                'avg_size_mb_per_index': 0,
                'largest_index': None,
                'smallest_index': None
            }
        }
        
        if indexes:
            # Build per-index metrics
            sizes = []
            vectors = []
            
            for idx_name in indexes:
                details = index_details(idx_name)
                if details:
                    metrics['by_index'].append({
                        'name': idx_name,
                        'vectors': details.get('total_vectors', 0),
                        'size_mb': details.get('size_mb', 0),
                        'type': details.get('index_type', 'Unknown'),
                        'modified': details.get('modified', '')
                    })
                    sizes.append(details.get('size_mb', 0))
                    vectors.append(details.get('total_vectors', 0))
            
            # Calculate statistics
            if vectors:
                metrics['statistics']['avg_vectors_per_index'] = round(sum(vectors) / len(vectors), 2)
            if sizes:
                metrics['statistics']['avg_size_mb_per_index'] = round(sum(sizes) / len(sizes), 2)
            
            # Find largest and smallest
            if metrics['by_index']:
                largest = max(metrics['by_index'], key=lambda x: x['vectors'])
                smallest = min(metrics['by_index'], key=lambda x: x['vectors'])
                metrics['statistics']['largest_index'] = largest['name']
                metrics['statistics']['smallest_index'] = smallest['name']
        
        logger.info("Generated aggregated metrics")
        return metrics
    except Exception as e:
        logger.error(f"Error generating aggregated metrics: {e}")
        return {}
