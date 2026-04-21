# SYNTHETIC DATA — no real financial data
# Task: PY-002 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path):
    """Validate date columns can be parsed as dates and numeric columns have numeric dtype."""
    accounts = pd.read_csv(accounts_path, comment='#')
    transactions = pd.read_csv(transactions_path, comment='#')
    balances = pd.read_csv(balances_path, comment='#')
    
    # Parse and validate date columns
    accounts['account_open_date'] = pd.to_datetime(accounts['account_open_date'], errors='raise')
    transactions['txn_date'] = pd.to_datetime(transactions['txn_date'], errors='raise')
    balances['balance_date'] = pd.to_datetime(balances['balance_date'], errors='raise')
    
    # Validate numeric columns
    transactions['txn_amount'] = pd.to_numeric(transactions['txn_amount'], errors='raise')
    balances['closing_balance'] = pd.to_numeric(balances['closing_balance'], errors='raise')
    balances['txn_count_day'] = pd.to_numeric(balances['txn_count_day'], errors='raise')
    
    validation_results = pd.DataFrame({
        'table': ['accounts', 'transactions', 'balances'],
        'date_column_validated': ['account_open_date', 'txn_date', 'balance_date'],
        'status': ['valid', 'valid', 'valid']
    })
    
    return validation_results
