# SYNTHETIC DATA — no real financial data
# Task: PY-012 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path):
    """Create a running total of txn_amount within each account ordered by txn_date."""
    df = pd.read_csv(transactions_path)
    
    # Convert txn_date to datetime
    df['txn_date'] = pd.to_datetime(df['txn_date'])
    
    # Sort by account_id and txn_date
    df = df.sort_values(['account_id', 'txn_date', 'txn_id'])
    
    # Create running total within each account
    df['running_total'] = df.groupby('account_id')['txn_amount'].cumsum()
    
    return df
