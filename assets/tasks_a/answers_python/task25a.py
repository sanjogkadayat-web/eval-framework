# SYNTHETIC DATA — no real financial data
# Task: PY-025 | Tier: Hard
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
import numpy as np
from pathlib import Path


def run(accounts_path, transactions_path, balances_path, window=10, z_threshold=2.5):
    """Flag rolling z-score anomalies in txn_amount within each account using a moving window."""
    df = pd.read_csv(transactions_path, comment='#')
    
    # Convert txn_date to datetime
    df['txn_date'] = pd.to_datetime(df['txn_date'])
    
    # Sort by account_id and txn_date
    df = df.sort_values(['account_id', 'txn_date', 'txn_id'])
    
    # Calculate rolling mean and std within each account
    df['rolling_mean'] = df.groupby('account_id')['txn_amount'].transform(
        lambda x: x.rolling(window=window, min_periods=1).mean()
    )
    df['rolling_std'] = df.groupby('account_id')['txn_amount'].transform(
        lambda x: x.rolling(window=window, min_periods=1).std()
    )
    
    # Calculate rolling z-score
    df['rolling_z_score'] = (df['txn_amount'] - df['rolling_mean']) / df['rolling_std']
    df['rolling_z_score'] = df['rolling_z_score'].fillna(0)
    
    # Flag anomalies
    df['is_anomaly'] = np.abs(df['rolling_z_score']) > z_threshold
    
    return df
