# SYNTHETIC DATA — no real financial data
# Task: PY-017 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path):
    """Build a three-DataFrame merge pipeline across accounts, transactions, and daily_balances and assert row counts at each step."""
    accounts = pd.read_csv(accounts_path, comment='#')
    transactions = pd.read_csv(transactions_path, comment='#')
    balances = pd.read_csv(balances_path, comment='#')
    
    initial_txn_count = len(transactions)
    
    # First merge: transactions + accounts
    step1 = transactions.merge(accounts, on='account_id', how='left')
    step1_count = len(step1)
    assert step1_count >= initial_txn_count, f"Merge 1 lost rows: {initial_txn_count} -> {step1_count}"
    
    # Second merge: result + balances
    step2 = step1.merge(balances, on='account_id', how='left')
    step2_count = len(step2)
    assert step2_count >= step1_count, f"Merge 2 lost rows: {step1_count} -> {step2_count}"
    
    print(f"Merge pipeline: {initial_txn_count} -> {step1_count} -> {step2_count} rows")
    
    return step2
