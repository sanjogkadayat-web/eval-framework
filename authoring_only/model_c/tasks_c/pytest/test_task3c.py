import pandas as pd
import pytest
from pathlib import Path
import importlib, sys

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).parent.parent / "assets" / "tasks_a" / "answers_python"))
task3c = importlib.import_module("task3c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task3c.py | Tests: task3c.py (PY-003)
# Tests: Counting nulls per column and raising error if threshold is exceeded.
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

DATASET_DIR = Path(__file__).parent.parent / "assets" / "datasets"

@pytest.fixture(params=["clean", "below_threshold", "above_threshold", "all_null_column", "empty_df", "duplicate_heavy", "medium", "large"])
def create_transactions_csv(tmp_path: Path, request):
    """
    Fixture to create dummy transactions CSV files for different null scenarios.
    """
    variant = request.param

    base_data = {
        "txn_id": [f"SYNTHETIC_TXN_{i:06d}" for i in range(1, 6)],
        "account_id": [f"SYNTHETIC_ACCT_{i:04d}" for i in range(1, 6)],
        "txn_date": ["2023-01-05", "2023-02-20", "2023-03-25", "2023-04-15", "2023-05-10"],
        "txn_amount": [100.50, 200.75, 50.25, 150.00, 300.10],
        "txn_type": ["PURCHASE", "REFUND", "TRANSFER", "FEE", "PURCHASE"],
        "merchant_category": ["RETAIL", "GROCERY", "TRAVEL", "DINING", "UTILITIES"],
        "channel": ["ONLINE", "BRANCH", "ATM", "MOBILE", "ONLINE"],
        "is_flagged": [False, False, True, False, True],
    }
    df = pd.DataFrame(base_data)

    if variant == "below_threshold": # e.g., 20% nulls on txn_amount (threshold is 30%)
        df.loc[[0], "txn_amount"] = None
    elif variant == "above_threshold": # e.g., 40% nulls on txn_amount
        df.loc[[0, 1], "txn_amount"] = None
    elif variant == "all_null_column": # All nulls in a column
        df["txn_amount"] = None
    elif variant == "empty_df":
        df = pd.DataFrame(columns=df.columns)
    elif variant == "duplicate_heavy":
        df = pd.concat([df, df.iloc[[0, 1]]], ignore_index=True) # Add 2 duplicate rows
        # Introduce nulls in duplicates to test consistency if needed
        df.loc[len(base_data), "txn_amount"] = None # Add a null to a duplicated row
    elif variant == "medium":
        df = pd.concat([df] * 10, ignore_index=True)
    elif variant == "large":
        df = pd.concat([df] * 100, ignore_index=True)

    transactions_path = tmp_path / f"synthetic_{variant}_transactions.csv"
    
    # Write synthetic header row first
    with open(transactions_path, 'w') as f:
        f.write("H1,H2,H3,H4,H5,H6,H7,H8\n") # Placeholder for synthetic header
    
    df.to_csv(transactions_path, mode='a', index=False, header=False)
    
    # Dummy files for accounts and balances as they are not used in task3c.run
    accounts_path = tmp_path / f"synthetic_{variant}_accounts.csv"
    balances_path = tmp_path / f"synthetic_{variant}_daily_balances.csv"
    pd.DataFrame(columns=[]).to_csv(accounts_path, index=False)
    pd.DataFrame(columns=[]).to_csv(balances_path, index=False)

    # Store expected column for error message check if this is an above_threshold test
    if variant == "above_threshold":
        request.node.add_marker(pytest.mark.xfail(raises=ValueError, reason="Expected ValueError due to null threshold"))

    return accounts_path, transactions_path, balances_path


@pytest.mark.parametrize(
    "create_transactions_csv",
    ["clean", "below_threshold", "duplicate_heavy", "medium", "large"],
    indirect=True,
)
def test_task3c_run_within_threshold(create_transactions_csv):
    """
    Tests the run function from task3c.py for scenarios where nulls are within
    the acceptable threshold or there are no nulls, expecting successful execution.
    """
    accounts_path, transactions_path, balances_path = create_transactions_csv
    result_df = task3c.run(accounts_path, transactions_path, balances_path)

    assert isinstance(result_df, pd.DataFrame)

    # Ensure the 'null_percentage' column exists and is numeric
    assert "null_percentage" in result_df.columns
    assert pd.api.types.is_float_dtype(result_df["null_percentage"])

    # Verify that no column exceeds the 30% null threshold
    assert (result_df["null_percentage"] <= 0.30).all()


@pytest.mark.parametrize(
    "create_transactions_csv, expected_col_in_error",
    [
        ("above_threshold", "txn_amount"),
        ("all_null_column", "txn_amount"),
    ],
    indirect=True,
)
def test_task3c_run_exceeds_threshold(create_transactions_csv, expected_col_in_error):
    """
    Tests the run function from task3c.py for scenarios where nulls exceed the
    threshold, expecting a ValueError.
    """
    accounts_path, transactions_path, balances_path = create_transactions_csv
    with pytest.raises(ValueError) as excinfo:
        task3c.run(accounts_path, transactions_path, balances_path)
    assert f"Column '{expected_col_in_error}' exceeds null threshold" in str(excinfo.value)


def test_task3c_run_empty_df(create_transactions_csv):
    """
    Tests the run function with an empty DataFrame, expecting it to return
    a DataFrame with null_percentage for all columns (which will be 0 as there are no rows/nulls).
    """
    accounts_path, transactions_path, balances_path = create_transactions_csv # This fixture is parametrized with empty_df
    result_df = task3c.run(accounts_path, transactions_path, balances_path)

    assert isinstance(result_df, pd.DataFrame)
    # For an empty DF, the null_percentage should be 0 for all columns (no nulls in an empty set of data)
    assert result_df.empty or (result_df["null_percentage"].sum() == 0.0) # all percentages should be 0.0 or nan if no columns
    # Ensure it still has the expected columns, even if empty
    expected_columns = ["column_name", "null_count", "total_rows", "null_percentage"]
    assert sorted(list(result_df.columns)) == sorted(expected_columns)
