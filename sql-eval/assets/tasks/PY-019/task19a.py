# SYNTHETIC DATA — no real financial data
# Task: PY-019 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path):
    """Deduplicate accounts by keeping the best row per account_id using a precedence rule over account_status."""
    df = pd.read_csv(accounts_path, comment='#')
    
    # Define status precedence: ACTIVE > SUSPENDED > CLOSED
    status_rank = {'ACTIVE': 1, 'SUSPENDED': 2, 'CLOSED': 3}
    df['status_rank'] = df['account_status'].map(status_rank)
    df['status_rank'] = df['status_rank'].fillna(999)
    
    # Sort by account_id and status_rank, then keep first occurrence
    df = df.sort_values(['account_id', 'status_rank'])
    df_deduplicated = df.drop_duplicates(subset=['account_id'], keep='first')
    
    # Drop helper column
    df_deduplicated = df_deduplicated.drop(columns=['status_rank'])
    
    return df_deduplicated
