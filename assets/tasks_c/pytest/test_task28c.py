import pandas as pd
import pytest
from pathlib import Path
import importlib, sys
import numpy as np
from datetime import timedelta

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).parent.parent / "assets" / "tasks_a" / "answers_python"))
task28c = importlib.import_module("task28c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task28c.py | Tests: task28c.py (PY-028)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

DATASET_DIR = Path(__file__).parent.parent / "assets" / "datasets"

@pytest.fixture(params=["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def variant(request):
    return request.param

@pytest.fixture
def setup_data(tmp_path: Path, variant: str):
    """
    Fixture to create dummy accounts and transactions CSV files for different variants
    to test churn detection logic.
    """
    # Base Accounts Data
    base_accounts_data = {
        "account_id": [f"SYNTHETIC_ACCT_{i:04d}" for i in range(1, 7)],
        "customer_segment": ["RETAIL"] * 6,
        "account_open_date": [f"2023-01-0{i}" for i in range(1, 7)],
        "account_status": ["ACTIVE"] * 6,
        "region": ["NORTH"] * 6,
    }
    accounts_df = pd.DataFrame(base_accounts_data)

    # Base Transactions Data
    base_transactions_data = {
        "txn_id": [f"SYNTHETIC_TXN_{i:06d}" for i in range(1, 9)],
        "account_id": [
            "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001", # ACCT_0001: active, recent txn
            "SYNTHETIC_ACCT_0002", # ACCT_0002: active, old txn (churned)
            "SYNTHETIC_ACCT_0003", # ACCT_0003: no transactions (churned)
            "SYNTHETIC_ACCT_0004", # ACCT_0004: active, recent txn
            "SYNTHETIC_ACCT_0001", # ACCT_0001
            "SYNTHETIC_ACCT_0002", # ACCT_0002
            "SYNTHETIC_ACCT_0004" # ACCT_0004
        ],
        "txn_date": [
            "2024-09-01", "2024-12-01", # ACCT_0001 (latest 2024-12-01)
            "2024-06-01", # ACCT_0002 (latest 2024-06-01)
            np.nan, # ACCT_0003 (no transactions)
            "2024-10-01", # ACCT_0004 (latest 2024-10-01)
            "2024-11-01", # ACCT_0001 (another txn)
            "2024-05-01", # ACCT_0002 (another txn)
            "2024-11-15" # ACCT_0004 (latest 2024-11-15)
        ],
        "txn_amount": [100.0] * 8,
        "txn_type": ["PURCHASE"] * 8,
        "merchant_category": ["RETAIL"] * 8,
        "channel": ["ONLINE"] * 8,
        "is_flagged": [False] * 8,
    }
    transactions_df = pd.DataFrame(base_transactions_data)

    # Reference date to be used for churn calculation
    # Max txn_date in the *entire* base_transactions_data is 2024-12-01 (for ACCT_0001).
    # Churn threshold will be 2024-12-01 - 90 days = 2024-09-02.
    # So, ACCT_0001 (last txn 2024-12-01) is NOT churned.
    # ACCT_0002 (last txn 2024-06-01) IS churned.
    # ACCT_0003 (no txns) IS churned.
    # ACCT_0004 (last txn 2024-11-15) is NOT churned.
    # ACCT_0005 (no txns) IS churned.
    # ACCT_0006 (no txns) IS churned.


    if variant == "null_heavy":
        # ACCT_0001: latest txn_date becomes null
        transactions_df.loc[1, "txn_date"] = None # 2024-12-01 for ACCT_0001
        # This makes the latest non-null txn_date for ACCT_0001 become 2024-11-01. 
        # Reference date will now be from ACCT_0004's 2024-11-15. So reference_date = 2024-11-15.
        # Churn threshold: 2024-11-15 - 90 days = 2024-08-17.
        # ACCT_0001 (last txn 2024-11-01) is NOT churned (2024-11-01 > 2024-08-17)
        # ACCT_0002 (last txn 2024-06-01) IS churned.
        # ACCT_0003 (no txns) IS churned.
        # ACCT_0004 (last txn 2024-11-15) is NOT churned.
        # ACCT_0005 (no txns) IS churned.
        # ACCT_0006 (no txns) IS churned.

        # Add a transaction with null account_id
        transactions_df = pd.concat([transactions_df, pd.DataFrame({
            "txn_id": ["SYNTHETIC_TXN_NULLACCT"], "account_id": [None],
            "txn_date": ["2024-11-01"], "txn_amount": [500.0], "txn_type": ["PURCHASE"],
            "merchant_category": ["RETAIL"], "channel": ["ONLINE"], "is_flagged": [False]
        })], ignore_index=True)

    elif variant == "duplicate_heavy":
        # Add a duplicate transaction for ACCT_0001 to ensure last_txn_date is handled correctly
        dup_txn = pd.DataFrame({
            "txn_id": ["SYNTHETIC_TXN_000002_DUP"], "account_id": ["SYNTHETIC_ACCT_0001"],
            "txn_date": ["2024-12-01"], "txn_amount": [10.0], "txn_type": ["PURCHASE"],
            "merchant_category": ["RETAIL"], "channel": ["ONLINE"], "is_flagged": [False]
        })
        transactions_df = pd.concat([transactions_df, dup_txn], ignore_index=True)
        # This should not change the latest txn date for ACCT_0001 (still 2024-12-01), nor churn status.

        # Add a duplicate account (will be merged in)
        accounts_df = pd.concat([accounts_df, accounts_df.iloc[[0]]], ignore_index=True)

    elif variant == "medium":
        accounts_df = pd.concat([accounts_df] * 10, ignore_index=True)
        transactions_df = pd.concat([transactions_df] * 10, ignore_index=True)
    elif variant == "large":
        accounts_df = pd.concat([accounts_df] * 100, ignore_index=True)
        transactions_df = pd.concat([transactions_df] * 100, ignore_index=True)

    accounts_path = tmp_path / f"synthetic_{variant}_accounts.csv"
    transactions_path = tmp_path / f"synthetic_{variant}_transactions.csv"
    balances_path = tmp_path / f"synthetic_{variant}_daily_balances.csv" # Dummy

    with open(accounts_path, 'w') as f: f.write("H1,H2,H3,H4,H5\n")
    accounts_df.to_csv(accounts_path, mode='a', index=False, header=False)
    
    with open(transactions_path, 'w') as f: f.write("H1,H2,H3,H4,H5,H6,H7,H8\n")
    transactions_df.to_csv(transactions_path, mode='a', index=False, header=False)

    # Create dummy empty files for balances as they are required by the run signature
    pd.DataFrame(columns=[]).to_csv(balances_path, index=False)

    return accounts_path, transactions_path, balances_path


def calculate_expected_churn_flags(accounts_df_original: pd.DataFrame, transactions_df_original: pd.DataFrame, N_DAYS_CHURN: int = 90) -> pd.DataFrame:
    """
    Helper function to calculate expected churn flags manually for comparison.
    """
    accounts_df = accounts_df_original.copy()
    transactions_df = transactions_df_original.copy()

    transactions_df["txn_date"] = pd.to_datetime(transactions_df["txn_date"], errors='coerce')

    if not transactions_df.empty:
        latest_dataset_date = transactions_df["txn_date"].max() # Max before dropping null account_id
    else:
        latest_dataset_date = pd.to_datetime("2024-12-31")
    
    churn_threshold_date = latest_dataset_date - timedelta(days=N_DAYS_CHURN)

    # Ensure sorting for last() is deterministic
    last_txn_date_per_account = transactions_df.sort_values(by=["txn_date", "txn_id"]).groupby("account_id")["txn_date"].last().reset_index()
    last_txn_date_per_account.rename(columns={"txn_date": "last_txn_date"}, inplace=True)

    accounts_with_last_txn = pd.merge(accounts_df, last_txn_date_per_account, on="account_id", how="left")

    accounts_with_last_txn["is_churned"] = (
        accounts_with_last_txn["last_txn_date"].isnull()
        | (accounts_with_last_txn["last_txn_date"] < churn_threshold_date)
    )

    return accounts_with_last_txn


@pytest.mark.parametrize(
    "variant",
    ["clean", "null_heavy", "duplicate_heavy", "medium", "large"],
    indirect=True,
)
def test_task28c_run_function(setup_data: tuple[Path, Path, Path], variant: str):
    """
    Tests the run function from task28c.py to flag likely churned accounts with no
    transactions in the last N days relative to the dataset's latest transaction date
    for various dataset variants.
    """
    accounts_path_arg, transactions_path_arg, balances_path = setup_data

    result_df = task28c.run(accounts_path_arg, transactions_path_arg, balances_path)

    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty, "Resulting DataFrame should not be empty"

    # Assert expected columns are present, including the new flag column
    expected_columns = [
        "account_id", "customer_segment", "account_open_date", "account_status", "region",
        "last_txn_date", "is_churned"
    ]
    assert sorted(list(result_df.columns)) == sorted(expected_columns)

    # Assert 'is_churned' column is boolean
    assert pd.api.types.is_boolean_dtype(result_df["is_churned"])

    # Load original data to calculate expected values for comparison
    original_accounts_df = pd.read_csv(accounts_path_arg, skiprows=1)
    original_transactions_df = pd.read_csv(transactions_path_arg, skiprows=1)
    
    expected_churn_df = calculate_expected_churn_flags(original_accounts_df, original_transactions_df)

    # Sort both for deterministic comparison (ignoring NaT for sorting)
    result_df_sorted = result_df.sort_values(by="account_id").reset_index(drop=True)
    expected_churn_df_sorted = expected_churn_df.sort_values(by="account_id").reset_index(drop=True)

    # Compare the churn flag. NaN values in `last_txn_date` are expected.
    pd.testing.assert_series_equal(
        result_df_sorted["is_churned"].reset_index(drop=True),
        expected_churn_df_sorted["is_churned"].reset_index(drop=True),
        check_dtype=True, check_exact=True
    )

    # For clean variant, verify specific churn flags
    if variant == "clean":
        # ACCT_0001: not churned (last txn 2024-12-01 > 2024-09-02)
        # ACCT_0002: churned (last txn 2024-06-01 < 2024-09-02)
        # ACCT_0003: churned (no txns)
        # ACCT_0004: not churned (last txn 2024-11-15 > 2024-09-02)
        # ACCT_0005: churned (no txns)
        # ACCT_0006: churned (no txns)

        expected_churn_status = {
            "SYNTHETIC_ACCT_0001": False,
            "SYNTHETIC_ACCT_0002": True,
            "SYNTHETIC_ACCT_0003": True,
            "SYNTHETIC_ACCT_0004": False,
            "SYNTHETIC_ACCT_0005": True,
            "SYNTHETIC_ACCT_0006": True,
        }

        for account_id, expected_churn in expected_churn_status.items():
            actual_churn = result_df_sorted[result_df_sorted["account_id"] == account_id]["is_churned"].iloc[0]
            assert actual_churn == expected_churn, f"Account {account_id}: Expected churned={expected_churn}, got {actual_churn}"

    # For null_heavy variant, verify how nulls impact churn detection
    elif variant == "null_heavy":
        # Reference date from original_transactions_df will be 2024-11-15 (from ACCT_0004).
        # Churn threshold: 2024-11-15 - 90 days = 2024-08-17.
        # ACCT_0001: Last valid txn is 2024-11-01 (before 2024-12-01 original). Not churned.
        # ACCT_0002: Churned.
        # ACCT_0003: Churned.
        # ACCT_0004: Not churned.
        # ACCT_0005: Churned.
        # ACCT_0006: Churned.

        expected_churn_status_null_heavy = {
            "SYNTHETIC_ACCT_0001": False,
            "SYNTHETIC_ACCT_0002": True,
            "SYNTHETIC_ACCT_0003": True,
            "SYNTHETIC_ACCT_0004": False,
            "SYNTHETIC_ACCT_0005": True,
            "SYNTHETIC_ACCT_0006": True,
        }
        for account_id, expected_churn in expected_churn_status_null_heavy.items():
            actual_churn = result_df_sorted[result_df_sorted["account_id"] == account_id]["is_churned"].iloc[0]
            assert actual_churn == expected_churn, f"Account {account_id} (null_heavy): Expected churned={expected_churn}, got {actual_churn}"

    # For medium and large variants, check that flag column exists and has expected properties.
