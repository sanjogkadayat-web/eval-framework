import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-001 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    """
    Loads the accounts CSV file, skips the synthetic header row, and asserts the expected five column names.
    """
    accounts_df = pd.read_csv(accounts_path, skiprows=1)

    expected_columns = [
        "account_id",
        "customer_segment",
        "account_open_date",
        "account_status",
        "region",
    ]

    if list(accounts_df.columns) != expected_columns:
        raise AssertionError(f"Expected columns {expected_columns}, but got {list(accounts_df.columns)}")

    return accounts_df