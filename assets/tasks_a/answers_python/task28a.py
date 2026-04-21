# SYNTHETIC DATA — no real financial data
# Task: PY-028 | Tier: Hard
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path, days_threshold=90):
    """Flag likely churned accounts with no transactions in the last N days relative to the dataset max date."""
    accounts = pd.read_csv(accounts_path)
    transactions = pd.read_csv(transactions_path)
    
    # Convert dates
    transactions['txn_date'] = pd.to_datetime(transactions['txn_date'])
    
    # Get dataset max date
    max_date = transactions['txn_date'].max()
    
    # Get last transaction date per account
    last_txn = transactions.groupby('account_id')['txn_date'].max().reset_index()
    last_txn.columns = ['account_id', 'last_txn_date']
    
    # Merge with accounts
    result = accounts.merge(last_txn, on='account_id', how='left')
    
    # Calculate days since last transaction
    result['days_since_last_txn'] = (max_date - result['last_txn_date']).dt.days
    
    # Flag churned accounts
    result['is_churned'] = result['days_since_last_txn'] > days_threshold
    result['is_churned'] = result['is_churned'].fillna(True)
    
    return result
