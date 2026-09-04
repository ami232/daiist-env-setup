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


def numpy_order_revenues(quantities: np.ndarray, unit_prices: np.ndarray) -> np.ndarray:
    """Return the per-order revenue (quantity * unit_price) as a NumPy array."""
    return quantities * unit_prices


def numpy_average_order_value(quantities: np.ndarray, unit_prices: np.ndarray) -> float:
    """Return the average revenue across all orders, as a plain float."""
    return float(numpy_order_revenues(quantities, unit_prices).mean())


def pandas_revenue_by_region(sales: pd.DataFrame) -> pd.DataFrame:
    """Return total revenue per region."""
    sales_with_revenue = sales.assign(
        revenue=sales["quantity"] * sales["unit_price"]
    )

    return (
        sales_with_revenue
        .groupby("region", as_index=False)["revenue"]
        .sum()
    )


def pandas_region_share(sales: pd.DataFrame) -> pd.DataFrame:
    """Return region revenue and its share of total revenue."""
    region_totals = pandas_revenue_by_region(sales)

    region_totals = region_totals.assign(key=1)

    grand_total = pd.DataFrame({
        "key": [1],
        "total_revenue": [region_totals["revenue"].sum()]
    })

    result = region_totals.merge(grand_total, on="key")
    result["share"] = result["revenue"] / result["total_revenue"]

    return result[["region", "revenue", "share"]]


def sql_revenue_by_region(csv_path: Path) -> pd.DataFrame:
    """Calculate revenue by region using SQLite."""
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


def check_torch_installed() -> float:
    """Check that PyTorch works."""
    tensor = torch.tensor([1.0, 2.0, 3.0])
    return float(tensor.sum().item())


if __name__ == "__main__":
    sales = pd.read_csv(DATA_DIR / "sales.csv")

    quantities = sales["quantity"].to_numpy()
    unit_prices = sales["unit_price"].to_numpy()

    print("Average order value:", numpy_average_order_value(quantities, unit_prices))
    print("\nRevenue by region:\n", pandas_revenue_by_region(sales))
    print("\nRegion share:\n", pandas_region_share(sales))
    print("\nSQL revenue by region:\n", sql_revenue_by_region(DATA_DIR / "sales.csv"))
    print("\ntorch check (expect 6.0):", check_torch_installed())
