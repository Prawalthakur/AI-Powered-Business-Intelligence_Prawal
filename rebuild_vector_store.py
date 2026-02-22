#!/usr/bin/env python3
"""
Rebuild vector store for sales_data.csv with current actual data
"""

from pathlib import Path
from src.loaders import load_uploaded_file
from src.database import create_vector_store, save_vector_store
import shutil
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

csv_file = Path('data/raw/sales_data.csv')

if not csv_file.exists():
    print(f"ERROR: {csv_file} not found")
    exit(1)

print(f"Loading {csv_file}...")
documents, file_type = load_uploaded_file(str(csv_file))

if not documents:
    print("ERROR: Could not load documents")
    exit(1)

print(f"✓ Loaded {len(documents)} document chunks")

# Backup old vector store
old_vector_store = Path('vector_db/sales_data')
backup_path = Path('vector_db/sales_data_backup_old')
if old_vector_store.exists():
    if backup_path.exists():
        shutil.rmtree(backup_path)
    shutil.move(str(old_vector_store), str(backup_path))
    print(f"✓ Backed up old vector store to {backup_path}")

print("Creating new FAISS vector store...")
vector_store = create_vector_store(documents, 'sales_data')

if not vector_store:
    print("ERROR: Could not create vector store")
    exit(1)

print("✓ Created FAISS vector store")

print("Saving vector store to disk...")
save_vector_store(vector_store, 'sales_data')
print("✓ Saved vector store")

print("\n" + "=" * 60)
print("SUCCESS: Vector store rebuilt with current sales_data.csv")
print("=" * 60)
print(f"Documents in vector store: {len(documents)}")
print("\nYou can now use the chat feature with accurate data!")
