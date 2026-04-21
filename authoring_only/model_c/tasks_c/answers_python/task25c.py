import pandas as pd
from pathlib import Path
import numpy as np

# SYNTHETIC DATA — no real financial data
# Task: PY-025 | Tier: Hard
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    """
    Flags rolling z-score anomalies in 'txn_amount' within each account using a moving window.
    Anomalies are flagged if the absolute z-score exceeds a threshold (default 2).
    """
    transactions_df = pd.read_csv(transactions_path, skiprows=1)

    # Ensure txn_date is datetime and txn_amount is numeric
    transactions_df["txn_date"] = pd.to_datetime(transactions_df["txn_date"])
    transactions_df["txn_amount"] = pd.to_numeric(transactions_df["txn_amount"], errors='coerce')

    # Drop rows with NaN txn_amount after conversion, as they cannot be used for z-score calculation
    transactions_df.dropna(subset=["txn_amount"], inplace=True)

    if transactions_df.empty:
        transactions_df["rolling_z_score"] = np.nan
        transactions_df["is_anomaly"] = False
        return transactions_df

    # Sort by account_id and txn_date for correct rolling calculations
    transactions_df = transactions_df.sort_values(by=["account_id", "txn_date", "txn_id"]).copy()

    # Define rolling window size (e.g., 7 observations)
    window_size = 7
    z_score_threshold = 2

    # Calculate rolling mean and standard deviation of txn_amount per account
    transactions_df["rolling_mean"] = transactions_df.groupby("account_id")["txn_amount"].rolling(
        window=window_size, min_periods=1
    ).mean().reset_index(level=0, drop=True)

    transactions_df["rolling_std"] = transactions_df.groupby("account_id")["txn_amount"].rolling(
        window=window_size, min_periods=1
    ).std().reset_index(level=0, drop=True)

    # Calculate rolling z-score
    # Handle cases where rolling_std might be 0 to avoid division by zero
    transactions_df["rolling_z_score"] = np.where(
        transactions_df["rolling_std"] == 0,
        0,  # If std is 0, z-score is 0 (no deviation)
        (transactions_df["txn_amount"] - transactions_df["rolling_mean"]) / transactions_df["rolling_std"]
    )

    # Flag anomalies based on z-score threshold
    transactions_df["is_anomaly"] = (
        transactions_df["rolling_z_score"].abs() > z_score_threshold
    )

    # Clean up intermediate columns
    transactions_df.drop(columns=["rolling_mean", "rolling_std"], inplace=True)

    return transactions_df