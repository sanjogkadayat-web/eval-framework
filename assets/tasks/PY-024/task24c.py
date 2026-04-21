import pandas as pd
from pathlib import Path
import numpy as np

# SYNTHETIC DATA — no real financial data
# Task: PY-024 | Tier: Hard
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    """
    Implements SCD Type 2 history tracking for account_status changes across account snapshots.
    A new record is created for each change in account_status, with effective start and end dates.
    """
    accounts_df = pd.read_csv(accounts_path, skiprows=1)

    # Ensure account_open_date is datetime
    accounts_df["account_open_date"] = pd.to_datetime(accounts_df["account_open_date"])

    # Add temporary status_rank for deterministic sorting in case of same account_id and account_open_date
    status_precedence = {"ACTIVE": 1, "SUSPENDED": 2, "CLOSED": 3}
    accounts_df["status_rank"] = accounts_df["account_status"].map(status_precedence)
    
    # Sort by account_id, account_open_date, and then by status_rank for deterministic historical order
    accounts_df = accounts_df.sort_values(by=["account_id", "account_open_date", "status_rank", "customer_segment", "region"]).reset_index(drop=True)

    # Identify changes in account_status for each account_id
    # Shift 'account_status' to get the previous status for comparison
    accounts_df["prev_account_status"] = accounts_df.groupby("account_id")["account_status"].shift(1)

    # Flag rows where status changes or it's the first record for an account
    accounts_df["is_new_status"] = (
        (accounts_df["account_status"] != accounts_df["prev_account_status"])
        | (accounts_df["prev_account_status"].isnull())
    )

    # Filter to only keep rows where a new status begins
    scd2_df = accounts_df[accounts_df["is_new_status"]].drop(columns=["prev_account_status", "is_new_status", "status_rank"]).copy()

    # Define effective_start_date
    scd2_df["effective_start_date"] = scd2_df["account_open_date"]

    # Calculate effective_end_date
    # For each account, the end date of the current record is one day before the start date of the next record
    scd2_df["next_start_date"] = scd2_df.groupby("account_id")["effective_start_date"].shift(-1)
    scd2_df["effective_end_date"] = scd2_df["next_start_date"] - pd.Timedelta(days=1)

    # For the current active record (the last one for each account_id), set end_date to a far future date
    scd2_df["effective_end_date"] = scd2_df["effective_end_date"].fillna(pd.to_datetime("9999-12-31"))

    # Select relevant columns for the SCD Type 2 table
    final_scd2_df = scd2_df[
        ["account_id", "customer_segment", "account_status", "region", "effective_start_date", "effective_end_date"]
    ]

    return final_scd2_df