import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-016 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    transactions_df = pd.read_csv(transactions_path, skiprows=1)
    transactions_df["txn_date"] = pd.to_datetime(transactions_df["txn_date"], errors="coerce")

    transactions_df["day_of_week"] = transactions_df["txn_date"].dt.day_name()
    transactions_df["month"] = transactions_df["txn_date"].dt.month
    transactions_df["quarter"] = transactions_df["txn_date"].dt.quarter
    transactions_df["is_weekend"] = transactions_df["txn_date"].dt.dayofweek >= 5

    return transactions_df
