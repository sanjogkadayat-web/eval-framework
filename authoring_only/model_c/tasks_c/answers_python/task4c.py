import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-004 | Tier: Easy
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    """
    Loads the transactions CSV file, drops exact duplicate rows, and prints the number removed.
    """
    transactions_df = pd.read_csv(transactions_path, skiprows=1)
    initial_row_count = len(transactions_df)

    deduplicated_df = transactions_df.drop_duplicates()
    rows_removed = initial_row_count - len(deduplicated_df)

    print(f"Removed {rows_removed} exact duplicate rows from the transactions table.")

    return deduplicated_df