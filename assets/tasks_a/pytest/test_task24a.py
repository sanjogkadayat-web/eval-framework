# SYNTHETIC DATA — no real financial data
# Pytest: test_task24a.py | Tests: task24a.py (PY-024)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

import importlib
import pathlib
import sys
import pytest
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
task = importlib.import_module("task24a")

DATASET_DIR = pathlib.Path(__file__).parent.parent / "assets" / "datasets"

@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task24a(variant):
    """Test that task24a implements SCD Type 2 history tracking."""
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"
    
    result = task.run(accounts_path, transactions_path, balances_path)
    
    # Verify result is a DataFrame
    assert isinstance(result, pd.DataFrame)
    
    # Verify SCD Type 2 columns exist
    assert 'surrogate_key' in result.columns
    assert 'valid_from' in result.columns
    assert 'valid_to' in result.columns
    assert 'is_current' in result.columns
    
    # Verify not empty
    assert len(result) > 0
