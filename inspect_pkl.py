#!/usr/bin/env python3
"""
Inspect the exact content of the vector store index.pkl
"""

import pickle
from pathlib import Path

pkl_path = Path('vector_db/sales_data/index.pkl')

if not pkl_path.exists():
    print(f"File not found: {pkl_path}")
    exit(1)

print("Loading pickle data...")
with open(pkl_path, 'rb') as f:
    data = pickle.load(f)

print(f"Type: {type(data)}")
print(f"Keys: {data.keys() if isinstance(data, dict) else 'N/A'}")

# If it's a dict with 'metadatas', show first few entries
if isinstance(data, dict) and 'metadatas' in data:
    metadatas = data['metadatas']
    print(f"\nNumber of documents: {len(metadatas)}")
    print("\nFirst 3 document metadatas:")
    for i, meta in enumerate(metadatas[:3]):
        print(f"  Doc {i}: {meta}")

# Also check if there's docstore/index data
if isinstance(data, dict):
    for key in data.keys():
        if 'document' in key.lower() or 'index' in key.lower():
            val = data[key]
            if hasattr(val, '__len__'):
                print(f"\n{key}: {len(val)} items")
