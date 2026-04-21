import pandas as pd
from pathlib import Path
from datetime import timedelta

# SYNTHETIC DATA — no real financial data
# Task: PY-027 | Tier: Hard
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    """
    Calculates RFM (Recency, Frequency, Monetary) scores for each account.
    - Recency: Days since last transaction.
    - Frequency: Total number of transactions.
    - Monetary: Sum of transaction amounts.
    """
    accounts_df = pd.read_csv(accounts_path, skiprows=1)
    transactions_df = pd.read_csv(transactions_path, skiprows=1)

    # Ensure date columns are in datetime format
    transactions_df["txn_date"] = pd.to_datetime(transactions_df["txn_date"])

    # Use the latest transaction date in the dataset as the reference date
    # If the dataset is empty, set a default reference date.
    if not transactions_df.empty:
        reference_date = transactions_df["txn_date"].max() + timedelta(days=1)
    else:
        reference_date = pd.to_datetime("2025-01-01")  # A sensible default if no transactions


    # Calculate Recency
    latest_txn_date = transactions_df.groupby("account_id")["txn_date"].max().reset_index()
    latest_txn_date["recency"] = (reference_date - latest_txn_date["txn_date"]).dt.days

    # Calculate Frequency and Monetary
    rf_df = transactions_df.groupby("account_id").agg(
        frequency=("txn_id", "count"),
        monetary=("txn_amount", "sum")
    ).reset_index()

    # Merge RFM components
    rfm_df = pd.merge(accounts_df[["account_id", "customer_segment", "region"]], latest_txn_date[["account_id", "recency"]], on="account_id", how="left")
    rfm_df = pd.merge(rfm_df, rf_df, on="account_id", how="left")

    # Handle accounts with no transactions (fillna for recency, frequency, monetary)
    rfm_df["recency"] = rfm_df["recency"].fillna((reference_date - accounts_df["account_open_date"]).dt.days.max()) # Max days for no txns
    rfm_df["frequency"] = rfm_df["frequency"].fillna(0)
    rfm_df["monetary"] = rfm_df["monetary"].fillna(0)

    return rfm_df