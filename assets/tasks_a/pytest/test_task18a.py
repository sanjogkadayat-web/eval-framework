# SYNTHETIC DATA — no real financial data
# Pytest: test_task18a.py | Tests: task18a.py (PY-018)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

import importlib
import pathlib
import sys
import pytest
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
task = importlib.import_module("task18a")

DATASET_DIR = pathlib.Path(__file__).parent.parent / "assets" / "datasets"

@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task18a(variant):
    """Test that task18a flags invalid txn_date earlier than account_open_date."""
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"
    
    result = task.run(accounts_path, transactions_path, balances_path)
    
    # Verify result is a DataFrame
    assert isinstance(result, pd.DataFrame)
    
    # Verify invalid_txn_date column exists
    assert 'invalid_txn_date' in result.columns
