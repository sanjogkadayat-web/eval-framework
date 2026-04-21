import pandas as pd
from pathlib import Path
import logging

# SYNTHETIC DATA — no real financial data
# Task: PY-005 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

logger = logging.getLogger(__name__)


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    transactions_df = pd.read_csv(transactions_path, skiprows=1)
    initial_rows = len(transactions_df)

    amount_threshold = 500.0

    tx = transactions_df.copy()
    tx["txn_amount"] = pd.to_numeric(tx["txn_amount"], errors="coerce")
    filtered_df = tx[(tx["is_flagged"] == True) & (tx["txn_amount"] > amount_threshold)].copy()

    logger.info(
        "Dropped %s rows after filtering flagged txns above %.2f.",
        initial_rows - len(filtered_df),
        amount_threshold,
    )
    return filtered_df
