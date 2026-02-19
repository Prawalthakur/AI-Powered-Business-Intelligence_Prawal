"""
Aggregated metrics tool for sales CSV data.
Builds grouped summaries and saves them to a pickle file.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple, List, Optional
import pickle

import pandas as pd
from langchain_core.documents import Document

from src.config import RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.summary_metrics import preprocess_sales_data


DEFAULT_INPUT = RAW_DATA_DIR / "sales_data.csv"
DEFAULT_OUTPUT = PROCESSED_DATA_DIR / "aggregated_metrics.pkl"


def load_aggregated_metrics(pkl_path: Optional[Path] = None) -> Dict[str, pd.DataFrame]:
    """Load aggregated metrics dictionary from a pickle file."""
    pkl_path = pkl_path or DEFAULT_OUTPUT
    if not pkl_path.exists():
        return {}

    try:
        with pkl_path.open("rb") as handle:
            data = pickle.load(handle)
        if isinstance(data, dict):
            return data
    except Exception:
        return {}

    return {}


def format_aggregated_metrics_context(
    metrics: Dict[str, pd.DataFrame],
    query: Optional[str] = None,
    max_rows: int = 5,
    max_tables: int = 4
) -> str:
    """Build a short prompt-friendly summary from aggregated metrics tables."""
    if not metrics:
        return ""

    query_text = (query or "").lower()
    table_order = []

    keyword_map = {
        "region": ["sales_by_region", "sales_by_region_gender", "satisfaction_by_region"],
        "gender": ["sales_by_gender", "sales_by_region_gender"],
        "product": ["sales_by_product"],
        "month": ["sales_by_month"],
        "time": ["sales_by_month"],
        "age": ["sales_by_age_group"],
        "satisfaction": ["satisfaction_by_region"],
    }

    if query_text:
        for keyword, tables in keyword_map.items():
            if keyword in query_text:
                table_order.extend(tables)

    if not table_order:
        table_order = list(metrics.keys())

    lines = ["Aggregated metrics (from PKL):"]
    added = 0
    for name in table_order:
        df = metrics.get(name)
        if df is None or df.empty:
            continue
        head = df.head(max_rows).to_string(index=False)
        lines.append(f"{name} (rows={len(df)}):\n{head}")
        added += 1
        if added >= max_tables:
            break

    return "\n".join(lines)


def aggregated_metrics_to_documents(
    metrics: Dict[str, pd.DataFrame],
    source: str = "aggregated_metrics.pkl",
    max_rows: int = 20
) -> List[Document]:
    """Convert aggregated metrics tables into LangChain documents."""
    documents: List[Document] = []
    if not metrics:
        return documents

    for name, df in metrics.items():
        if df is None or df.empty:
            continue
        preview = df.head(max_rows).to_string(index=False)
        if len(df) > max_rows:
            preview = preview + f"\n... (showing {max_rows} of {len(df)} rows)"
        content = f"Aggregated table: {name}\nRows: {len(df)}\n\n{preview}"
        documents.append(Document(page_content=content, metadata={"source": source, "table": name}))

    return documents


def _safe_group_sum(df: pd.DataFrame, group_col: str, value_col: str = "Sales") -> pd.DataFrame:
    if group_col not in df.columns or value_col not in df.columns:
        return pd.DataFrame()
    return (
        df.groupby(group_col, dropna=False, observed=False)[value_col]
        .sum()
        .reset_index()
        .rename(columns={value_col: "Total_Sales"})
        .sort_values("Total_Sales", ascending=False)
    )


def _safe_group_stats(df: pd.DataFrame, group_col: str, value_col: str = "Sales") -> pd.DataFrame:
    if group_col not in df.columns or value_col not in df.columns:
        return pd.DataFrame()
    return (
        df.groupby(group_col, dropna=False, observed=False)[value_col]
        .agg(["sum", "mean", "count"])
        .reset_index()
        .rename(columns={"sum": "Total_Sales", "mean": "Avg_Sales", "count": "Txn_Count"})
        .sort_values("Total_Sales", ascending=False)
    )


def build_aggregated_metrics(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Build aggregated sales metrics as DataFrames."""
    df = preprocess_sales_data(df.copy())

    metrics: Dict[str, pd.DataFrame] = {
        "sales_by_region": _safe_group_sum(df, "Region"),
        "sales_by_gender": _safe_group_stats(df, "Customer_Gender"),
        "sales_by_product": _safe_group_stats(df, "Product"),
    }

    # Time period (month) aggregation
    if "YearMonth" in df.columns and "Sales" in df.columns:
        monthly = (
            df.groupby("YearMonth", dropna=False)["Sales"]
            .sum()
            .reset_index()
            .rename(columns={"Sales": "Total_Sales"})
        )
        monthly["YearMonth"] = monthly["YearMonth"].astype(str)
        metrics["sales_by_month"] = monthly.sort_values("YearMonth")
    else:
        metrics["sales_by_month"] = pd.DataFrame()

    # Customer demographics
    metrics["sales_by_age_group"] = _safe_group_stats(df, "Age_Group")

    # Regional + gender segmentation
    if {"Region", "Customer_Gender", "Sales"}.issubset(df.columns):
        by_region_gender = (
            df.groupby(["Region", "Customer_Gender"], dropna=False)["Sales"]
            .sum()
            .reset_index()
            .rename(columns={"Sales": "Total_Sales"})
            .sort_values("Total_Sales", ascending=False)
        )
        metrics["sales_by_region_gender"] = by_region_gender
    else:
        metrics["sales_by_region_gender"] = pd.DataFrame()

    # Customer satisfaction by segment
    if {"Customer_Satisfaction", "Region"}.issubset(df.columns):
        metrics["satisfaction_by_region"] = (
            df.groupby("Region", dropna=False)["Customer_Satisfaction"]
            .mean()
            .reset_index()
            .rename(columns={"Customer_Satisfaction": "Avg_Satisfaction"})
            .sort_values("Avg_Satisfaction", ascending=False)
        )
    else:
        metrics["satisfaction_by_region"] = pd.DataFrame()

    return metrics


def save_aggregated_metrics(metrics: Dict[str, pd.DataFrame], output_path: Path) -> Path:
    """Save aggregated metrics dictionary to a pickle file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as handle:
        pickle.dump(metrics, handle)
    return output_path


def build_aggregated_metrics_from_csv(
    csv_path: Path | None = None,
    output_path: Path | None = None
) -> Tuple[Path, Dict[str, pd.DataFrame]]:
    """Load CSV, build aggregated metrics, and save to pickle."""
    csv_path = csv_path or DEFAULT_INPUT
    output_path = output_path or DEFAULT_OUTPUT

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    df = pd.read_csv(csv_path)
    metrics = build_aggregated_metrics(df)
    output_path = save_aggregated_metrics(metrics, output_path)
    return output_path, metrics
