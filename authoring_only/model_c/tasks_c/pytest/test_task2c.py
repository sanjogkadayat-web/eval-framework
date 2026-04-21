import pandas as pd
import pytest
from pathlib import Path
import importlib, sys
import numpy as np

# Adjust the path to import from the directory containing task files
sys.path.insert(0, str(Path(__file__).parent.parent / "assets" / "tasks_a" / "answers_python"))
task2c = importlib.import_module("task2c")

# SYNTHETIC DATA — no real financial data
# Pytest: test_task2c.py | Tests: task2c.py (PY-002)
# Tests: Validation of date and numeric column dtypes.
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

DATASET_DIR = Path(__file__).parent.parent / "assets" / "datasets"

@pytest.fixture(params=["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def variant(request):
    return request.param

@pytest.fixture
def create_dummy_csv_files(tmp_path: Path, variant: str, request):
    """
    Fixture to create dummy CSV files for different variants and specific invalid data scenarios.
    The 'request' fixture is used to access parametrization for custom data types.
    """
    accounts_data = {
        "account_id": [f"SYNTHETIC_ACCT_{i:04d}" for i in range(1, 6)],
        "customer_segment": ["RETAIL", "SMALL_BIZ", "WEALTH", "STUDENT", "RETAIL"],
        "account_open_date": ["2023-01-01", "2023-02-15", "2023-03-20", "2023-04-10", "2023-05-05"],
        "account_status": ["ACTIVE", "ACTIVE", "CLOSED", "SUSPENDED", "ACTIVE"],
        "region": ["NORTH", "SOUTH", "EAST", "WEST", "NORTH"],
    }
    transactions_data = {
        "txn_id": [f"SYNTHETIC_TXN_{i:06d}" for i in range(1, 6)],
        "account_id": [f"SYNTHETIC_ACCT_{i:04d}" for i in range(1, 6)],
        "txn_date": ["2023-01-05", "2023-02-20", "2023-03-25", "2023-04-15", "2023-05-10"],
        "txn_amount": [100.50, 200.75, 50.25, 150.00, 300.10],
        "txn_type": ["PURCHASE", "REFUND", "TRANSFER", "FEE", "PURCHASE"],
        "merchant_category": ["RETAIL", "GROCERY", "TRAVEL", "DINING", "UTILITIES"],
        "channel": ["ONLINE", "BRANCH", "ATM", "MOBILE", "ONLINE"],
        "is_flagged": [False, False, True, False, True],
    }
    balances_data = {
        "account_id": [f"SYNTHETIC_ACCT_{i:04d}" for i in range(1, 6)],
        "balance_date": ["2024-10-03", "2024-10-04", "2024-10-05", "2024-10-06", "2024-10-07"],
        "closing_balance": [1000.00, 950.00, 1050.00, 900.00, 1100.00],
        "txn_count_day": [1, 2, 1, 3, 2],
    }

    accounts_df = pd.DataFrame(accounts_data)
    transactions_df = pd.DataFrame(transactions_data)
    balances_df = pd.DataFrame(balances_data)

    # Apply variant-specific modifications
    if variant == "null_heavy":
        accounts_df.loc[0, "account_open_date"] = None
        transactions_df.loc[1, "txn_amount"] = None
        balances_df.loc[2, "closing_balance"] = None
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
    
    # Custom invalid data for specific test cases
    if hasattr(request, 'param') and isinstance(request.param, dict):
        param_dict = request.param
        if param_dict.get("type") == "invalid_date":
            if param_dict["invalid_col"] == "account_open_date":
                accounts_df.loc[0, "account_open_date"] = param_dict["invalid_value"]
            elif param_dict["invalid_col"] == "txn_date":
                transactions_df.loc[0, "txn_date"] = param_dict["invalid_value"]
            elif param_dict["invalid_col"] == "balance_date":
                balances_df.loc[0, "balance_date"] = param_dict["invalid_value"]
        elif param_dict.get("type") == "invalid_numeric":
            if param_dict["invalid_col"] == "txn_amount":
                transactions_df.loc[0, "txn_amount"] = param_dict["invalid_value"]
            elif param_dict["invalid_col"] == "closing_balance":
                balances_df.loc[0, "closing_balance"] = param_dict["invalid_value"]
            elif param_dict["invalid_col"] == "txn_count_day":
                balances_df.loc[0, "txn_count_day"] = param_dict["invalid_value"]


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
    "create_dummy_csv_files",
    [
        {"type": "clean"},
        {"type": "null_heavy", "invalid_col": None, "invalid_value": None}, # no specific invalid values, just nulls
        {"type": "duplicate_heavy", "invalid_col": None, "invalid_value": None},
        {"type": "medium", "invalid_col": None, "invalid_value": None},
        {"type": "large", "invalid_col": None, "invalid_value": None},
    ],
    indirect=True,
)
def test_task2c_run_valid_data(create_dummy_csv_files):
    """
    Tests the run function from task2c.py with valid data (including expected nulls/duplicates)
    to ensure no unexpected errors are raised and dtypes are correct.
    """
    accounts_path, transactions_path, balances_path = create_dummy_csv_files
    result = task2c.run(accounts_path, transactions_path, balances_path)
    assert result is None # task2c.py does not return a dataframe, but asserts internally


@pytest.mark.parametrize(
    "create_dummy_csv_files",
    [
        {"type": "invalid_date", "invalid_col": "account_open_date", "invalid_value": "not-a-date"},
        {"type": "invalid_date", "invalid_col": "txn_date", "invalid_value": "bad-date"},
        {"type": "invalid_date", "invalid_col": "balance_date", "invalid_value": "invalid_date_string"},
    ],
    indirect=True,
)
def test_task2c_run_invalid_date_data(create_dummy_csv_files):
    """
    Tests the run function from task2c.py with invalid date data, expecting ValueError.
    """
    accounts_path, transactions_path, balances_path = create_dummy_csv_files
    with pytest.raises(ValueError) as excinfo:
        task2c.run(accounts_path, transactions_path, balances_path)
    assert "Error converting column" in str(excinfo.value) and "to datetime64[ns]" in str(excinfo.value)


@pytest.mark.parametrize(
    "create_dummy_csv_files",
    [
        {"type": "invalid_numeric", "invalid_col": "txn_amount", "invalid_value": "abc"},
        {"type": "invalid_numeric", "invalid_col": "closing_balance", "invalid_value": "not_a_num"},
        {"type": "invalid_numeric", "invalid_col": "txn_count_day", "invalid_value": "XYZ"},
    ],
    indirect=True,
)
def test_task2c_run_invalid_numeric_data(create_dummy_csv_files):
    """
    Tests the run function from task2c.py with invalid numeric data, expecting ValueError.
    """
    accounts_path, transactions_path, balances_path = create_dummy_csv_files
    with pytest.raises(ValueError) as excinfo:
        task2c.run(accounts_path, transactions_path, balances_path)
    assert "Error converting column" in str(excinfo.value) and ("to float64" in str(excinfo.value) or "to int64" in str(excinfo.value))
