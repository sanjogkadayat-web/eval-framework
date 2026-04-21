import importlib
import pathlib
import sys

import pandas as pd
import pytest

# SYNTHETIC DATA — no real financial data
# Pytest: test_task27b.py | Tests: task27b.py (PY-027)
# Variants tested: clean, null_heavy, duplicate_heavy, medium, large

TASK_DIR = pathlib.Path(__file__).resolve().parents[1] / "answers_python"
sys.path.insert(0, str(TASK_DIR))
task = importlib.import_module("task27b")

DATASET_DIR = pathlib.Path(__file__).resolve().parents[2] / "datasets"


@pytest.mark.parametrize("variant", ["clean", "null_heavy", "duplicate_heavy", "medium", "large"])
def test_task27b_rfm(variant: str) -> None:
    accounts_path = DATASET_DIR / f"synthetic_{variant}_accounts.csv"
    transactions_path = DATASET_DIR / f"synthetic_{variant}_transactions.csv"
    balances_path = DATASET_DIR / f"synthetic_{variant}_daily_balances.csv"

    out = task.run(accounts_path, transactions_path, balances_path)
    assert isinstance(out, pd.DataFrame)
    expected = {"account_id", "recency_days", "frequency", "monetary", "r_score", "f_score", "m_score", "rfm_score"}
    assert expected.issubset(set(out.columns))
