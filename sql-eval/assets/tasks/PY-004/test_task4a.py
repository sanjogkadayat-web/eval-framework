# SYNTHETIC DATA — no real financial data
# Pytest: test_task4a.py | Tests: task4a.py (PY-004)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

import importlib
import pathlib
import sys
import pytest
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
task = importlib.import_module("task4a")

DATASET_DIR = pathlib.Path(__file__).resolve().parents[2] / "datasets"

@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task4a(variant):
    """Test that task4a drops exact duplicate rows."""
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"
    
    result = task.run(accounts_path, transactions_path, balances_path)
    
    # Verify result is a DataFrame
    assert isinstance(result, pd.DataFrame)
    
    # Verify not empty
    assert len(result) > 0
    
    # Verify no exact duplicates remain
    assert result.duplicated().sum() == 0
    
    # For duplicate_heavy variant, expect row count reduction
    if variant == "duplicate_heavy":
        original = pd.read_csv(transactions_path)
        assert len(result) < len(original)
