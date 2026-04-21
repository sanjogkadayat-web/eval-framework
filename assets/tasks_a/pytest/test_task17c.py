import pandas as pd
import pytest
from pathlib import Path
import importlib, sys
import numpy as np

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).parent.parent / "assets" / "tasks_a" / "answers_python"))
task17c = importlib.import_module("task17c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task17c.py | Tests: task17c.py (PY-017)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

DATASET_DIR = Path(__file__).parent.parent / "assets" / "datasets"

@pytest.fixture(params=["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def variant(request):
    return request.param

@pytest.fixture
def setup_data(tmp_path: Path, variant: str):
    """
    Fixture to create dummy accounts, transactions, and daily_balances CSV files
    for different variants.
    """
    # Base Accounts Data
    accounts_data = {
        "account_id": [f"SYNTHETIC_ACCT_{i:04d}" for i in range(1, 6)],
        "customer_segment": ["RETAIL", "SMALL_BIZ", "WEALTH", "STUDENT", "RETAIL"],
        "account_open_date": [f"2023-01-0{i}" for i in range(1, 6)],
        "account_status": ["ACTIVE"] * 5,
        "region": ["NORTH", "SOUTH", "EAST", "WEST", "NORTH"],
    }
    accounts_df = pd.DataFrame(accounts_data)

    # Base Transactions Data
    transactions_data = {
        "txn_id": [f"SYNTHETIC_TXN_{i:06d}" for i in range(1, 8)],
        "account_id": [
            "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0002", 
            "SYNTHETIC_ACCT_0003", "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0004",
            "SYNTHETIC_ACCT_0005"
        ],
        "txn_date": [
            "2023-01-01", "2023-01-02", "2023-01-01", 
            "2023-01-03", "2023-01-03", "2023-01-04",
            "2023-01-01"
        ],
        "txn_amount": [100.0, 50.0, 200.0, 75.0, 150.0, 300.0, 110.0],
        "txn_type": ["PURCHASE"] * 7,
        "merchant_category": ["RETAIL"] * 7,
        "channel": ["ONLINE"] * 7,
        "is_flagged": [False] * 7,
    }
    transactions_df = pd.DataFrame(transactions_data)

    # Base Daily Balances Data
    balances_data = {
        "account_id": [
            "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0002", 
            "SYNTHETIC_ACCT_0003", "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0005"
        ],
        "balance_date": [
            "2023-01-01", "2023-01-03", "2023-01-01", 
            "2023-01-03", "2023-01-04", "2023-01-01"
        ],
        "closing_balance": [1000.0, 950.0, 2000.0, 1500.0, 900.0, 1100.0],
        "txn_count_day": [1, 2, 1, 1, 3, 1],
    }
    balances_df = pd.DataFrame(balances_data)

    if variant == "null_heavy":
        accounts_df.loc[0, "region"] = None # Null in accounts
        transactions_df.loc[1, "account_id"] = None # Null in transactions (FK)
        balances_df.loc[0, "account_id"] = None # Null in balances (FK)
        transactions_df.loc[3, "txn_date"] = None # Null transaction date
        balances_df.loc[1, "balance_date"] = None # Null balance date
    elif variant == "duplicate_heavy":
        # Add duplicate accounts, transactions, balances to test merge robustness
        accounts_df = pd.concat([accounts_df, accounts_df.iloc[[0]]], ignore_index=True)
        transactions_df = pd.concat([transactions_df, transactions_df.iloc[[0]]], ignore_index=True)
        balances_df = pd.concat([balances_df, balances_df.iloc[[0]]], ignore_index=True)
    elif variant == "medium":
        accounts_df = pd.concat([accounts_df] * 10, ignore_index=True)
        transactions_df = pd.concat([transactions_df] * 10, ignore_index=True)
        balances_df = pd.concat([balances_df] * 10, ignore_index=True)
    elif variant == "large":
        accounts_df = pd.concat([accounts_df] * 100, ignore_index=True)
        transactions_df = pd.concat([transactions_df] * 100, ignore_index=True)
        balances_df = pd.concat([balances_df] * 100, ignore_index=True)

    accounts_path = tmp_path / f"synthetic_{variant}_accounts.csv"
    transactions_path = tmp_path / f"synthetic_{variant}_transactions.csv"
    balances_path = tmp_path / f"synthetic_{variant}_daily_balances.csv"

    with open(accounts_path, 'w') as f: f.write("H1,H2,H3,H4,H5\n")
    accounts_df.to_csv(accounts_path, mode='a', index=False, header=False)
    
    with open(transactions_path, 'w') as f: f.write("H1,H2,H3,H4,H5,H6,H7,H8\n")
    transactions_df.to_csv(transactions_path, mode='a', index=False, header=False)

    with open(balances_path, 'w') as f: f.write("H1,H2,H3,H4\n")
    balances_df.to_csv(balances_path, mode='a', index=False, header=False)

    return accounts_path, transactions_path, balances_path


@pytest.mark.parametrize(
    "variant",
    ["clean", "null_heavy", "duplicate_heavy", "medium", "large"],
    indirect=True,
)
def test_task17c_run_function(setup_data: tuple[Path, Path, Path], variant: str):
    """
    Tests the run function from task17c.py to perform a three-DataFrame merge pipeline
    and asserts row counts and column presence at each step for various dataset variants.
    """
    accounts_path, transactions_path, balances_path = setup_data

    result_df = task17c.run(accounts_path, transactions_path, balances_path)

    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty, "Resulting DataFrame should not be empty (unless expected for variant)"

    # Assert expected columns are present from all three tables
    expected_columns = [
        "account_id", "customer_segment", "account_open_date", "account_status", "region",
        "txn_id", "txn_date", "txn_amount", "txn_type", "merchant_category", "channel", "is_flagged",
        "balance_date", "closing_balance", "txn_count_day"
    ]
    assert all(col in result_df.columns for col in expected_columns)

    # For the clean variant, verify specific row counts and values
    if variant == "clean":
        # Accounts: 5 rows
        # Transactions: 7 rows. ACCT_0001 (3 txns), ACCT_0002 (1 txn), ACCT_0003 (2 txns), ACCT_0004 (1 txn), ACCT_0005 (1 txn, not present in base accounts list, should be included by left merge)
        # Transactions for ACCT_0001, txn_date 2023-01-03 has 2 entries. This should create 2 rows in the merge.
        # Balances: 6 rows

        # Expected row counts: accounts (5), transactions (7 distinct account_ids: 0001,0002,0003,0004,0005) (7 rows, 2023-01-03 has 2 for 0001).
        # Merge accounts (5 rows) LEFT with transactions (7 rows, 5 unique accounts_ids) on account_id. Should be sum of transactions related to the accounts.
        # This should result in: 
        # ACCT_0001: 3 transactions -> 3 rows
        # ACCT_0002: 1 transaction -> 1 row
        # ACCT_0003: 2 transactions -> 2 rows
        # ACCT_0004: 1 transaction -> 1 row
        # ACCT_0005: 1 transaction -> 1 row (from transactions, this account is in accounts)
        # Total: 8 rows
        # Wait, there are 5 accounts: ACCT_0001, ACCT_0002, ACCT_0003, ACCT_0004, ACCT_0005.
        # Accounts_df: 5 rows.
        # Transactions_df: 7 rows.
        # Merge 1: `merged_acct_txn`
        #  - `SYNTHETIC_ACCT_0001` (3 txns on 01-01, 01-02, 01-03) -> 3 rows
        #  - `SYNTHETIC_ACCT_0002` (1 txn on 01-01) -> 1 row
        #  - `SYNTHETIC_ACCT_0003` (2 txns on 01-03, 01-06) -> 2 rows
        #  - `SYNTHETIC_ACCT_0004` (1 txn on 01-04) -> 1 row
        #  - `SYNTHETIC_ACCT_0005` (1 txn on 01-01) -> 1 row
        # Total `merged_acct_txn` rows: 3 + 1 + 2 + 1 + 1 = 8 rows.
        # The assertion in task17c.py: `len(merged_acct_txn) >= len(accounts_df)` (8 >= 5, true)

        # Merge 2: `final_merged_df`
        # Left merge `merged_acct_txn` (8 rows) with `balances_df` (6 rows) on (account_id, txn_date) = (account_id, balance_date)
        # ACCT_0001:
        #   - txn_date 01-01: balance 1000.0 -> 1 row
        #   - txn_date 01-02: no balance -> 1 row
        #   - txn_date 01-03: balance 950.0 -> 1 row
        #   - txn_date 01-03 (dup_txn): balance 950.0 -> 1 row
        # ACCT_0002:
        #   - txn_date 01-01: balance 2000.0 -> 1 row
        # ACCT_0003:
        #   - txn_date 01-03: balance 1500.0 -> 1 row
        # ACCT_0004:
        #   - txn_date 01-04: balance 900.0 -> 1 row
        # ACCT_0005:
        #   - txn_date 01-01: balance 1100.0 -> 1 row
        # Total `final_merged_df` rows should be: 1 (01-01) + 1 (01-02) + 1 (01-03) + 1 (01-03_dup_txn) + 1 (ACCT_0002 01-01) + 1 (ACCT_0003 01-03) + 1 (ACCT_0004 01-04) + 1 (ACCT_0005 01-01) = 8 rows (if original merged_acct_txn was 8 rows)
        # Re-check transactions: 
        # ACCT_0001: 2023-01-01, 2023-01-02, 2023-01-03, 2023-01-03 (from 2 original, 1 added dup, but only 1 on 01-03 and 1 on 01-03 here, so total 4 distinct, not 3) - original has 4 txns for ACCT_0001
        # ACCT_0001: TXN_000001 (01-01), TXN_000002 (01-02), TXN_000005 (01-03), TXN_000004 (01-03) - these are 4 unique TXN_IDs for ACCT_0001. So 4 rows.
        # This means total `merged_acct_txn` will be 4+1+2+1+1 = 9 rows.
        # Balances for ACCT_0001: 01-01 (1000.0), 01-03 (950.0), 01-04 (900.0)
        # Merge `merged_acct_txn` (9 rows) with `balances_df` (6 rows) on (account_id, txn_date) = (account_id, balance_date)
        # ACCT_0001:
        #   - 01-01: balance 1000.0 -> 1 row
        #   - 01-02: no balance -> 1 row
        #   - 01-03 (TXN_000004): balance 950.0 -> 1 row
        #   - 01-03 (TXN_000005): balance 950.0 -> 1 row
        # ACCT_0002:
        #   - 01-01: balance 2000.0 -> 1 row
        # ACCT_0003:
        #   - 01-03: balance 1500.0 -> 1 row
        #   - 01-06: no balance -> 1 row (from merged_acct_txn)
        # ACCT_0004:
        #   - 01-04: no balance (but in transactions) -> 1 row
        # ACCT_0005:
        #   - 01-01: balance 1100.0 -> 1 row
        # Total `final_merged_df`: 1+1+1+1 (ACCT_0001) + 1 (ACCT_0002) + 1+1 (ACCT_0003) + 1 (ACCT_0004) + 1 (ACCT_0005) = 10 rows.
        assert len(result_df) == 10

    # For null_heavy variant, verify that nulls in merge keys are handled (NaNs in merged columns)
    elif variant == "null_heavy":
        # Accounts: 5 rows (1 null region)
        # Transactions: 7 rows (1 null account_id, 1 null txn_date). When account_id is null, it won't merge to accounts.
        # Balances: 6 rows (1 null account_id, 1 null balance_date)

        # After `pd.read_csv`, nulls in `account_id` or `txn_date` will lead to those rows not merging properly.
        # In `transactions_df.loc[1, "account_id"] = None` and `transactions_df.loc[3, "txn_date"] = None`
        # In `balances_df.loc[0, "account_id"] = None` and `balances_df.loc[1, "balance_date"] = None`

        # Let's count rows with non-null `account_id` and `txn_date` (or `balance_date`)
        original_accounts = pd.read_csv(accounts_path, skiprows=1)
        original_transactions = pd.read_csv(transactions_path, skiprows=1)
        original_balances = pd.read_csv(balances_path, skiprows=1)

        # First merge: accounts (5 rows) left with transactions (7 rows) on account_id
        # original_transactions.loc[1, "account_id"] = None means TXN_000002 (account None) will not join to accounts
        # original_accounts has 5 rows. transactions has 6 rows with non-null account_id.
        # This leads to (3 txns for ACCT_0001 + 1 for ACCT_0002 + 2 for ACCT_0003 + 1 for ACCT_0004 + 1 for ACCT_0005) = 8 rows in merged_acct_txn
        # And 1 row for TXN_000002 (account_id=None) which will have NaNs for account info. Total 9 rows.

        # Second merge: merged_acct_txn (9 rows) left with balances (6 rows) on (account_id, txn_date)
        # original_balances.loc[0, "account_id"] = None and original_balances.loc[1, "balance_date"] = None
        # These will not join.

        # The number of rows will be influenced by the non-joining nulls, but left merges generally preserve rows from the left side.
        # The `print` statements in task17c.py will indicate the lengths. Given `len(final_merged_df) >= len(merged_acct_txn)` it implies no rows are dropped.
        # So the result_df will contain all original rows from the left side, with NaNs where joins fail.
        # Thus, the number of rows in `result_df` should be the same as the number of rows in the `merged_acct_txn` at the end of task17c.py.
        # From the `merged_acct_txn` calculation above, it should be 9 rows.
        assert len(result_df) == 9 # Number of rows after 1st merge including rows with null account_id
        assert result_df["region"].isnull().sum() >= 1 # At least one null region from accounts
        assert result_df["txn_amount"].isnull().sum() >= 1 # At least one null txn_amount from original data, not from merge
        assert result_df["closing_balance"].isnull().sum() >= 1 # At least one null closing_balance due to missing join, or null balance_date

    # For duplicate_heavy variant, check row counts after merging duplicates
    elif variant == "duplicate_heavy":
        # Accounts: 5 + 1 dup = 6 rows
        # Transactions: 7 + 1 dup = 8 rows
        # Balances: 6 + 1 dup = 7 rows

        # Merge 1: accounts (6 rows) left with transactions (8 rows)
        # ACCT_0001 (original 4 txns + 1 dup) -> 5 rows
        # ACCT_0002 (1 txn) -> 1 row
        # ACCT_0003 (2 txns) -> 2 rows
        # ACCT_0004 (1 txn) -> 1 row
        # ACCT_0005 (1 txn) -> 1 row
        # Total `merged_acct_txn`: 5 + 1 + 2 + 1 + 1 = 10 rows.

        # Merge 2: `merged_acct_txn` (10 rows) left with `balances_df` (7 rows) on (account_id, txn_date)
        # The added duplicate in balances_df for ACCT_0001, 2023-01-01 should not impact the row count unless there are multiple transactions on that date.
        # If ACCT_0001, 2023-01-01 has 1 transaction, and there are 2 balance entries for that, it will duplicate.
        # Original: ACCT_0001, 2023-01-01 (1 txn)
        # Balances: ACCT_0001, 2023-01-01 (1 bal) + 1 dup bal = 2 matching balances.
        # So original 1 txn for ACCT_0001, 01-01 will now match 2 balance rows -> 2 rows in final_merged_df
        # Total rows should be 11. (Original 10, plus one duplication from the balance merge)
        # The transaction for ACCT_0001 on 2023-01-01 (`TXN_000001`) joins to 2 balance rows (1 original, 1 duplicate).
        # So `merged_acct_txn` had 10 rows. This specific join will turn 1 row into 2 rows. So 11 total rows.
        assert len(result_df) == 11

    # For medium and large variants, ensure it completes without error, and column count is correct
    elif variant == "medium":
        # Expect row count to be scaled by 10 from the clean variant's logic
        assert len(result_df) == 10 * 10 # 10 rows * 10 scale factor = 100 rows
    elif variant == "large":
        # Expect row count to be scaled by 100 from the clean variant's logic
        assert len(result_df) == 10 * 100 # 10 rows * 100 scale factor = 1000 rows
