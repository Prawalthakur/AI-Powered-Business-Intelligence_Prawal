#!/usr/bin/env python3
"""
Analyze the actual date range in sales_data.csv
"""

import pandas as pd

df = pd.read_csv('data/raw/sales_data.csv')

# Convert to datetime
df['Date_obj'] = pd.to_datetime(df['Date'], format='mixed', dayfirst=True, errors='coerce')

print("=" * 60)
print("CSV DATA ANALYSIS")
print("=" * 60)
print(f'\nTotal rows: {len(df)}')
print(f'\nDate range:')
print(f'  Min: {df["Date_obj"].min()}')
print(f'  Max: {df["Date_obj"].max()}')

# Show date distribution
print(f'\nRows by year:')
yearly = df['Date_obj'].dt.year.value_counts().sort_index()
for year, count in yearly.items():
    print(f'  {year}: {count} rows')

# Check for rows with high sales values (like the 666666 outlier)
print(f'\nHigh sales transactions (>100,000):')
high_sales = df[df['Sales'] > 100000][['Date', 'Sales', 'Product', 'Region']]
print(high_sales)

# Check first 10 and last 10 dates
print(f'\nFirst 10 dates:')
print(df['Date'].iloc[:10].tolist())
print(f'\nLast 10 dates:')
print(df['Date'].iloc[-10:].tolist())
