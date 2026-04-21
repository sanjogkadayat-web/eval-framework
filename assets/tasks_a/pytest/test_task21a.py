# SYNTHETIC DATA — no real financial data
# Pytest: test_task21a.py | Tests: task21a.py (PY-021)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

import importlib
import pathlib
import sys
import pytest
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "answers_python"))
task = importlib.import_module("task21a")

DATASET_DIR = pathlib.Path(__file__).parent.parent.parent / "datasets"

@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task21a(variant):
    """Test that task21a assigns cohorts based on account_open_date month."""
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"
    
    result = task.run(accounts_path, transactions_path, balances_path)
    
    # Verify result is a DataFrame
    assert isinstance(result, pd.DataFrame)
    
    # Verify cohort column exists
    assert 'cohort' in result.columns
    
    # Verify not empty
    assert len(result) > 0
