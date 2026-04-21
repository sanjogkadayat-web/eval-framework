# SYNTHETIC DATA — no real financial data
# Pytest: test_task23c.py | Tests: task23c.py (PY-023)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

import importlib
import pathlib
import sys
import pytest
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
task = importlib.import_module("task23c")

DATASET_DIR = pathlib.Path(__file__).parent.parent.parent / "datasets"

@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task23c(variant):
    """Test that task23c runs end-to-end pipeline."""
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
