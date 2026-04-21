import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-022 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    """
    Generates an audit log DataFrame capturing each transformation step and row counts before/after.
    """
    audit_log = []

    # Step 1: Load accounts data
    accounts_df = pd.read_csv(accounts_path, skiprows=1)
    audit_log.append({"step": "Load accounts", "rows_before": None, "rows_after": len(accounts_df)})

    # Step 2: Load transactions data
    transactions_df = pd.read_csv(transactions_path, skiprows=1)
    audit_log.append({"step": "Load transactions", "rows_before": None, "rows_after": len(transactions_df)})

    # Step 3: Load daily_balances data
    balances_df = pd.read_csv(balances_path, skiprows=1)
    audit_log.append({"step": "Load daily_balances", "rows_before": None, "rows_after": len(balances_df)})

    # Step 4: Example Transformation 1 - Filter active accounts
    rows_before = len(accounts_df)
    accounts_df = accounts_df[accounts_df["account_status"] == "ACTIVE"].copy()
    rows_after = len(accounts_df)
    audit_log.append({"step": "Filter active accounts", "rows_before": rows_before, "rows_after": rows_after})

    # Step 5: Example Transformation 2 - Drop nulls from transactions (if any)
    rows_before = len(transactions_df)
    transactions_df.dropna(subset=["txn_amount"], inplace=True)
    rows_after = len(transactions_df)
    audit_log.append({"step": "Drop null txn_amount", "rows_before": rows_before, "rows_after": rows_after})

    # Convert audit log to DataFrame
    audit_df = pd.DataFrame(audit_log)

    return audit_df