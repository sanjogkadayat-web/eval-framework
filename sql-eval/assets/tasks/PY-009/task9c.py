import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-009 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    """
    Fills null 'txn_amount' values with the median 'txn_amount' of the file.
    """
    transactions_df = pd.read_csv(transactions_path, skiprows=1)

    median_txn_amount = transactions_df["txn_amount"].median()
    transactions_df["txn_amount"] = transactions_df["txn_amount"].fillna(median_txn_amount)

    return transactions_df