# SYNTHETIC DATA — no real financial data
# Task: PY-014 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path):
    """Compute a rolling 7-day sum of txn_amount for each account using a time-based window."""
    df = pd.read_csv(transactions_path)
    
    # Convert txn_date to datetime
    df['txn_date'] = pd.to_datetime(df['txn_date'])
    
    # Sort by account_id and txn_date
    df = df.sort_values(['account_id', 'txn_date'])
    
    # Set index to txn_date for rolling window
    df_with_index = df.set_index('txn_date')
    
    # Calculate rolling 7-day sum within each account
    df['rolling_7day_sum'] = df_with_index.groupby('account_id')['txn_amount'].transform(
        lambda x: x.rolling(window='7D').sum()
    )
    
    return df
