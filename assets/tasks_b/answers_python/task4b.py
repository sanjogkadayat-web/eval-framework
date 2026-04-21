import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-004 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    transactions_df = pd.read_csv(transactions_path, skiprows=1)
    before = len(transactions_df)
    deduped_df = transactions_df.drop_duplicates(keep="first")
    removed = before - len(deduped_df)
    print(f"Removed {removed} exact duplicate rows from transactions.")
    return deduped_df
