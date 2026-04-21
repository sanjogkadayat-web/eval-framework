import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-028 | Tier: Hard
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    accounts_df = pd.read_csv(accounts_path, skiprows=1)
    transactions_df = pd.read_csv(transactions_path, skiprows=1)
    transactions_df["txn_date"] = pd.to_datetime(transactions_df["txn_date"], errors="coerce")

    n_days = 30
    max_date = transactions_df["txn_date"].max()

    last_txn = (
        transactions_df.dropna(subset=["account_id", "txn_date"])
        .groupby("account_id", dropna=False)["txn_date"]
        .max()
        .rename("last_txn_date")
        .reset_index()
    )

    out = accounts_df.merge(last_txn, on="account_id", how="left")
    out["days_since_last_txn"] = (max_date - out["last_txn_date"]).dt.days

    out["is_churned"] = out["days_since_last_txn"].gt(n_days) | out["last_txn_date"].isna()
    out["is_churned"] = out["is_churned"].fillna(True)

    return out
