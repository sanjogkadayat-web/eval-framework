# SYNTHETIC DATA — no real financial data
# Pytest: test_task25a.py | Tests: task25a.py (PY-025)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

import importlib
import pathlib
import sys
import pytest
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
task = importlib.import_module("task25a")

DATASET_DIR = pathlib.Path(__file__).parent.parent / "assets" / "datasets"

@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task25a(variant):
    """Test that task25a flags rolling z-score anomalies."""
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"
    
    result = task.run(accounts_path, transactions_path, balances_path)
    
    # Verify result is a DataFrame
    assert isinstance(result, pd.DataFrame)
    
    # Verify anomaly detection columns exist
    assert 'rolling_z_score' in result.columns
    assert 'is_anomaly' in result.columns
    
    # Verify not empty
    assert len(result) > 0
