# SYNTHETIC DATA — no real financial data
# Pytest: test_task1a.py | Tests: task1a.py (PY-001)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

import importlib
import pathlib
import sys
import pytest
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "answers_python"))
task = importlib.import_module("task1a")

DATASET_DIR = pathlib.Path(__file__).parent.parent.parent / "datasets"

@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task1a(variant):
    """Test that task1a loads accounts CSV and validates column names."""
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"
    
    result = task.run(accounts_path, transactions_path, balances_path)
    
    # Verify result is a DataFrame
    assert isinstance(result, pd.DataFrame)
    
    # Verify not empty
    assert len(result) > 0
    
    # Verify expected columns are present
    expected_columns = ['account_id', 'customer_segment', 'account_open_date', 'account_status', 'region']
    assert list(result.columns) == expected_columns
