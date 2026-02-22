#!/usr/bin/env python3
"""
Deep inspect the FAISS vector store and its docstore
"""

import os
from pathlib import Path
from langchain_community.vectorstores import FAISS
from src.llm import get_embeddings

os.chdir(Path(__file__).parent)

embeddings = get_embeddings()
store_path = 'vector_db/sales_data'

print(f"Loading FAISS store from {store_path}...")
store = FAISS.load_local(
    folder_path=store_path,
    embeddings=embeddings,
    allow_dangerous_deserialization=True
)

print(f"Store loaded successfully")

# Check docstore
if hasattr(store, 'docstore'):
    docstore = store.docstore
    print(f"\nDocstore type: {type(docstore)}")
    print(f"Docstore _dict length: {len(docstore._dict) if hasattr(docstore, '_dict') else 'N/A'}")
    
    # Get first few doc IDs and their content
    if hasattr(docstore, '_dict'):
        keys = list(docstore._dict.keys())[:3]
        print(f"\nFirst 3 documents:")
        for key in keys:
            doc = docstore._dict[key]
            print(f"  ID {key}: {str(doc)[:150]}...")

# Check index_to_docstore_id mapping
if hasattr(store, 'index_to_docstore_id'):
    mapping = store.index_to_docstore_id
    print(f"\nIndex-to-docstore mapping length: {len(mapping)}")
    print(f"First 3 mappings: {list(mapping.items())[:3]}")

# Try a similarity search
print("\n" + "=" * 60)
print("Testing similarity search...")
results = store.similarity_search("total sales", k=2)
print(f"Found {len(results)} results")
for i, doc in enumerate(results):
    print(f"\nResult {i+1}:")
    print(f"  Content (first 200 chars): {doc.page_content[:200]}")
    print(f"  Metadata: {doc.metadata}")
