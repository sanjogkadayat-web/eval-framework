import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-018 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    accounts_df = pd.read_csv(accounts_path, skiprows=1)
    transactions_df = pd.read_csv(transactions_path, skiprows=1)

    accounts_df["account_open_date"] = pd.to_datetime(accounts_df["account_open_date"], errors="coerce")
    transactions_df["txn_date"] = pd.to_datetime(transactions_df["txn_date"], errors="coerce")

    merged = transactions_df.merge(
        accounts_df[["account_id", "account_open_date"]],
        on="account_id",
        how="left",
    )

    merged["txn_before_account_open"] = merged["txn_date"] < merged["account_open_date"]
    merged["txn_before_account_open"] = merged["txn_before_account_open"].fillna(False)

    return merged
