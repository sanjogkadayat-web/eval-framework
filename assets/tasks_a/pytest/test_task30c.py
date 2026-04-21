import pandas as pd
import pytest
from pathlib import Path
import importlib, sys
import numpy as np

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).parent.parent / "assets" / "tasks_a" / "answers_python"))
task30c = importlib.import_module("task30c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task30c.py | Tests: task30c.py (PY-030)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

DATASET_DIR = Path(__file__).parent.parent / "assets" / "datasets"

@pytest.fixture(params=["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def variant(request):
    return request.param

@pytest.fixture
def dummy_data_path(tmp_path: Path, variant: str):
    """
    Fixture to create a dummy CSV file that will be passed to task30c.run.
    The content is generic since dummy_transform_function just returns the DataFrame.
    """
    dummy_data = {
        "col1": [1, 2, 3, 4, 5],
        "col2": ["A", "B", "C", "D", "E"],
        "col3": [10.0, 20.0, 30.0, 40.0, 50.0],
    }
    df = pd.DataFrame(dummy_data)

    if variant == "null_heavy":
        df.loc[0, "col1"] = None
        df.loc[2, "col2"] = None
    elif variant == "duplicate_heavy":
        df = pd.concat([df, df.iloc[[0, 1]]], ignore_index=True) # Add 2 duplicate rows
    elif variant == "medium":
        df = pd.concat([df] * 10, ignore_index=True)
    elif variant == "large":
        df = pd.concat([df] * 100, ignore_index=True)

    data_path = tmp_path / f"synthetic_{variant}_dummy.csv"
    with open(data_path, 'w') as f: f.write("H1,H2,H3\n") # Synthetic header
    df.to_csv(data_path, mode='a', index=False, header=False)

    return data_path


@pytest.mark.parametrize(
    "variant",
    ["clean", "null_heavy", "duplicate_heavy", "medium", "large"],
    indirect=True,
)
def test_task30c_dummy_transform_function(dummy_data_path: Path, variant: str):
    """
    Tests the dummy_transform_function from task30c.py to ensure it returns the input DataFrame unchanged.
    """
    # Read the dummy data as it would be read by task30c.run
    loaded_df = pd.read_csv(dummy_data_path, skiprows=1)

    # Call the dummy transformation function directly
    transformed_df = task30c.dummy_transform_function(loaded_df)

    # Assert that the function returns a DataFrame
    assert isinstance(transformed_df, pd.DataFrame)
    
    # Assert that the returned DataFrame is identical to the input DataFrame
    pd.testing.assert_frame_equal(transformed_df, loaded_df)


@pytest.mark.parametrize(
    "variant",
    ["clean", "null_heavy", "duplicate_heavy", "medium", "large"],
    indirect=True,
)
def test_task30c_run_function_returns_none(dummy_data_path: Path, variant: str):
    """
    Tests the run function from task30c.py to ensure it returns None as specified.
    This function is a placeholder and should not perform any actual transformations.
    """
    # Dummy paths for accounts, transactions, and balances.
    # dummy_data_path is used as a placeholder for accounts_path
    accounts_path = dummy_data_path
    transactions_path = Path("dummy_transactions.csv")
    balances_path = Path("dummy_balances.csv")

    result = task30c.run(accounts_path, transactions_path, balances_path)

    # Assert that the run function returns None
    assert result is None
