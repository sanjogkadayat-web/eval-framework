import pandas as pd
import pytest
from pathlib import Path
import importlib, sys
import numpy as np

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).resolve().parent))
task18c = importlib.import_module("task18c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task18c.py | Tests: task18c.py (PY-018)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

DATASET_DIR = Path(__file__).resolve().parents[2] / "datasets"

@pytest.fixture(params=["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def variant(request):
    return request.param

@pytest.fixture
def setup_data(tmp_path: Path, variant: str):
    """
    Fixture to create dummy accounts and transactions CSV files for different variants.
    """
    # Base Accounts Data
    accounts_data = {
        "account_id": [f"SYNTHETIC_ACCT_{i:04d}" for i in range(1, 6)],
        "customer_segment": ["RETAIL", "SMALL_BIZ", "WEALTH", "STUDENT", "RETAIL"],
        "account_open_date": [
            "2023-01-10", # ACCT_0001
            "2023-01-05", # ACCT_0002
            "2023-02-01", # ACCT_0003
            "2023-03-15", # ACCT_0004
            "2023-01-20"  # ACCT_0005
        ],
        "account_status": ["ACTIVE"] * 5,
        "region": ["NORTH", "SOUTH", "EAST", "WEST", "NORTH"],
    }
    accounts_df = pd.DataFrame(accounts_data)

    # Base Transactions Data
    transactions_data = {
        "txn_id": [f"SYNTHETIC_TXN_{i:06d}" for i in range(1, 11)],
        "account_id": [
            "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0002", 
            "SYNTHETIC_ACCT_0003", "SYNTHETIC_ACCT_0001", "SYNTHETIC_ACCT_0004", 
            "SYNTHETIC_ACCT_0002", "SYNTHETIC_ACCT_0005", "SYNTHETIC_ACCT_0001", 
            "SYNTHETIC_ACCT_0003"
        ],
        "txn_date": [
            "2023-01-01", # ACCT_0001, BEFORE open
            "2023-01-10", # ACCT_0001, ON open
            "2023-01-06", # ACCT_0002, AFTER open
            "2023-01-20", # ACCT_0003, BEFORE open
            "2023-01-11", # ACCT_0001, AFTER open
            "2023-03-10", # ACCT_0004, BEFORE open
            "2023-01-04", # ACCT_0002, BEFORE open
            "2023-01-15", # ACCT_0005, BEFORE open
            "2023-01-09", # ACCT_0001, BEFORE open
            "2023-02-01"  # ACCT_0003, ON open
        ],
        "txn_amount": [100.0] * 10,
        "txn_type": ["PURCHASE"] * 10,
        "merchant_category": ["RETAIL"] * 10,
        "channel": ["ONLINE"] * 10,
        "is_flagged": [False] * 10,
    }
    transactions_df = pd.DataFrame(transactions_data)

    if variant == "null_heavy":
        accounts_df.loc[0, "account_open_date"] = None # ACCT_0001 has null open date
        transactions_df.loc[1, "txn_date"] = None      # ACCT_0001 has null txn_date
        transactions_df.loc[2, "account_id"] = None    # Transaction with null account_id
    elif variant == "duplicate_heavy":
        # Add a duplicate transaction that would be flagged
        dup_txn_before_open = pd.DataFrame({
            "txn_id": ["SYNTHETIC_TXN_000011"], "account_id": ["SYNTHETIC_ACCT_0001"],
            "txn_date": ["2023-01-01"], "txn_amount": [100.0], "txn_type": ["PURCHASE"],
            "merchant_category": ["RETAIL"], "channel": ["ONLINE"], "is_flagged": [False]
        })
        transactions_df = pd.concat([transactions_df, dup_txn_before_open], ignore_index=True)

        # Add a duplicate transaction that would NOT be flagged
        dup_txn_after_open = pd.DataFrame({
            "txn_id": ["SYNTHETIC_TXN_000012"], "account_id": ["SYNTHETIC_ACCT_0001"],
            "txn_date": ["2023-01-11"], "txn_amount": [50.0], "txn_type": ["PURCHASE"],
            "merchant_category": ["RETAIL"], "channel": ["ONLINE"], "is_flagged": [False]
        })
        transactions_df = pd.concat([transactions_df, dup_txn_after_open], ignore_index=True)
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


@pytest.mark.parametrize(
    "variant",
    ["clean", "null_heavy", "duplicate_heavy", "medium", "large"],
    indirect=True,
)
def test_task18c_run_function(setup_data: tuple[Path, Path, Path], variant: str):
    """
    Tests the run function from task18c.py to flag transactions where 'txn_date'
    is earlier than 'account_open_date' for various dataset variants.
    """
    accounts_path, transactions_path, balances_path = setup_data

    result_df = task18c.run(accounts_path, transactions_path, balances_path)

    assert isinstance(result_df, pd.DataFrame)
    assert not result_df.empty, "Resulting DataFrame should not be empty (unless filtered to empty)"

    # Assert expected columns are present, including the new flag column
    expected_columns = [
        "txn_id", "account_id", "txn_date", "txn_amount", "txn_type",
        "merchant_category", "channel", "is_flagged",
        "customer_segment", "account_open_date", "account_status", "region",
        "is_txn_before_account_open"
    ]
    assert all(col in result_df.columns for col in expected_columns)

    # Assert 'is_txn_before_account_open' column is boolean
    assert pd.api.types.is_boolean_dtype(result_df["is_txn_before_account_open"])

    # For clean variant, manually verify the flag
    if variant == "clean":
        expected_flags = [
            True,  # ACCT_0001, 2023-01-01 < 2023-01-10
            False, # ACCT_0001, 2023-01-10 == 2023-01-10
            False, # ACCT_0002, 2023-01-06 > 2023-01-05
            True,  # ACCT_0003, 2023-01-20 < 2023-02-01
            False, # ACCT_0001, 2023-01-11 > 2023-01-10
            True,  # ACCT_0004, 2023-03-10 < 2023-03-15
            True,  # ACCT_0002, 2023-01-04 < 2023-01-05
            True,  # ACCT_0005, 2023-01-15 < 2023-01-20
            True,  # ACCT_0001, 2023-01-09 < 2023-01-10
            False  # ACCT_0003, 2023-02-01 == 2023-02-01
        ]
        pd.testing.assert_series_equal(
            result_df["is_txn_before_account_open"].reset_index(drop=True),
            pd.Series(expected_flags, dtype='bool'),
            check_exact=True
        )

    # For null_heavy variant, check handling of null dates or account_ids
    elif variant == "null_heavy":
        # accounts_df.loc[0, "account_open_date"] = None # ACCT_0001 open date is null
        # transactions_df.loc[1, "txn_date"] = None      # ACCT_0001, txn_id 2 has null txn_date
        # transactions_df.loc[2, "account_id"] = None    # TXN_000003 has null account_id

        # A transaction with null account_id will result in `account_open_date` being `NaT` after left merge.
        # `NaT < some_date` evaluates to False
        # `some_date < NaT` evaluates to False
        # `NaT < NaT` evaluates to False
        # So, if either `txn_date` or `account_open_date` is `NaT`, `is_txn_before_account_open` should be False.

        # Verify specific rows with nulls
        # Row for TXN_000001 (ACCT_0001, 2023-01-01) with null account_open_date (ACCT_0001): False
        row_txn_000001_null_acct_open = result_df[(result_df["txn_id"] == "SYNTHETIC_TXN_000001") & (result_df["account_open_date"].isnull())]
        assert not row_txn_000001_null_acct_open.empty
        assert row_txn_000001_null_acct_open["is_txn_before_account_open"].iloc[0] == False

        # Row for TXN_000002 (ACCT_0001, txn_date None) with null txn_date: False
        row_txn_000002_null_txn_date = result_df[(result_df["txn_id"] == "SYNTHETIC_TXN_000002") & (result_df["txn_date"].isnull())]
        assert not row_txn_000002_null_txn_date.empty
        assert row_txn_000002_null_txn_date["is_txn_before_account_open"].iloc[0] == False

        # Row for TXN_000003 (null account_id): False
        row_txn_000003_null_account_id = result_df[result_df["txn_id"] == "SYNTHETIC_TXN_000003"]
        assert not row_txn_000003_null_account_id.empty
        assert row_txn_000003_null_account_id["account_id"].isnull().all()
        assert row_txn_000003_null_account_id["is_txn_before_account_open"].iloc[0] == False

    # For duplicate_heavy, ensure duplicates are flagged consistently
    elif variant == "duplicate_heavy":
        # Check for consistency across duplicates based on txn_id and account_id
        duplicates_check_df = result_df[result_df.duplicated(subset=["txn_id", "account_id"], keep=False)]
        for _, group in duplicates_check_df.groupby(["txn_id", "account_id"]):
            assert group["is_txn_before_account_open"].nunique() == 1, \
                f"Duplicate entries for txn_id/account_id have inconsistent flags"

    # For medium and large variants, simply ensure it completes without error
    # and the new column exists with appropriate dtype.
