import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-008 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    """
    Builds a pivot table of total txn_amount by region and channel.
    """
    accounts_df = pd.read_csv(accounts_path, skiprows=1)
    transactions_df = pd.read_csv(transactions_path, skiprows=1)

    # Merge accounts and transactions to get region and channel together
    merged_df = pd.merge(accounts_df, transactions_df, on="account_id", how="inner")

    # Create a pivot table of total txn_amount by region and channel
    pivot_table = pd.pivot_table(
        merged_df,
        values="txn_amount",
        index="region",
        columns="channel",
        aggfunc="sum",
        fill_value=0
    )

    return pivot_table