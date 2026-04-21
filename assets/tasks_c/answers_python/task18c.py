import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-018 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    """
    Flags rows where 'txn_date' is earlier than 'account_open_date' after joining
    accounts and transactions.
    """
    accounts_df = pd.read_csv(accounts_path, skiprows=1)
    transactions_df = pd.read_csv(transactions_path, skiprows=1)

    # Ensure date columns are in datetime format
    accounts_df["account_open_date"] = pd.to_datetime(accounts_df["account_open_date"])
    transactions_df["txn_date"] = pd.to_datetime(transactions_df["txn_date"])

    # Merge accounts and transactions
    merged_df = pd.merge(transactions_df, accounts_df, on="account_id", how="left")

    # Flag transactions where txn_date is earlier than account_open_date
    merged_df["is_txn_before_account_open"] = merged_df["txn_date"] < merged_df["account_open_date"]

    return merged_df