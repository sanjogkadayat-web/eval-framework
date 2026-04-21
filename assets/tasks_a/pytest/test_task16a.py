# SYNTHETIC DATA — no real financial data
# Pytest: test_task16a.py | Tests: task16a.py (PY-016)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

import importlib
import pathlib
import sys
import pytest
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
task = importlib.import_module("task16a")

DATASET_DIR = pathlib.Path(__file__).parent.parent / "assets" / "datasets"

@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task16a(variant):
    """Test that task16a extracts temporal features from txn_date."""
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"
    
    result = task.run(accounts_path, transactions_path, balances_path)
    
    # Verify result is a DataFrame
    assert isinstance(result, pd.DataFrame)
    
    # Verify temporal feature columns exist
    assert 'day_of_week' in result.columns
    assert 'month' in result.columns
    assert 'quarter' in result.columns
    assert 'is_weekend' in result.columns
    
    # Verify values are in valid ranges
    if variant == "clean":
        assert result['day_of_week'].between(0, 6).all()
        assert result['month'].between(1, 12).all()
        assert result['quarter'].between(1, 4).all()
