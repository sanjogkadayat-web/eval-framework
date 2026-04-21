import numpy as np
import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-025 | Tier: Hard
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    transactions_df = pd.read_csv(transactions_path, skiprows=1)
    transactions_df["txn_date"] = pd.to_datetime(transactions_df["txn_date"], errors="coerce")
    transactions_df["txn_amount"] = pd.to_numeric(transactions_df["txn_amount"], errors="coerce")

    transactions_df = transactions_df.dropna(subset=["txn_amount"]).copy()
    if transactions_df.empty:
        transactions_df["rolling_z_score"] = np.nan
        transactions_df["is_anomaly"] = False
        return transactions_df

    transactions_df = transactions_df.sort_values(
        by=["account_id", "txn_date", "txn_id"], kind="stable"
    ).copy()

    window_size = 7
    z_thresh = 2.0

    rolling_mean = (
        transactions_df.groupby("account_id", dropna=False)["txn_amount"]
        .rolling(window=window_size, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )
    rolling_std = (
        transactions_df.groupby("account_id", dropna=False)["txn_amount"]
        .rolling(window=window_size, min_periods=1)
        .std()
        .reset_index(level=0, drop=True)
    )

    transactions_df["rolling_z_score"] = np.where(
        rolling_std == 0,
        0.0,
        (transactions_df["txn_amount"] - rolling_mean) / rolling_std,
    )
    transactions_df["is_anomaly"] = transactions_df["rolling_z_score"].abs() > z_thresh

    return transactions_df
