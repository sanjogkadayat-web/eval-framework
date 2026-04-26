# SYNTHETIC DATA — no real financial data
# Task: PY-015 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path):
    """Add a previous_txn_amount feature within each account using shift."""
    df = pd.read_csv(transactions_path, comment='#')
    
    # Convert txn_date to datetime
    df['txn_date'] = pd.to_datetime(df['txn_date'])
    
    # Sort by account_id and txn_date
    df = df.sort_values(['account_id', 'txn_date', 'txn_id'])
    
    # Add previous_txn_amount using shift within each account
    df['previous_txn_amount'] = df.groupby('account_id')['txn_amount'].shift(1)
    
    return df
