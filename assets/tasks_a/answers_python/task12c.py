import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-012 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    """
    Creates a running total of 'txn_amount' within each account, ordered by 'txn_date'.
    """
    transactions_df = pd.read_csv(transactions_path, skiprows=1)

    # Ensure txn_date is datetime and txn_amount is numeric
    transactions_df["txn_date"] = pd.to_datetime(transactions_df["txn_date"])
    transactions_df["txn_amount"] = pd.to_numeric(transactions_df["txn_amount"])

    # Sort by account_id and txn_date for correct running total calculation
    transactions_df = transactions_df.sort_values(by=["account_id", "txn_date", "txn_id"]).copy()

    # Calculate running total of txn_amount within each account
    transactions_df["running_total_txn_amount"] = transactions_df.groupby("account_id")["txn_amount"].cumsum()

    return transactions_df