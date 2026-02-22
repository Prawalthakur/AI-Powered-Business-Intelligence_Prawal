#!/usr/bin/env python3
"""
Diagnostic script to compare CSV sales data vs chat retrieval data
"""

import pandas as pd
from pathlib import Path
from src.summary_metrics import (
    load_sales_data, 
    preprocess_sales_data, 
    calculate_overall_sales_metrics,
    generate_summary_metrics
)
from src.database import load_vector_store, similarity_search_documents_only
from src.loaders import load_csv

# Load CSV directly
print("=" * 60)
print("CSV ACTUAL DATA")
print("=" * 60)
df = load_sales_data('data/raw/sales_data.csv')
df = preprocess_sales_data(df)
metrics = calculate_overall_sales_metrics(df)

print(f'Total Rows: {len(df):,}')
print(f'Total Sales: ${metrics.get("total_sales", 0):,.2f}')
print(f'Average Sale: ${metrics.get("average_sale", 0):.2f}')
print(f'Min Sale: ${df["Sales"].min():,.0f}')
print(f'Max Sale: ${df["Sales"].max():,.0f}')

# Load summary metrics
print("\n" + "=" * 60)
print("SUMMARY METRICS (From Cache/PKL)")
print("=" * 60)
summary = generate_summary_metrics()
if summary.get('status') == 'success':
    overall = summary.get('overall_metrics', {})
    print(f'Total Sales: ${overall.get("total_sales", 0):,.2f}')
    print(f'Average Sale: ${overall.get("average_sale", 0):.2f}')
    print(f'Transaction Count: {overall.get("transaction_count", 0):,}')
else:
    print("Error generating summary metrics")

# Check Vector Store
print("\n" + "=" * 60)
print("VECTOR STORE DOCUMENTS")
print("=" * 60)
store = load_vector_store('sales_data')
if store:
    try:
        # Test similarity search
        results = similarity_search_documents_only(store, "total sales revenue", k=5)
        print(f'Retrieved {len(results)} documents from vector store')
        if results:
            print("\nFirst document content (first 500 chars):")
            print(results[0].page_content[:500])
    except Exception as e:
        print(f"Error querying vector store: {e}")
else:
    print("No vector store found for 'sales_data'")

# Check CSV documents in vector store
print("\n" + "=" * 60)
print("CSV LOADING (as Documents)")
print("=" * 60)
csv_docs = load_csv('data/raw/sales_data.csv')
print(f'CSV loaded as {len(csv_docs)} documents')
if csv_docs:
    print(f"First doc content:\n{csv_docs[0].page_content[:200]}")
