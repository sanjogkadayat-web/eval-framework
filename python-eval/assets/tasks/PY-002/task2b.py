import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-002 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame | None:
    accounts_df = pd.read_csv(accounts_path, skiprows=1)
    transactions_df = pd.read_csv(transactions_path, skiprows=1)
    balances_df = pd.read_csv(balances_path, skiprows=1)

    # Dates
    accounts_df["account_open_date"] = pd.to_datetime(accounts_df["account_open_date"], errors="raise")
    transactions_df["txn_date"] = pd.to_datetime(transactions_df["txn_date"], errors="raise")
    balances_df["balance_date"] = pd.to_datetime(balances_df["balance_date"], errors="raise")

    # Numerics
    transactions_df["txn_amount"] = pd.to_numeric(transactions_df["txn_amount"], errors="raise")
    balances_df["closing_balance"] = pd.to_numeric(balances_df["closing_balance"], errors="raise")
    balances_df["txn_count_day"] = pd.to_numeric(balances_df["txn_count_day"], errors="raise")

    print("All date and numeric columns validated successfully.")
    return None
