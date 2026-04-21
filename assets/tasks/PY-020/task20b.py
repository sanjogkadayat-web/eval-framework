import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-020 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    transactions_df = pd.read_csv(transactions_path, skiprows=1)
    transactions_df["txn_amount"] = pd.to_numeric(transactions_df["txn_amount"], errors="coerce")

    s = transactions_df["txn_amount"].dropna()
    if s.empty:
        transactions_df["iqr_lower_bound"] = pd.NA
        transactions_df["iqr_upper_bound"] = pd.NA
        transactions_df["is_outlier"] = False
        return transactions_df

    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    transactions_df["iqr_lower_bound"] = lower
    transactions_df["iqr_upper_bound"] = upper
    transactions_df["is_outlier"] = transactions_df["txn_amount"].lt(lower) | transactions_df["txn_amount"].gt(upper)
    transactions_df["is_outlier"] = transactions_df["is_outlier"].fillna(False)

    return transactions_df
