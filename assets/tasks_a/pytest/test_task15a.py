# SYNTHETIC DATA — no real financial data
# Pytest: test_task15a.py | Tests: task15a.py (PY-015)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

import importlib
import pathlib
import sys
import pytest
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "answers_python"))
task = importlib.import_module("task15a")

DATASET_DIR = pathlib.Path(__file__).parent.parent.parent / "datasets"

@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task15a(variant):
    """Test that task15a adds previous_txn_amount feature."""
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"
    
    result = task.run(accounts_path, transactions_path, balances_path)
    
    # Verify result is a DataFrame
    assert isinstance(result, pd.DataFrame)
    
    # Verify previous_txn_amount column exists
    assert 'previous_txn_amount' in result.columns
