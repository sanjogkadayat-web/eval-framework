import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-026 | Tier: Hard
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    """
    Computes funnel drop-off from account creation to first transaction to first flagged transaction.
    """
    accounts_df = pd.read_csv(accounts_path, skiprows=1)
    transactions_df = pd.read_csv(transactions_path, skiprows=1)

    # Ensure date columns are in datetime format
    accounts_df["account_open_date"] = pd.to_datetime(accounts_df["account_open_date"])
    transactions_df["txn_date"] = pd.to_datetime(transactions_df["txn_date"])

    # Step 1: Account Created (all accounts)
    account_created_count = len(accounts_df)

    # Step 2: First Transaction
    first_txn = transactions_df.groupby("account_id")["txn_date"].min().reset_index()
    first_txn.rename(columns={"txn_date": "first_txn_date"}, inplace=True)

    accounts_with_first_txn = pd.merge(accounts_df, first_txn, on="account_id", how="inner")
    first_txn_count = len(accounts_with_first_txn)

    # Step 3: First Flagged Transaction
    flagged_txns = transactions_df[transactions_df["is_flagged"] == True]
    first_flagged_txn = flagged_txns.groupby("account_id")["txn_date"].min().reset_index()
    first_flagged_txn.rename(columns={"txn_date": "first_flagged_txn_date"}, inplace=True)

    accounts_with_first_flagged_txn = pd.merge(
        accounts_with_first_txn, first_flagged_txn, on="account_id", how="inner"
    )
    first_flagged_txn_count = len(accounts_with_first_flagged_txn)

    # Calculate drop-off rates
    drop_off_to_first_txn = (account_created_count - first_txn_count) / account_created_count if account_created_count > 0 else 0
    drop_off_to_first_flagged_txn = (first_txn_count - first_flagged_txn_count) / first_txn_count if first_txn_count > 0 else 0

    # Create a DataFrame for the funnel results
    funnel_data = {
        "step": ["Account Created", "First Transaction", "First Flagged Transaction"],
        "count": [account_created_count, first_txn_count, first_flagged_txn_count],
        "drop_off_rate": [0, drop_off_to_first_txn, drop_off_to_first_flagged_txn]
    }
    funnel_df = pd.DataFrame(funnel_data)

    return funnel_df