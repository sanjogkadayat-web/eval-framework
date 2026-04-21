import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-017 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    """
    Builds a three-DataFrame merge pipeline across accounts, transactions, and daily_balances
    and asserts row counts at each step.
    """
    accounts_df = pd.read_csv(accounts_path, skiprows=1)
    transactions_df = pd.read_csv(transactions_path, skiprows=1)
    balances_df = pd.read_csv(balances_path, skiprows=1)

    # Convert date columns to datetime for accurate merging if needed
    accounts_df["account_open_date"] = pd.to_datetime(accounts_df["account_open_date"])
    transactions_df["txn_date"] = pd.to_datetime(transactions_df["txn_date"])
    balances_df["balance_date"] = pd.to_datetime(balances_df["balance_date"])

    # Sort for deterministic merging order if multiple matches exist
    transactions_df = transactions_df.sort_values(by=["account_id", "txn_date", "txn_id"]).copy()
    balances_df = balances_df.sort_values(by=["account_id", "balance_date", "txn_count_day"]).copy()

    # First merge: accounts and transactions
    # Using a left merge to keep all accounts, even if no transactions
    merged_acct_txn = pd.merge(accounts_df, transactions_df, on="account_id", how="left")
    print(f"Rows after accounts-transactions merge: {len(merged_acct_txn)}")
    assert len(merged_acct_txn) >= len(accounts_df), "Row count decreased unexpectedly after first merge"

    # Second merge: merged_acct_txn and daily_balances
    # Merge on account_id and where txn_date matches balance_date for daily balances
    # This assumes we want daily balance for each transaction date.
    # If balance_date is not unique per account_id, this might create duplicates or require more complex logic.
    final_merged_df = pd.merge(merged_acct_txn, balances_df, left_on=["account_id", "txn_date"], right_on=["account_id", "balance_date"], how="left")
    print(f"Rows after final merge: {len(final_merged_df)}")
    assert len(final_merged_df) >= len(merged_acct_txn), "Row count decreased unexpectedly after second merge"

    return final_merged_df