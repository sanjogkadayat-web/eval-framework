import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-012 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    transactions_df = pd.read_csv(transactions_path, skiprows=1)
    transactions_df["txn_date"] = pd.to_datetime(transactions_df["txn_date"], errors="coerce")
    transactions_df["txn_amount"] = pd.to_numeric(transactions_df["txn_amount"], errors="coerce")

    transactions_df = transactions_df.sort_values(
        by=["account_id", "txn_date", "txn_id"], kind="stable"
    ).copy()

    amt = transactions_df["txn_amount"].fillna(0.0)
    transactions_df["running_total_txn_amount"] = amt.groupby(transactions_df["account_id"]).cumsum()

    return transactions_df
