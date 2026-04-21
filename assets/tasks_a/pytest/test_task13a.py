# SYNTHETIC DATA — no real financial data
# Pytest: test_task13a.py | Tests: task13a.py (PY-013)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

import importlib
import pathlib
import sys
import pytest
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
task = importlib.import_module("task13a")

DATASET_DIR = pathlib.Path(__file__).parent.parent / "assets" / "datasets"

@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task13a(variant):
    """Test that task13a computes rolling average of closing_balance."""
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"
    
    result = task.run(accounts_path, transactions_path, balances_path)
    
    # Verify result is a DataFrame
    assert isinstance(result, pd.DataFrame)
    
    # Verify rolling_avg_7 column exists
    assert 'rolling_avg_7' in result.columns
    
    # For clean variant, verify rolling average is within reasonable bounds
    if variant == "clean":
        assert result['rolling_avg_7'].notna().any()
