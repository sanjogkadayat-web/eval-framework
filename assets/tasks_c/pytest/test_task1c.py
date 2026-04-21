import pandas as pd
import pytest
from pathlib import Path
import importlib, sys

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).parent.parent / "assets" / "tasks_a" / "answers_python"))
task1c = importlib.import_module("task1c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task1c.py | Tests: task1c.py (PY-001)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

DATASET_DIR = Path(__file__).parent.parent / "assets" / "datasets"

@pytest.fixture
def create_dummy_accounts_csv(tmp_path: Path, variant: str):
    """
    Fixture to create dummy accounts CSV files for different variants.
    """
    data = {
        "account_id": [f"SYNTHETIC_ACCT_{i:04d}" for i in range(1, 6)],
        "customer_segment": ["RETAIL", "SMALL_BIZ", "WEALTH", "STUDENT", "RETAIL"],
        "account_open_date": ["2020-01-01", "2021-02-01", "2022-03-01", "2023-04-01", "2024-05-01"],
        "account_status": ["ACTIVE", "ACTIVE", "CLOSED", "SUSPENDED", "ACTIVE"],
        "region": ["NORTH", "SOUTH", "EAST", "WEST", "NORTH"],
    }
    df = pd.DataFrame(data)

    # Introduce specific characteristics for variants
    if variant == "null_heavy":
        df.loc[0, "account_id"] = None
        df.loc[2, "customer_segment"] = None
    elif variant == "duplicate_heavy":
        df = pd.concat([df, df.iloc[[0, 1]]], ignore_index=True) # Add 2 duplicate rows
    elif variant == "medium":
        df = pd.concat([df] * 10, ignore_index=True)
    elif variant == "large":
        df = pd.concat([df] * 100, ignore_index=True)

    accounts_path = tmp_path / f"synthetic_{variant}_accounts.csv"
    
    # Write synthetic header row first
    with open(accounts_path, 'w') as f:
        f.write("H1,H2,H3,H4,H5\n") # Placeholder for synthetic header (skipped by task1c.py)
    
    df.to_csv(accounts_path, mode='a', index=False, header=False)
    
    return accounts_path


@pytest.mark.parametrize(
    "variant",
    ["clean", "null_heavy", "duplicate_heavy", "medium", "large"],
    indirect=True,
)
def test_task1c_run_function(create_dummy_accounts_csv: Path, variant: str):
    """
    Tests the run function from task1c.py for various dataset variants.
    It checks if the accounts CSV is loaded correctly, the synthetic header is skipped,
    and the expected column names are asserted.
    """
    accounts_path = create_dummy_accounts_csv
    transactions_path = Path("dummy_transactions.csv") # Not used in task1c.run
    balances_path = Path("dummy_balances.csv")     # Not used in task1c.run

    expected_columns = [
        "account_id", "customer_segment", "account_open_date", "account_status", "region",
    ]

    if variant == "null_heavy":
        # Expect ValueError due to missing 'account_id' column from the original data definition
        # task1c.py asserts list(accounts_df.columns) == expected_columns. Nulls won't cause this to fail.
        # The primary test here is column validation, which should pass even with nulls in data.
        # However, if an entire column is missing, it would fail.
        # For this test, assume only valid CSVs are provided, even for null_heavy. Nulls are within cells, not missing columns.
        pass
    
    result_df = task1c.run(accounts_path, transactions_path, balances_path)

    assert isinstance(result_df, pd.DataFrame)
    assert list(result_df.columns) == expected_columns
    assert len(result_df) >= 4 # Ensure at least some rows are loaded, depends on variant logic

    if variant == "duplicate_heavy":
        # Assert that the number of rows is greater than the base due to duplicates
        assert len(result_df) == 5 + 2
    elif variant == "clean":
        assert len(result_df) == 5
    elif variant == "medium":
        assert len(result_df) == 5 * 10
    elif variant == "large":
        assert len(result_df) == 5 * 100
