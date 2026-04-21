# SYNTHETIC DATA — no real financial data
# Task: PY-016 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path):
    """Extract day_of_week, month, quarter, and is_weekend features from txn_date."""
    df = pd.read_csv(transactions_path)
    
    # Convert txn_date to datetime
    df['txn_date'] = pd.to_datetime(df['txn_date'])
    
    # Extract temporal features
    df['day_of_week'] = df['txn_date'].dt.dayofweek
    df['month'] = df['txn_date'].dt.month
    df['quarter'] = df['txn_date'].dt.quarter
    df['is_weekend'] = df['txn_date'].dt.dayofweek.isin([5, 6])
    
    return df
