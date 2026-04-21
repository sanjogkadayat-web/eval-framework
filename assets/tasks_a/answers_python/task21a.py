# SYNTHETIC DATA — no real financial data
# Task: PY-021 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path):
    """Assign each account to a cohort based on account_open_date month."""
    df = pd.read_csv(accounts_path, comment='#')
    
    # Convert account_open_date to datetime
    df['account_open_date'] = pd.to_datetime(df['account_open_date'])
    
    # Create cohort based on year-month
    df['cohort'] = df['account_open_date'].dt.to_period('M').astype(str)
    
    return df
