# SYNTHETIC DATA — no real financial data
# Task: PY-011 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path, output_path=None):
    """Write a functional ETL pipeline that loads accounts, validates schema, filters active rows, and saves output."""
    # Load
    df = pd.read_csv(accounts_path, comment='#')
    
    # Validate schema
    expected_columns = ['account_id', 'customer_segment', 'account_open_date', 'account_status', 'region']
    assert list(df.columns) == expected_columns, f"Schema validation failed"
    
    # Filter active rows
    df_active = df[df['account_status'] == 'ACTIVE'].copy()
    
    # Save output if path provided
    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df_active.to_csv(output_path, index=False)
        return None
    
    return df_active
