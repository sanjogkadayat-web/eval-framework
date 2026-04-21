import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-017 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    accounts_df = pd.read_csv(accounts_path, skiprows=1)
    transactions_df = pd.read_csv(transactions_path, skiprows=1)
    balances_df = pd.read_csv(balances_path, skiprows=1)

    rows_accounts = len(accounts_df)
    rows_txns = len(transactions_df)
    rows_balances = len(balances_df)

    merged_1 = transactions_df.merge(accounts_df, on="account_id", how="left")
    if len(merged_1) != rows_txns:
        raise AssertionError("Expected left-join to preserve transaction row count.")

    merged_2 = merged_1.merge(balances_df, on="account_id", how="left", suffixes=("", "_balance"))
    if len(merged_2) < len(merged_1) and rows_balances > 0:
        raise AssertionError("Expected merge with balances to not reduce row count for left join.")

    if rows_accounts < 0 or rows_txns < 0 or rows_balances < 0:
        raise AssertionError("Row counts must be non-negative.")

    return merged_2
