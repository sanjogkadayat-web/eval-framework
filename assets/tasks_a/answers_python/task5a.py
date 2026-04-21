# SYNTHETIC DATA — no real financial data
# Task: PY-005 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path, min_amount=100.0):
    """Filter transactions to keep only flagged transactions above a chosen amount."""
    df = pd.read_csv(transactions_path, comment='#')
    
    initial_count = len(df)
    
    # Convert is_flagged to boolean
    df['is_flagged'] = df['is_flagged'].astype(str).str.lower() == 'true'
    
    # Filter for flagged transactions above min_amount
    filtered = df[(df['is_flagged'] == True) & (df['txn_amount'] > min_amount)].copy()
    
    final_count = len(filtered)
    dropped_count = initial_count - final_count
    
    print(f"Rows dropped: {dropped_count} (initial: {initial_count}, final: {final_count})")
    
    return filtered
