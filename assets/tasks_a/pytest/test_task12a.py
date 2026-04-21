# SYNTHETIC DATA — no real financial data
# Pytest: test_task12a.py | Tests: task12a.py (PY-012)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

import importlib
import pathlib
import sys
import pytest
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
task = importlib.import_module("task12a")

DATASET_DIR = pathlib.Path(__file__).parent.parent / "assets" / "datasets"

@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task12a(variant):
    """Test that task12a creates running total of txn_amount."""
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"
    
    result = task.run(accounts_path, transactions_path, balances_path)
    
    # Verify result is a DataFrame
    assert isinstance(result, pd.DataFrame)
    
    # Verify running_total column exists
    assert 'running_total' in result.columns
    
    # Verify running total is non-negative for clean variant
    if variant == "clean":
        assert (result['running_total'] >= 0).all()
