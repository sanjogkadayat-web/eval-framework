# SYNTHETIC DATA — no real financial data
# Task: PY-009 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path):
    """Fill null txn_amount values with the median txn_amount of the file."""
    df = pd.read_csv(transactions_path)
    
    median_amount = df['txn_amount'].median()
    df['txn_amount'] = df['txn_amount'].fillna(median_amount)
    
    return df
