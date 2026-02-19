"""
Build aggregated metrics pickle from a sales CSV file.

Usage:
  .\.venv\Scripts\python.exe .\scripts\build_agg_metrics.py --data data\raw\sales_data.csv
"""

import argparse
from pathlib import Path

from src.metrics_tool import build_aggregated_metrics_from_csv


def main() -> int:
    parser = argparse.ArgumentParser(description="Build aggregated metrics pickle")
    parser.add_argument("--data", type=str, default="data/raw/sales_data.csv")
    parser.add_argument("--output", type=str, default="data/processed/aggregated_metrics.pkl")
    args = parser.parse_args()

    csv_path = Path(args.data)
    output_path = Path(args.output)

    output_path, metrics = build_aggregated_metrics_from_csv(csv_path, output_path)

    print(f"Saved aggregated metrics to {output_path}")
    print(f"Sections: {', '.join(metrics.keys())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
