# SYNTHETIC DATA — no real financial data
# Pytest: test_task23a.py | Tests: task23a.py (PY-023)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

import importlib
import pathlib
import sys
import pytest
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
task = importlib.import_module("task23a")

DATASET_DIR = pathlib.Path(__file__).resolve().parents[2] / "datasets"

@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task23a(variant):
    """Test that task23a runs end-to-end pipeline."""
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"
    
    result = task.run(accounts_path, transactions_path, balances_path)
    
    # Verify result is a DataFrame
    assert isinstance(result, pd.DataFrame)
    
    # Verify feature engineering columns exist
    assert 'month' in result.columns
    assert 'is_weekend' in result.columns
    
    # For large variant, verify completes without memory errors
    if variant == "large":
        assert len(result) > 0
