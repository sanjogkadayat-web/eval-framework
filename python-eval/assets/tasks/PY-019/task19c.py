import pandas as pd
from pathlib import Path

# SYNTHETIC DATA — no real financial data
# Task: PY-019 | Tier: Medium
# Input tables: accounts_path, transactions_path, balances_path (pathlib.Path or str)
# Returns: pd.DataFrame or None

def run(accounts_path: Path, transactions_path: Path, balances_path: Path) -> pd.DataFrame:
    """
    Deduplicates accounts by keeping the best row per account_id using a precedence rule
    over 'account_status': ACTIVE > SUSPENDED > CLOSED.
    """
    accounts_df = pd.read_csv(accounts_path, skiprows=1)

    # Define precedence for account_status
    status_precedence = {
        "ACTIVE": 1,
        "SUSPENDED": 2,
        "CLOSED": 3,
    }

    # Map account_status to numerical rank
    accounts_df["status_rank"] = accounts_df["account_status"].map(status_precedence)

    # Sort by account_id and then by status_rank (lowest rank first)
    # If status_rank is tied, the original order (or pandas default) will be kept,
    # which is acceptable as per task description "regardless of open date".
    deduplicated_accounts_df = accounts_df.sort_values(
        by=["account_id", "status_rank", "account_open_date", "customer_segment"]
    ).drop_duplicates(subset=["account_id"], keep="first")

    # Drop the temporary status_rank column
    deduplicated_accounts_df = deduplicated_accounts_df.drop(columns=["status_rank"])

    return deduplicated_accounts_df