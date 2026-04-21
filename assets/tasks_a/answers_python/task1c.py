# SYNTHETIC DATA — no real financial data
# Task: PY-001 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path):
    """Load accounts CSV, skip synthetic header, assert expected column names."""
    df = pd.read_csv(accounts_path)
    
    expected_columns = ['account_id', 'customer_segment', 'account_open_date', 'account_status', 'region']
    actual_columns = df.columns.tolist()
    
    assert actual_columns == expected_columns, (
        f"Column mismatch. Expected: {expected_columns}, Got: {actual_columns}"
    )
    
    return df
