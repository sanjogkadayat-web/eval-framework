# SYNTHETIC DATA — no real financial data
# Task: PY-013 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path):
    """Compute a rolling average of closing_balance over the last 7 observations per account."""
    df = pd.read_csv(balances_path)
    
    # Convert balance_date to datetime
    df['balance_date'] = pd.to_datetime(df['balance_date'])
    
    # Sort by account_id and balance_date
    df = df.sort_values(['account_id', 'balance_date'])
    
    # Calculate rolling average within each account
    df['rolling_avg_7'] = df.groupby('account_id')['closing_balance'].transform(
        lambda x: x.rolling(window=7, min_periods=1).mean()
    )
    
    return df
