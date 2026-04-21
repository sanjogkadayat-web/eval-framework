# SYNTHETIC DATA — no real financial data
# Pytest: test_task26a.py | Tests: task26a.py (PY-026)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

import importlib
import pathlib
import sys
import pytest
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
task = importlib.import_module("task26a")

DATASET_DIR = pathlib.Path(__file__).resolve().parents[2] / "datasets"

@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task26a(variant):
    """Test that task26a computes funnel drop-off."""
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"
    
    result = task.run(accounts_path, transactions_path, balances_path)
    
    # Verify result is a DataFrame
    assert isinstance(result, pd.DataFrame)
    
    # Verify funnel columns exist
    assert 'stage' in result.columns
    assert 'account_count' in result.columns
    assert 'drop_off_count' in result.columns
    assert 'drop_off_pct' in result.columns
    
    # Verify we have 3 funnel stages
    assert len(result) == 3
