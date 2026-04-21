# SYNTHETIC DATA — no real financial data
# Pytest: test_task22c.py | Tests: task22c.py (PY-022)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

import importlib
import pathlib
import sys
import pytest
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
task = importlib.import_module("task22c")

DATASET_DIR = pathlib.Path(__file__).parent.parent.parent / "datasets"

@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task22c(variant):
    """Test that task22c generates an audit log DataFrame."""
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"
    
    result = task.run(accounts_path, transactions_path, balances_path)
    
    # Verify result is a DataFrame
    assert isinstance(result, pd.DataFrame)
    
    # Verify audit log columns exist
    assert 'step' in result.columns
    assert 'action' in result.columns
    assert 'rows_before' in result.columns
    assert 'rows_after' in result.columns
    
    # Verify not empty
    assert len(result) > 0
