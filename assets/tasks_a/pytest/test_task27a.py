# SYNTHETIC DATA — no real financial data
# Pytest: test_task27a.py | Tests: task27a.py (PY-027)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

import importlib
import pathlib
import sys
import pytest
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
task = importlib.import_module("task27a")

DATASET_DIR = pathlib.Path(__file__).parent.parent / "assets" / "datasets"

@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task27a(variant):
    """Test that task27a calculates RFM scores."""
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"
    
    result = task.run(accounts_path, transactions_path, balances_path)
    
    # Verify result is a DataFrame
    assert isinstance(result, pd.DataFrame)
    
    # Verify RFM columns exist
    assert 'recency' in result.columns
    assert 'frequency' in result.columns
    assert 'monetary' in result.columns
    assert 'recency_score' in result.columns
    assert 'frequency_score' in result.columns
    assert 'monetary_score' in result.columns
    assert 'rfm_score' in result.columns
    
    # Verify not empty
    assert len(result) > 0
