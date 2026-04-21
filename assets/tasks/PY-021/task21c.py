import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-021 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    """
    Assigns each account to a cohort based on the 'account_open_date' month.
    The cohort is represented as 'YYYY-MM'.
    """
    accounts_df = pd.read_csv(accounts_path, skiprows=1)

    # Ensure account_open_date is datetime
    accounts_df["account_open_date"] = pd.to_datetime(accounts_df["account_open_date"])

    # Create a cohort column based on the year and month of account_open_date
    accounts_df["cohort_month"] = accounts_df["account_open_date"].dt.to_period("M").astype(str)

    return accounts_df