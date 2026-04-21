import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-006 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    accounts_df = pd.read_csv(accounts_path, skiprows=1)

    string_cols = ["account_id", "customer_segment", "account_status", "region"]
    for col in string_cols:
        if col in accounts_df.columns:
            accounts_df[col] = accounts_df[col].astype("string").str.strip()

    for col in ["region", "customer_segment"]:
        if col in accounts_df.columns:
            accounts_df[col] = accounts_df[col].str.upper()

    return accounts_df
