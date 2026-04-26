# SYNTHETIC DATA — no real financial data
# Pytest: test_task30a.py | Tests: task30a.py (PY-030)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

import importlib
import pathlib
import sys
import pytest
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
task = importlib.import_module("task30a")

DATASET_DIR = pathlib.Path(__file__).resolve().parents[2] / "datasets"

@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task30a(variant):
    """Test that task30a provides parameterized test cases."""
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"
    
    result = task.run(accounts_path, transactions_path, balances_path)
    
    # Verify result is a DataFrame
    assert isinstance(result, pd.DataFrame)
    
    # Verify result contains deduplication metrics
    assert 'variant' in result.columns
    assert 'initial_count' in result.columns
    assert 'final_count' in result.columns
    assert 'duplicates_removed' in result.columns
    
    # For duplicate_heavy, expect duplicates removed > 0
    if variant == "duplicate_heavy":
        assert result['duplicates_removed'].iloc[0] > 0
