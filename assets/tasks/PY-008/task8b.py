import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-008 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    accounts_df = pd.read_csv(accounts_path, skiprows=1)
    transactions_df = pd.read_csv(transactions_path, skiprows=1)
    transactions_df["txn_amount"] = pd.to_numeric(transactions_df["txn_amount"], errors="coerce")

    merged_df = pd.merge(accounts_df, transactions_df, on="account_id", how="inner")

    pivot_table = pd.pivot_table(
        merged_df,
        values="txn_amount",
        index="region",
        columns="channel",
        aggfunc="sum",
        fill_value=0,
    )

    return pivot_table
