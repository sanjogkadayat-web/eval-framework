import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-030 | Tier: Hard
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None


def dummy_transform_function(df: pd.DataFrame) -> pd.DataFrame:
    return df


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> None:
    return None
