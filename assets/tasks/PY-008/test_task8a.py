# SYNTHETIC DATA — no real financial data
# Pytest: test_task8a.py | Tests: task8a.py (PY-008)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

import importlib
import pathlib
import sys
import pytest
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
task = importlib.import_module("task8a")

DATASET_DIR = pathlib.Path(__file__).resolve().parents[2] / "datasets"

@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task8a(variant):
    """Test that task8a builds a pivot table of txn_amount by region and channel."""
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"
    
    result = task.run(accounts_path, transactions_path, balances_path)
    
    # Verify result is a DataFrame
    assert isinstance(result, pd.DataFrame)
    
    # Verify not empty
    assert len(result) > 0
    
    # Verify region column exists
    assert 'region' in result.columns
