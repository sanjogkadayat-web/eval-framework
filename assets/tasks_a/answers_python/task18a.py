# SYNTHETIC DATA — no real financial data
# Task: PY-018 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path):
    """Flag rows where txn_date is earlier than account_open_date after joining accounts and transactions."""
    accounts = pd.read_csv(accounts_path)
    transactions = pd.read_csv(transactions_path)
    
    # Convert dates to datetime
    accounts['account_open_date'] = pd.to_datetime(accounts['account_open_date'])
    transactions['txn_date'] = pd.to_datetime(transactions['txn_date'])
    
    # Merge
    merged = transactions.merge(accounts[['account_id', 'account_open_date']], on='account_id', how='left')
    
    # Flag invalid dates
    merged['invalid_txn_date'] = merged['txn_date'] < merged['account_open_date']
    
    return merged
