import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-014 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    transactions_df = pd.read_csv(transactions_path, skiprows=1)
    transactions_df["txn_date"] = pd.to_datetime(transactions_df["txn_date"], errors="coerce")
    transactions_df["txn_amount"] = pd.to_numeric(transactions_df["txn_amount"], errors="coerce")

    transactions_df = transactions_df.sort_values(
        by=["account_id", "txn_date", "txn_id"], kind="stable"
    ).copy()

    transactions_df["rolling_7day_sum_txn_amount"] = pd.NA
    mask = transactions_df["account_id"].notna() & transactions_df["txn_date"].notna()
    if mask.any():
        sub = transactions_df.loc[mask, ["account_id", "txn_date", "txn_amount"]].copy()
        indexed = sub.set_index("txn_date")
        rolling = (
            indexed.groupby("account_id")["txn_amount"]
            .rolling("7D", closed="left")
            .sum()
            .reset_index(level=0, drop=True)
        )
        transactions_df.loc[mask, "rolling_7day_sum_txn_amount"] = rolling.to_numpy()

    return transactions_df
