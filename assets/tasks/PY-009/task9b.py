import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-009 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    transactions_df = pd.read_csv(transactions_path, skiprows=1)
    transactions_df["txn_amount"] = pd.to_numeric(transactions_df["txn_amount"], errors="coerce")

    median_amount = transactions_df["txn_amount"].median(skipna=True)
    transactions_df["txn_amount"] = transactions_df["txn_amount"].fillna(median_amount)

    return transactions_df
