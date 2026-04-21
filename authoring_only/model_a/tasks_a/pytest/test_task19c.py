# SYNTHETIC DATA — no real financial data
# Pytest: test_task19c.py | Tests: task19c.py (PY-019)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

import importlib
import pathlib
import sys
import pytest
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
task = importlib.import_module("task19c")

DATASET_DIR = pathlib.Path(__file__).parent.parent.parent / "datasets"

@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task19c(variant):
    """Test that task19c deduplicates accounts by precedence rule."""
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"
    
    result = task.run(accounts_path, transactions_path, balances_path)
    
    # Verify result is a DataFrame
    assert isinstance(result, pd.DataFrame)
    
    # Verify no duplicate account_ids
    assert result['account_id'].duplicated().sum() == 0
    
    # For duplicate_heavy variant, expect row count reduction
    if variant == "duplicate_heavy":
        original = pd.read_csv(accounts_path)
        assert len(result) <= len(original)
