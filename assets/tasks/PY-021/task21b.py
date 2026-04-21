import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-021 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    accounts_df = pd.read_csv(accounts_path, skiprows=1)
    accounts_df["account_open_date"] = pd.to_datetime(accounts_df["account_open_date"], errors="coerce")

    accounts_df["cohort_month"] = accounts_df["account_open_date"].dt.to_period("M").dt.to_timestamp()
    return accounts_df
