# SYNTHETIC DATA — no real financial data
# Task: PY-007 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path):
    """Group transactions by txn_type and compute total txn_amount and row count."""
    df = pd.read_csv(transactions_path)
    
    grouped = df.groupby('txn_type').agg(
        total_txn_amount=('txn_amount', 'sum'),
        row_count=('txn_id', 'count')
    ).reset_index()
    
    grouped = grouped.sort_values('txn_type')
    
    return grouped
