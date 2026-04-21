import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-020 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    """
    Flags 'txn_amount' outliers using the Interquartile Range (IQR) rule.
    Outliers are defined as values below (Q1 - 1.5 * IQR) or above (Q3 + 1.5 * IQR).
    """
    transactions_df = pd.read_csv(transactions_path, skiprows=1)

    # Ensure txn_amount is numeric
    transactions_df["txn_amount"] = pd.to_numeric(transactions_df["txn_amount"], errors='coerce')

    # Drop rows where txn_amount is NaN after conversion, as they can't be used for outlier detection
    transactions_df.dropna(subset=["txn_amount"], inplace=True)

    if transactions_df.empty:
        transactions_df["is_outlier"] = False
        return transactions_df

    Q1 = transactions_df["txn_amount"].quantile(0.25)
    Q3 = transactions_df["txn_amount"].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    transactions_df["is_outlier"] = (
        (transactions_df["txn_amount"] < lower_bound) |
        (transactions_df["txn_amount"] > upper_bound)
    )

    return transactions_df