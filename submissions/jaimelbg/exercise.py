"""
Environment setup verification exercise.

Fill in every TODO below. Do not rename functions, change their signatures, or
remove imports — the autograder calls these functions directly by name.

Self-check locally before opening your PR:

    uv run pytest tests/test_exercise.py -v

Where to put this file: copy it to submissions/<your-github-username>/exercise.py
(see the repo README for the full workflow) and edit the copy, not this template.
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
    """Return the per-order revenue (quantity * unit_price) as a NumPy array.

    Must be a vectorized operation - no Python-level for loop.
    """
    array = np.multiply(quantities, unit_prices)
    return array


def numpy_average_order_value(quantities: np.ndarray, unit_prices: np.ndarray) -> float:
    """Return the average revenue across all orders, as a plain float."""
    array = np.multiply(quantities, unit_prices)
    return np.mean(array)


# ---------------------------------------------------------------------------
# 2. Pandas
# ---------------------------------------------------------------------------
def pandas_revenue_by_region(sales: pd.DataFrame) -> pd.DataFrame:
    """Given the sales DataFrame (columns include region, quantity, unit_price),
    return a DataFrame with columns ["region", "revenue"] — total revenue per
    region, where revenue = quantity * unit_price.
    """
    sales = sales.copy()
    sales["revenue"] = sales["quantity"] * sales["unit_price"]
    result = sales.groupby("region", as_index=False)["revenue"].sum()
    
    return result


def pandas_region_share(sales: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame with columns ["region", "revenue", "share"], where
    `share` is that region's revenue divided by total revenue across all
    regions (values should sum to 1.0).

    Build this by merging the per-region totals from pandas_revenue_by_region()
    with the grand total (rather than hand-computing division in a loop).
    """
    by_region = pandas_revenue_by_region(sales)

    grand_total = by_region["revenue"].sum()
    totals = pd.DataFrame({"total_revenue": [grand_total]})

    result = by_region.merge(totals, how="cross")
    result["share"] = result["revenue"] / result["total_revenue"]

    return result


# ---------------------------------------------------------------------------
# 3. SQL
# ---------------------------------------------------------------------------
def sql_revenue_by_region(csv_path: Path) -> pd.DataFrame:
    """Load the sales data from `csv_path` into an in-memory SQLite table named
    "sales", then return a DataFrame with columns ["region", "revenue"] — the
    SQL equivalent of pandas_revenue_by_region(), computed with a SQL GROUP BY
    query (not by loading the table and using pandas groupby).
    """
    sales = pd.read_csv(csv_path)
    with sqlite3.connect(":memory:") as connection:
        sales.to_sql("sales", connection, index=False, if_exists="replace")
        return pd.read_sql(
            """
            SELECT
                region,
                SUM(quantity * unit_price) AS revenue
            FROM sales
            GROUP BY region
            """,
            connection,
        )
# ---------------------------------------------------------------------------
# 4. Deep learning stack check
# ---------------------------------------------------------------------------
def check_torch_installed() -> float:
    """Prove torch is installed and working: build a 1-D tensor [1.0, 2.0, 3.0]
    and return the sum of its elements as a plain float.
    """
    tensor = torch.tensor([1.0, 2.0, 3.0])
    return tensor.sum().item()
    


if __name__ == "__main__":
    sales = pd.read_csv(DATA_DIR / "sales.csv")

    quantities = sales["quantity"].to_numpy()
    unit_prices = sales["unit_price"].to_numpy()

    print("Average order value:", numpy_average_order_value(quantities, unit_prices))
    print("\nRevenue by region:\n", pandas_revenue_by_region(sales))
    print("\nRegion share:\n", pandas_region_share(sales))
    print("\nSQL revenue by region:\n", sql_revenue_by_region(DATA_DIR / "sales.csv"))
    print("\ntorch check (expect 6.0):", check_torch_installed())
