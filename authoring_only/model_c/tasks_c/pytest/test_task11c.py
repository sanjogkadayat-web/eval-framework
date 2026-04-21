import pandas as pd
import pytest
from pathlib import Path
import importlib, sys
import numpy as np

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).parent.parent / "assets" / "tasks_a" / "answers_python"))
task11c = importlib.import_module("task11c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task11c.py | Tests: task11c.py (PY-011)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

DATASET_DIR = Path(__file__).parent.parent / "assets" / "datasets"

@pytest.fixture(params=["clean", "duplicate_heavy", "medium", "large"])
def setup_valid_accounts_data(tmp_path: Path, request):
    """
    Fixture to create dummy accounts CSV files for different valid variants
    and provide paths and expected active count.
    """
    variant = request.param
    base_accounts_data = {
        "account_id": [f"SYNTHETIC_ACCT_{i:04d}" for i in range(1, 11)],
        "customer_segment": ["RETAIL", "SMALL_BIZ", "WEALTH", "STUDENT", "RETAIL",
                             "SMALL_BIZ", "WEALTH", "STUDENT", "RETAIL", "SMALL_BIZ"],
        "account_open_date": [f"2023-0{i//2 + 1}-{i%2 * 15 + 1:02d}" for i in range(10)],
        "account_status": ["ACTIVE", "CLOSED", "ACTIVE", "SUSPENDED", "ACTIVE",
                           "ACTIVE", "CLOSED", "ACTIVE", "SUSPENDED", "ACTIVE"],
        "region": ["NORTH", "SOUTH", "EAST", "WEST", "NORTH",
                   "SOUTH", "EAST", "WEST", "NORTH", "SOUTH"],
    }
    accounts_df = pd.DataFrame(base_accounts_data)

    # Calculate expected active count before any variant-specific modifications that change structure
    expected_active_count = len(accounts_df[accounts_df["account_status"] == "ACTIVE"])

    if variant == "duplicate_heavy":
        # Add a duplicate ACTIVE account row that should pass filtering
        dup_account = accounts_df[accounts_df["account_status"] == "ACTIVE"].iloc[[0]].copy()
        accounts_df = pd.concat([accounts_df, dup_account], ignore_index=True)
        expected_active_count += 1
    elif variant == "medium":
        accounts_df = pd.concat([accounts_df] * 10, ignore_index=True)
        expected_active_count *= 10
    elif variant == "large":
        accounts_df = pd.concat([accounts_df] * 100, ignore_index=True)
        expected_active_count *= 100

    accounts_path = tmp_path / f"synthetic_{variant}_accounts.csv"
    transactions_path = tmp_path / f"synthetic_{variant}_transactions.csv" # Dummy
    balances_path = tmp_path / f"synthetic_{variant}_daily_balances.csv"   # Dummy

    # Write synthetic header row first
    with open(accounts_path, 'w') as f: f.write("H1,H2,H3,H4,H5\n")
    accounts_df.to_csv(accounts_path, mode='a', index=False, header=False)

    # Create dummy empty files for transactions and balances as they are required by the run signature
    pd.DataFrame(columns=[]).to_csv(transactions_path, index=False)
    pd.DataFrame(columns=[]).to_csv(balances_path, index=False)

    return accounts_path, transactions_path, balances_path, expected_active_count

@pytest.fixture
def setup_invalid_accounts_data(tmp_path: Path):
    """
    Fixture to create dummy accounts CSV files that should cause validation errors.
    Specifically, an ACTIVE account with a non-parsable account_open_date.
    """
    invalid_accounts_data = {
        "account_id": ["SYNTHETIC_ACCT_0001"],
        "customer_segment": ["RETAIL"],
        "account_open_date": ["not-a-date"], # This will cause pd.to_datetime to fail
        "account_status": ["ACTIVE"],
        "region": ["NORTH"],
    }
    accounts_df = pd.DataFrame(invalid_accounts_data)

    accounts_path = tmp_path / "synthetic_null_heavy_accounts.csv"
    transactions_path = tmp_path / "synthetic_null_heavy_transactions.csv" # Dummy
    balances_path = tmp_path / "synthetic_null_heavy_daily_balances.csv"   # Dummy

    with open(accounts_path, 'w') as f: f.write("H1,H2,H3,H4,H5\n")
    accounts_df.to_csv(accounts_path, mode='a', index=False, header=False)

    pd.DataFrame(columns=[]).to_csv(transactions_path, index=False)
    pd.DataFrame(columns=[]).to_csv(balances_path, index=False)

    return accounts_path, transactions_path, balances_path


@pytest.mark.parametrize(
    "setup_valid_accounts_data",
    ["clean", "duplicate_heavy", "medium", "large"],
    indirect=True,
)
def test_task11c_run_function_success(setup_valid_accounts_data: tuple[Path, Path, Path, int], variant: str):
    """
    Tests the run function from task11c.py for various dataset variants, expecting successful execution.
    It checks file creation, content, and schema validation for active accounts.
    """
    accounts_path, transactions_path, balances_path, expected_active_count = setup_valid_accounts_data

    # Call the ETL pipeline
    result = task11c.run(accounts_path, transactions_path, balances_path)

    # Assert that the function returns None as it writes to disk
    assert result is None

    # Verify the output file was created
    output_path = accounts_path.parent / "processed_active_accounts.csv"
    assert output_path.exists()
    
    output_df = pd.read_csv(output_path)

    # Assert expected output columns are present
    expected_output_columns = [
        "account_id", "customer_segment", "account_open_date", "account_status", "region"
    ]
    assert list(output_df.columns) == expected_output_columns
    
    # Assert that only ACTIVE accounts are in the output
    assert (output_df["account_status"] == "ACTIVE").all()

    # Assert row count matches the expected number of active accounts
    assert len(output_df) == expected_active_count

    # Further schema validation (date column should be parsed as datetime by pandas when read back)
    assert pd.api.types.is_datetime64_any_dtype(output_df["account_open_date"])


def test_task11c_run_function_validation_failure(setup_invalid_accounts_data: tuple[Path, Path, Path]):
    """
    Tests the run function from task11c.py for scenarios that should lead to validation errors.
    Specifically, an ACTIVE account with a non-parsable account_open_date.
    """
    accounts_path, transactions_path, balances_path = setup_invalid_accounts_data
    
    with pytest.raises(ValueError, match="Error converting column 'account_open_date' to datetime64\[ns\]"):
        task11c.run(accounts_path, transactions_path, balances_path)


@pytest.mark.parametrize(
    "setup_valid_accounts_data",
    ["null_heavy"], # Test null_heavy where nulls are in non-critical columns or for non-active accounts
    indirect=True,
)
def test_task11c_run_function_null_heavy(setup_valid_accounts_data: tuple[Path, Path, Path, int], variant: str):
    """
    Tests the run function from task11c.py for the null_heavy variant where nulls
    are in non-critical columns or for non-active accounts, expecting success.
    """
    accounts_path, transactions_path, balances_path, expected_active_count = setup_valid_accounts_data

    original_accounts_df = pd.read_csv(accounts_path, skiprows=1)
    
    # Modify original_accounts_df to introduce specific null_heavy characteristics for THIS test
    # Ensure ACTIVE accounts have valid dates but potentially null region/segment
    # Ensure CLOSED/SUSPENDED accounts can have nulls in critical columns as they are filtered out anyway.
    original_accounts_df.loc[original_accounts_df["account_id"] == "SYNTHETIC_ACCT_0003", "region"] = None # Active account with null region
    original_accounts_df.loc[original_accounts_df["account_id"] == "SYNTHETIC_ACCT_0002", "account_open_date"] = None # Closed account with null date

    # Rewrite the CSV with these specific null_heavy conditions
    with open(accounts_path, 'w') as f: f.write("H1,H2,H3,H4,H5\n")
    original_accounts_df.to_csv(accounts_path, mode='a', index=False, header=False)

    # Recalculate expected_active_count based on this modified data
    expected_active_count = len(original_accounts_df[original_accounts_df["account_status"] == "ACTIVE"])

    result = task11c.run(accounts_path, transactions_path, balances_path)
    assert result is None

    output_path = accounts_path.parent / "processed_active_accounts.csv"
    assert output_path.exists()
    output_df = pd.read_csv(output_path)

    assert not output_df.empty
    assert (output_df["account_status"] == "ACTIVE").all()
    assert len(output_df) == expected_active_count

    # Check that the active account with null region is still present and its region is NaN
    active_account_with_null_region = output_df[output_df["account_id"] == "SYNTHETIC_ACCT_0003"]
    assert not active_account_with_null_region.empty
    assert active_account_with_null_region["region"].isnull().all()

    # Ensure account_open_date for active accounts are not null
    assert output_df[output_df["account_status"] == "ACTIVE"]["account_open_date"].notnull().all()
    assert pd.api.types.is_datetime64_any_dtype(output_df["account_open_date"])
