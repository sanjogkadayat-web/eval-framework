import pandas as pd
from pathlib import Path
import logging

# SYNTHETIC DATA — no real financial data
# Task: PY-003 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

logger = logging.getLogger(__name__)

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    """
    Counts nulls per column in the transactions table and raises an error if any column
    exceeds a configured threshold.
    """
    transactions_df = pd.read_csv(transactions_path, skiprows=1)

    # Configure the null threshold (e.g., 30%)
    null_threshold = 0.3

    null_counts = transactions_df.isnull().sum()
    null_percentages = transactions_df.isnull().mean()

    for column, percentage in null_percentages.items():
        if percentage > null_threshold:
            raise ValueError(
                f"Column '{column}' exceeds null threshold: "
                f"{percentage:.2%} nulls (threshold: {null_threshold:.2%})"
            )
        elif percentage > 0:
            logger.info(f"Column '{column}' has {percentage:.2%} nulls.")

    print("Null value check passed. No columns exceeded the configured threshold.")
    return transactions_df