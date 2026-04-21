# SYNTHETIC DATA — no real financial data
# Pytest: test_task2c.py | Tests: task2c.py (PY-002)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

import importlib
import pathlib
import sys
import pytest
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
task = importlib.import_module("task2c")

DATASET_DIR = pathlib.Path(__file__).parent.parent.parent / "datasets"

@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task2c(variant):
    """Test that task2c validates date and numeric columns."""
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"
    
    result = task.run(accounts_path, transactions_path, balances_path)
    
    # Verify result is a DataFrame
    assert isinstance(result, pd.DataFrame)
    
    # Verify not empty
    assert len(result) > 0
    
    # Verify expected columns
    assert 'table' in result.columns
    assert 'date_column_validated' in result.columns
    assert 'status' in result.columns
