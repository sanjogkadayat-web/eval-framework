import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-007 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    """
    Groups transactions by txn_type and computes total txn_amount and row count.
    """
    transactions_df = pd.read_csv(transactions_path, skiprows=1)

    grouped_df = transactions_df.groupby("txn_type").agg(
        total_txn_amount=("txn_amount", "sum"),
        transaction_count=("txn_id", "count"),
    ).reset_index()

    return grouped_df