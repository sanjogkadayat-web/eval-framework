import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-014 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    """
    Computes a rolling 7-day sum of 'txn_amount' for each account using a time-based window.
    """
    transactions_df = pd.read_csv(transactions_path, skiprows=1)

    # Ensure txn_date is datetime and txn_amount is numeric
    transactions_df["txn_date"] = pd.to_datetime(transactions_df["txn_date"])
    transactions_df["txn_amount"] = pd.to_numeric(transactions_df["txn_amount"])

    # Sort by account_id and txn_date for correct rolling sum calculation
    transactions_df = transactions_df.sort_values(by=["account_id", "txn_date", "txn_id"]).copy()

    # Set txn_date as index for rolling window operations
    transactions_df = transactions_df.set_index("txn_date")

    # Calculate a 7-day rolling sum of txn_amount per account
    transactions_df["rolling_7day_sum_txn_amount"] = transactions_df.groupby("account_id")["txn_amount"].rolling(
        "7D", closed="left"
    ).sum().reset_index(level=0, drop=True)

    transactions_df = transactions_df.reset_index()
    return transactions_df