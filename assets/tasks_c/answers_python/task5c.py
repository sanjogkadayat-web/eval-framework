import pandas as pd
from pathlib import Path
import logging

# SYNTHETIC DATA — no real financial data
# Task: PY-005 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

logger = logging.getLogger(__name__)

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    """
    Filters the transactions table to keep only flagged transactions above a chosen amount
    and logs the number of dropped rows.
    """
    transactions_df = pd.read_csv(transactions_path, skiprows=1)
    initial_row_count = len(transactions_df)

    # Configure the amount threshold
    amount_threshold = 500.00

    filtered_df = transactions_df[
        (transactions_df["is_flagged"] == True) & (transactions_df["txn_amount"] > amount_threshold)
    ]

    rows_dropped = initial_row_count - len(filtered_df)
    logger.info(f"Dropped {rows_dropped} rows after filtering for flagged transactions above {amount_threshold}.")

    return filtered_df