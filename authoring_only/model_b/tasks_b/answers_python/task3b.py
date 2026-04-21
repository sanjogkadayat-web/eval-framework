import pandas as pd
from pathlib import Path
import logging

# SYNTHETIC DATA — no real financial data
# Task: PY-003 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

logger = logging.getLogger(__name__)


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    transactions_df = pd.read_csv(transactions_path, skiprows=1)

    null_threshold = 0.3
    null_percentages = transactions_df.isna().mean()

    for column, pct in null_percentages.items():
        if pct > null_threshold:
            raise ValueError(
                f"Column '{column}' exceeds null threshold: {pct:.2%} (threshold: {null_threshold:.2%})"
            )
        if pct > 0:
            logger.info("Column '%s' has %.2f%% nulls.", column, pct * 100.0)

    print("Null value check passed. No columns exceeded the configured threshold.")
    return transactions_df
