import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-007 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    transactions_df = pd.read_csv(transactions_path, skiprows=1)
    transactions_df["txn_amount"] = pd.to_numeric(transactions_df["txn_amount"], errors="coerce")

    out = (
        transactions_df.groupby("txn_type", dropna=False)
        .agg(total_txn_amount=("txn_amount", "sum"), row_count=("txn_id", "size"))
        .reset_index()
        .sort_values("txn_type", kind="stable")
        .reset_index(drop=True)
    )
    return out
