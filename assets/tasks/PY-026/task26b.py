import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-026 | Tier: Hard
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    accounts_df = pd.read_csv(accounts_path, skiprows=1, usecols=["account_id"])
    transactions_df = pd.read_csv(transactions_path, skiprows=1)

    transactions_df["txn_date"] = pd.to_datetime(transactions_df["txn_date"], errors="coerce")

    first_txn = (
        transactions_df.dropna(subset=["account_id", "txn_date"])
        .groupby("account_id", dropna=False)["txn_date"]
        .min()
        .rename("first_transaction_date")
        .reset_index()
    )
    first_flagged = (
        transactions_df[(transactions_df["is_flagged"] == True)]
        .dropna(subset=["account_id", "txn_date"])
        .groupby("account_id", dropna=False)["txn_date"]
        .min()
        .rename("first_flagged_transaction_date")
        .reset_index()
    )

    per_account = accounts_df.merge(first_txn, on="account_id", how="left").merge(
        first_flagged, on="account_id", how="left"
    )

    accounts_opened = len(per_account)
    accounts_with_first_transaction = per_account["first_transaction_date"].notna().sum()
    accounts_with_first_flagged_transaction = per_account["first_flagged_transaction_date"].notna().sum()

    dropoff_opened_to_first_txn = (
        1.0 - (accounts_with_first_transaction / accounts_opened) if accounts_opened else 0.0
    )
    dropoff_first_txn_to_first_flagged = (
        1.0 - (accounts_with_first_flagged_transaction / accounts_with_first_transaction)
        if accounts_with_first_transaction
        else 0.0
    )

    return pd.DataFrame(
        [
            {
                "accounts_opened": accounts_opened,
                "accounts_with_first_transaction": int(accounts_with_first_transaction),
                "accounts_with_first_flagged_transaction": int(accounts_with_first_flagged_transaction),
                "dropoff_opened_to_first_txn": dropoff_opened_to_first_txn,
                "dropoff_first_txn_to_first_flagged_txn": dropoff_first_txn_to_first_flagged,
            }
        ]
    )
