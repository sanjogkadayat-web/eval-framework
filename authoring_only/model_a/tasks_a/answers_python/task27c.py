# SYNTHETIC DATA — no real financial data
# Task: PY-027 | Tier: Hard
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

import pandas as pd
from pathlib import Path


def run(accounts_path, transactions_path, balances_path, reference_date='2024-12-31'):
    """Calculate RFM scores (recency, frequency, monetary) for each account."""
    transactions = pd.read_csv(transactions_path)
    
    # Convert dates
    transactions['txn_date'] = pd.to_datetime(transactions['txn_date'])
    reference_date = pd.to_datetime(reference_date)
    
    # Calculate RFM metrics
    rfm = transactions.groupby('account_id').agg(
        recency=('txn_date', lambda x: (reference_date - x.max()).days),
        frequency=('txn_id', 'count'),
        monetary=('txn_amount', 'sum')
    ).reset_index()
    
    # Calculate RFM scores (1-5 quintiles, higher is better)
    rfm['recency_score'] = pd.qcut(rfm['recency'], q=5, labels=[5, 4, 3, 2, 1], duplicates='drop')
    rfm['frequency_score'] = pd.qcut(rfm['frequency'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    rfm['monetary_score'] = pd.qcut(rfm['monetary'], q=5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    
    # Convert scores to integers
    rfm['recency_score'] = rfm['recency_score'].astype(int)
    rfm['frequency_score'] = rfm['frequency_score'].astype(int)
    rfm['monetary_score'] = rfm['monetary_score'].astype(int)
    
    # Calculate overall RFM score
    rfm['rfm_score'] = rfm['recency_score'] + rfm['frequency_score'] + rfm['monetary_score']
    
    return rfm
