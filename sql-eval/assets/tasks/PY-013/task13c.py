import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-013 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    """
    Computes a rolling average of 'closing_balance' over the last 7 observations per account.
    """
    balances_df = pd.read_csv(balances_path, skiprows=1)

    # Ensure balance_date is datetime and closing_balance is numeric
    balances_df["balance_date"] = pd.to_datetime(balances_df["balance_date"])
    balances_df["closing_balance"] = pd.to_numeric(balances_df["closing_balance"])

    # Sort by account_id and balance_date for correct rolling average calculation
    balances_df = balances_df.sort_values(by=["account_id", "balance_date"]).copy()

    # Calculate a 7-observation rolling average of closing_balance per account
    balances_df["rolling_avg_7_obs"] = balances_df.groupby("account_id")["closing_balance"].rolling(window=7, min_periods=1).mean().reset_index(level=0, drop=True)

    return balances_df