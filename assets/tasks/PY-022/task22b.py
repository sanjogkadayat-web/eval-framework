import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-022 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None


def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    audit: list[dict[str, object]] = []

    accounts_df = pd.read_csv(accounts_path, skiprows=1)
    audit.append({"step": "load_accounts", "rows_before": None, "rows_after": len(accounts_df)})

    transactions_df = pd.read_csv(transactions_path, skiprows=1)
    audit.append({"step": "load_transactions", "rows_before": None, "rows_after": len(transactions_df)})

    before = len(accounts_df)
    active_accounts_df = accounts_df[accounts_df["account_status"] == "ACTIVE"].copy()
    audit.append({"step": "filter_active_accounts", "rows_before": before, "rows_after": len(active_accounts_df)})

    before = len(transactions_df)
    deduped_txn_df = transactions_df.drop_duplicates(keep="first")
    audit.append({"step": "dedupe_transactions", "rows_before": before, "rows_after": len(deduped_txn_df)})

    return pd.DataFrame(audit)
