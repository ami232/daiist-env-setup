"""
Environment setup verification exercise.
"""

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
import torch


def _find_repo_root(start: Path) -> Path:
    """Walk upward from `start` until a directory containing data/ is found."""
    for candidate in [start, *start.parents]:
        if (candidate / "data").is_dir():
            return candidate
    raise FileNotFoundError("Could not locate the repo's data/ directory")


DATA_DIR = _find_repo_root(Path(__file__).resolve()) / "data"


# ---------------------------------------------------------------------------
# 1. NumPy
# ---------------------------------------------------------------------------
def numpy_order_revenues(quantities: np.ndarray, unit_prices: np.ndarray) -> np.ndarray:
    """Return the per-order revenue (quantity * unit_price) as a NumPy array."""
    return quantities * unit_prices


def numpy_average_order_value(quantities: np.ndarray, unit_prices: np.ndarray) -> float:
    """Return the average revenue across all orders, as a plain float."""
    return float(numpy_order_revenues(quantities, unit_prices).mean())


# ---------------------------------------------------------------------------
# 2. Pandas
# ---------------------------------------------------------------------------
def pandas_revenue_by_region(sales: pd.DataFrame) -> pd.DataFrame:
    """Total revenue per region."""
    return (
        sales.assign(revenue=sales["quantity"] * sales["unit_price"])
        .groupby("region", as_index=False)["revenue"]
        .sum()
    )


def pandas_region_share(sales: pd.DataFrame) -> pd.DataFrame:
    """Per-region revenue plus its share of the grand total."""
    by_region = pandas_revenue_by_region(sales)
    grand_total = pd.DataFrame(
        {"_k": [1], "total_revenue": [by_region["revenue"].sum()]}
    )
    merged = by_region.assign(_k=1).merge(grand_total, on="_k")
    merged["share"] = merged["revenue"] / merged["total_revenue"]
    return merged[["region", "revenue", "share"]]


# ---------------------------------------------------------------------------
# 3. SQL
# ---------------------------------------------------------------------------
def sql_revenue_by_region(csv_path: Path) -> pd.DataFrame:
    """Same as pandas_revenue_by_region(), but computed with a SQL GROUP BY."""
    sales = pd.read_csv(csv_path)
    with sqlite3.connect(":memory:") as connection:
        sales.to_sql("sales", connection, index=False, if_exists="replace")
        return pd.read_sql(
            """
            SELECT region, SUM(quantity * unit_price) AS revenue
            FROM sales
            GROUP BY region
            ORDER BY region
            """,
            connection,
        )


# ---------------------------------------------------------------------------
# 4. Deep learning stack check
# ---------------------------------------------------------------------------
def check_torch_installed() -> float:
    """Build a 1-D tensor [1.0, 2.0, 3.0] and return the sum of its elements."""
    return float(torch.tensor([1.0, 2.0, 3.0]).sum())


if __name__ == "__main__":
    sales = pd.read_csv(DATA_DIR / "sales.csv")

    quantities = sales["quantity"].to_numpy()
    unit_prices = sales["unit_price"].to_numpy()

    print("Average order value:", numpy_average_order_value(quantities, unit_prices))
    print("\nRevenue by region:\n", pandas_revenue_by_region(sales))
    print("\nRegion share:\n", pandas_region_share(sales))
    print("\nSQL revenue by region:\n", sql_revenue_by_region(DATA_DIR / "sales.csv"))
    print("\ntorch check (expect 6.0):", check_torch_installed())