# SYNTHETIC DATA — no real financial data
# Task: PY-024 | Tier: Hard
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path):
    """Implement SCD Type 2 history tracking for account_status changes across account snapshots."""
    df = pd.read_csv(accounts_path, comment='#')
    
    # Convert account_open_date to datetime
    df['account_open_date'] = pd.to_datetime(df['account_open_date'])
    
    # Sort by account_id and account_open_date
    df = df.sort_values(['account_id', 'account_open_date'])
    
    # Identify status changes within each account
    df['prev_status'] = df.groupby('account_id')['account_status'].shift(1)
    df['status_changed'] = df['account_status'] != df['prev_status']
    
    # Create SCD Type 2 fields
    df['valid_from'] = df['account_open_date']
    df['valid_to'] = df.groupby('account_id')['account_open_date'].shift(-1)
    df['is_current'] = df['valid_to'].isna()
    
    # Fill valid_to with a far future date for current records
    df['valid_to'] = df['valid_to'].fillna(pd.Timestamp('2099-12-31'))
    
    # Assign surrogate keys
    df['surrogate_key'] = range(1, len(df) + 1)
    
    return df[['surrogate_key', 'account_id', 'customer_segment', 'account_status', 'region', 
               'valid_from', 'valid_to', 'is_current']]
