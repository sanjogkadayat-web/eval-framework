# SYNTHETIC DATA — no real financial data
# Task: PY-004 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path):
    """Drop exact duplicate rows from duplicate-heavy transactions and print how many were removed."""
    df = pd.read_csv(transactions_path)
    
    initial_count = len(df)
    df_deduplicated = df.drop_duplicates()
    final_count = len(df_deduplicated)
    duplicates_removed = initial_count - final_count
    
    print(f"Duplicates removed: {duplicates_removed} rows (initial: {initial_count}, final: {final_count})")
    
    return df_deduplicated
