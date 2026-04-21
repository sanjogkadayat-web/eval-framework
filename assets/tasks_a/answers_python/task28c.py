import pandas as pd
from pathlib import Path
from datetime import timedelta

# SYNTHETIC DATA — no real financial data
# Task: PY-028 | Tier: Hard
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    """
    Flags likely churned accounts with no transactions in the last N days relative to
    the dataset's latest transaction date.
    """
    accounts_df = pd.read_csv(accounts_path, skiprows=1)
    transactions_df = pd.read_csv(transactions_path, skiprows=1)

    # Ensure date columns are in datetime format
    transactions_df["txn_date"] = pd.to_datetime(transactions_df["txn_date"])

    # Define N days for churn (e.g., 90 days)
    N_DAYS_CHURN = 90

    # Determine the latest transaction date in the entire dataset
    # If transactions_df is empty, reference_date will be set to a default value and no churn will be detected.
    if not transactions_df.empty:
        latest_dataset_date = transactions_df["txn_date"].max()
    else:
        latest_dataset_date = pd.to_datetime("2024-12-31") # Synthetic reference date if no transactions

    # Calculate the date N days before the latest dataset date
    churn_threshold_date = latest_dataset_date - timedelta(days=N_DAYS_CHURN)

    # Find the last transaction date for each account, using txn_id as a tie-breaker
    last_txn_date_per_account = transactions_df.sort_values(by=["txn_date", "txn_id"]).groupby("account_id")["txn_date"].last().reset_index()
    last_txn_date_per_account.rename(columns={"txn_date": "last_txn_date"}, inplace=True)

    # Merge with accounts_df
    accounts_with_last_txn = pd.merge(accounts_df, last_txn_date_per_account, on="account_id", how="left")

    # Flag churned accounts
    # An account is churned if:
    # 1. It has no transactions (last_txn_date is NaT)
    # 2. Its last transaction was before the churn_threshold_date
    accounts_with_last_txn["is_churned"] = (
        accounts_with_last_txn["last_txn_date"].isnull()
        | (accounts_with_last_txn["last_txn_date"] < churn_threshold_date)
    )

    return accounts_with_last_txn