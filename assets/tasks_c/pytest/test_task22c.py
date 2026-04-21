import pandas as pd
import pytest
from pathlib import Path
import importlib, sys
import numpy as np

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).parent.parent / "assets" / "tasks_a" / "answers_python"))
task22c = importlib.import_module("task22c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task22c.py | Tests: task22c.py (PY-022)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

DATASET_DIR = Path(__file__).parent.parent / "assets" / "datasets"

@pytest.fixture(params=["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def variant(request):
    return request.param

@pytest.fixture
def setup_data(tmp_path: Path, variant: str):
    """
    Fixture to create dummy accounts, transactions, and daily_balances CSV files
    for different variants for audit log testing.
    """
    # Base Accounts Data
    accounts_data = {
        "account_id": [f"SYNTHETIC_ACCT_{i:04d}" for i in range(1, 4)],
        "customer_segment": ["RETAIL", "SMALL_BIZ", "WEALTH"],
        "account_open_date": [f"2023-01-0{i}" for i in range(1, 4)],
        "account_status": ["ACTIVE", "CLOSED", "ACTIVE"],
        "region": ["NORTH", "SOUTH", "EAST"],
    }
    accounts_df = pd.DataFrame(accounts_data)

    # Base Transactions Data
    transactions_data = {
        "txn_id": [f"SYNTHETIC_TXN_{i:06d}" for i in range(1, 6)],
        "account_id": ["SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0002", "SYNTHETIC_ACCT_0003", "SYNTHETIC_ACCT_0001"],
        "txn_date": [f"2023-01-0{i}" for i in range(1, 6)],
        "txn_amount": [100.0, 50.0, 200.0, 75.0, 150.0],
        "txn_type": ["PURCHASE"] * 5,
        "merchant_category": ["RETAIL"] * 5,
        "channel": ["ONLINE"] * 5,
        "is_flagged": [False] * 5,
    }
    transactions_df = pd.DataFrame(transactions_data)

    # Base Daily Balances Data
    balances_data = {
        "account_id": [f"SYNTHETIC_ACCT_{i:04d}" for i in range(1, 3)],
        "balance_date": ["2023-01-01", "2023-01-02"],
        "closing_balance": [1000.0, 950.0],
        "txn_count_day": [1, 2],
    }
    balances_df = pd.DataFrame(balances_data)

    if variant == "null_heavy":
        transactions_df.loc[0, "txn_amount"] = None # Null txn_amount
        transactions_df.loc[3, "account_id"] = None # Null account_id (should not affect filtering by txn_amount)
        accounts_df.loc[0, "account_status"] = "SUSPENDED" # Make an active account non-active
        # Add a row that will be dropped because of txn_amount being non-numeric and coerced to NaN
        transactions_df = pd.concat([transactions_df, pd.DataFrame({
            "txn_id": ["SYNTHETIC_TXN_NONUMERIC"], "account_id": ["SYNTHETIC_ACCT_9999"],
            "txn_date": ["2023-01-10"], "txn_amount": ["abc"], "txn_type": ["PURCHASE"],
            "merchant_category": ["RETAIL"], "channel": ["ONLINE"], "is_flagged": [False]
        })], ignore_index=True)
    elif variant == "duplicate_heavy":
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
def test_task22c_run_function(setup_data: tuple[Path, Path, Path], variant: str):
    """
    Tests the run function from task22c.py to generate an audit log DataFrame
    capturing each transformation step and row counts before/after for various dataset variants.
    """
    accounts_path, transactions_path, balances_path = setup_data

    audit_df = task22c.run(accounts_path, transactions_path, balances_path)

    assert isinstance(audit_df, pd.DataFrame)
    assert not audit_df.empty, "Audit log DataFrame should not be empty"

    # Assert expected columns are present in the audit log
    expected_audit_columns = ["step", "rows_before", "rows_after"]
    assert sorted(list(audit_df.columns)) == sorted(expected_audit_columns)

    # Assert that all expected steps are present
    expected_steps = [
        "Load accounts", "Load transactions", "Load daily_balances",
        "Filter active accounts", "Drop null txn_amount"
    ]
    assert all(step in audit_df["step"].values for step in expected_steps)

    # Verify row counts for clean variant
    if variant == "clean":
        # Accounts: 3 rows, 2 active
        # Transactions: 5 rows, 5 non-null txn_amount
        # Balances: 2 rows
        expected_audit_log_clean = [
            {"step": "Load accounts", "rows_before": None, "rows_after": 3},
            {"step": "Load transactions", "rows_before": None, "rows_after": 5},
            {"step": "Load daily_balances", "rows_before": None, "rows_after": 2},
            {"step": "Filter active accounts", "rows_before": 3, "rows_after": 2},
            {"step": "Drop null txn_amount", "rows_before": 5, "rows_after": 5},
        ]
        expected_audit_df = pd.DataFrame(expected_audit_log_clean)
        pd.testing.assert_frame_equal(audit_df, expected_audit_df, check_dtype=False)
    
    # Verify row counts for null_heavy variant
    elif variant == "null_heavy":
        # Accounts: 3 rows, 1 active initially (ACCT_0001 changed to SUSPENDED, ACCT_0002 CLOSED, ACCT_0003 ACTIVE)
        # Transactions: 5 + 1 non-numeric = 6 rows. 1 null txn_amount, 1 non-numeric txn_amount. Both dropped.
        # Original accounts: ACCT_0001 (ACTIVE -> SUSPENDED), ACCT_0002 (CLOSED), ACCT_0003 (ACTIVE)
        # So after filtering: only ACCT_0003 is active.
        
        expected_audit_log_null_heavy = [
            {"step": "Load accounts", "rows_before": None, "rows_after": 3},
            {"step": "Load transactions", "rows_before": None, "rows_after": 6},
            {"step": "Load daily_balances", "rows_before": None, "rows_after": 2},
            {"step": "Filter active accounts", "rows_before": 3, "rows_after": 1}, # Only ACCT_0003 is active
            {"step": "Drop null txn_amount", "rows_before": 6, "rows_after": 4}, # Original 6. Row 0 (null txn_amount), Row 5 (non-numeric) dropped. So 6-2=4.
        ]
        expected_audit_df = pd.DataFrame(expected_audit_log_null_heavy)
        pd.testing.assert_frame_equal(audit_df, expected_audit_df, check_dtype=False)

    # Verify row counts for duplicate_heavy variant
    elif variant == "duplicate_heavy":
        # Accounts: 3 + 1 dup = 4 rows. 2 active (ACCT_0001, ACCT_0003) + 1 dup active (ACCT_0001)
        # Transactions: 5 + 1 dup = 6 rows. All non-null txn_amount.
        # Balances: 2 + 1 dup = 3 rows.
        expected_audit_log_duplicate_heavy = [
            {"step": "Load accounts", "rows_before": None, "rows_after": 4},
            {"step": "Load transactions", "rows_before": None, "rows_after": 6},
            {"step": "Load daily_balances", "rows_before": None, "rows_after": 3},
            {"step": "Filter active accounts", "rows_before": 4, "rows_after": 3}, # ACCT_0001 (2 rows), ACCT_0003 (1 row)
            {"step": "Drop null txn_amount", "rows_before": 6, "rows_after": 6},
        ]
        expected_audit_df = pd.DataFrame(expected_audit_log_duplicate_heavy)
        pd.testing.assert_frame_equal(audit_df, expected_audit_df, check_dtype=False)

    # For medium and large variants, check that step counts are correct and no errors
    elif variant == "medium":
        assert len(audit_df) == len(expected_steps)
        assert audit_df.loc[audit_df["step"] == "Load accounts", "rows_after"].iloc[0] == 3 * 10
        assert audit_df.loc[audit_df["step"] == "Load transactions", "rows_after"].iloc[0] == 5 * 10
        assert audit_df.loc[audit_df["step"] == "Load daily_balances", "rows_after"].iloc[0] == 2 * 10
        # Assuming base case active accounts (2) * 10 = 20. And 5 * 10 = 50 transactions without nulls.
        assert audit_df.loc[audit_df["step"] == "Filter active accounts", "rows_after"].iloc[0] == 2 * 10
        assert audit_df.loc[audit_df["step"] == "Drop null txn_amount", "rows_after"].iloc[0] == 5 * 10
    elif variant == "large":
        assert len(audit_df) == len(expected_steps)
        assert audit_df.loc[audit_df["step"] == "Load accounts", "rows_after"].iloc[0] == 3 * 100
        assert audit_df.loc[audit_df["step"] == "Load transactions", "rows_after"].iloc[0] == 5 * 100
        assert audit_df.loc[audit_df["step"] == "Load daily_balances", "rows_after"].iloc[0] == 2 * 100
        assert audit_df.loc[audit_df["step"] == "Filter active accounts", "rows_after"].iloc[0] == 2 * 100
        assert audit_df.loc[audit_df["step"] == "Drop null txn_amount", "rows_after"].iloc[0] == 5 * 100
