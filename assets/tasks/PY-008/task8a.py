# SYNTHETIC DATA — no real financial data
# Task: PY-008 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path):
    """Build a pivot table of total txn_amount by region and channel."""
    transactions = pd.read_csv(transactions_path, comment='#')
    accounts = pd.read_csv(accounts_path, comment='#')
    
    # Merge to get region information
    merged = transactions.merge(accounts[['account_id', 'region']], on='account_id', how='left')
    
    # Create pivot table
    pivot = merged.pivot_table(
        values='txn_amount',
        index='region',
        columns='channel',
        aggfunc='sum',
        fill_value=0
    )
    
    pivot = pivot.reset_index()
    
    return pivot
