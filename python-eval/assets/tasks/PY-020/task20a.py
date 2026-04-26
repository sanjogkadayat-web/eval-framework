# SYNTHETIC DATA — no real financial data
# Task: PY-020 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
import numpy as np
from pathlib import Path


def run(accounts_path, transactions_path, balances_path):
    """Flag txn_amount outliers using the IQR rule."""
    df = pd.read_csv(transactions_path, comment='#')
    
    # Calculate IQR
    q1 = df['txn_amount'].quantile(0.25)
    q3 = df['txn_amount'].quantile(0.75)
    iqr = q3 - q1
    
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    # Flag outliers
    df['is_outlier'] = (df['txn_amount'] < lower_bound) | (df['txn_amount'] > upper_bound)
    df['lower_bound'] = lower_bound
    df['upper_bound'] = upper_bound
    
    return df
