#!/usr/bin/env python3
"""
Comprehensive evaluation script for SQL and Python tasks.
Runs 60 tasks (30 SQL + 30 Python) across 5 dataset variants each.
Collects metrics: tokens, runtime, memory, formatting, tests, checksums.
"""

import csv
import hashlib
import importlib.util
import io
import pathlib
import re
import subprocess
import sys
import time
import tracemalloc
from contextlib import redirect_stdout, redirect_stderr

import duckdb
import pandas as pd
import tiktoken

from task_prompts import SQL_PROMPTS, PYTHON_PROMPTS

# Constants
WORKSPACE = pathlib.Path(__file__).parent
DATASET_DIR = WORKSPACE / "assets" / "datasets"
SQL_DIR = WORKSPACE / "assets" / "tasks_a" / "answers_sql"
PYTHON_DIR = WORKSPACE / "assets" / "tasks_a" / "answers_python"
PYTEST_DIR = WORKSPACE / "assets" / "tasks_a" / "pytest"
RESULTS_CSV = WORKSPACE / "results_table_a.csv"

VARIANTS = ["clean", "null_heavy", "duplicate_heavy", "medium", "large"]

# Token encoder - initialize lazily to avoid startup failures
_enc = None


def get_encoder():
    """Get or initialize the tiktoken encoder."""
    global _enc
    if _enc is None:
        try:
            _enc = tiktoken.get_encoding("cl100k_base")
        except Exception as e:
            print(f"⚠️  Warning: Could not load tiktoken encoder: {e}")
            print("    Using approximate token count (text length / 4)")
            _enc = "fallback"
    return _enc


def count_tokens(text):
    """Count tokens using tiktoken cl100k_base encoding."""
    enc = get_encoder()
    if enc == "fallback":
        # Approximate: ~4 characters per token
        return len(text) // 4
    return len(enc.encode(text))


def get_dataset_paths(variant):
    """Get paths to the three dataset files for a variant."""
    return {
        "accounts": DATASET_DIR / f"synthetic_{variant}_accounts.csv",
        "transactions": DATASET_DIR / f"synthetic_{variant}_transactions.csv",
        "daily_balances": DATASET_DIR / f"synthetic_{variant}_daily_balances.csv",
    }


def run_sqlfluff(sql_file):
    """
    Run sqlfluff lint on a SQL file.
    Returns formatting_pass_pct: ((checked - violations) / checked) * 100
    """
    try:
        result = subprocess.run(
            ["sqlfluff", "lint", str(sql_file), "--dialect", "ansi"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        # Parse output to find violations
        # sqlfluff typically outputs: "X violations detected"
        violations = 0
        checked = 1  # At least 1 file checked
        
        for line in result.stdout.splitlines():
            if "violations" in line.lower():
                match = re.search(r"(\d+)\s+violations?", line, re.IGNORECASE)
                if match:
                    violations = int(match.group(1))
        
        # Count lines of SQL (approximate "checked" count)
        with open(sql_file, 'r') as f:
            sql_lines = [l for l in f.readlines() if l.strip() and not l.strip().startswith('--')]
            checked = max(len(sql_lines), 1)
        
        formatting_pass_pct = ((checked - violations) / checked) * 100
        return round(formatting_pass_pct, 2)
    except Exception as e:
        print(f"  ⚠️  sqlfluff error: {e}")
        return 0.0


def run_flake8(py_file):
    """
    Run flake8 on a Python file.
    Returns formatting_pass_pct: ((checked - violations) / checked) * 100
    """
    try:
        result = subprocess.run(
            ["flake8", str(py_file), "--count"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        # flake8 with --count outputs violations count on last line
        violations = 0
        if result.stdout.strip():
            last_line = result.stdout.strip().splitlines()[-1]
            if last_line.isdigit():
                violations = int(last_line)
        
        # Count lines of code
        with open(py_file, 'r') as f:
            code_lines = [l for l in f.readlines() if l.strip() and not l.strip().startswith('#')]
            checked = max(len(code_lines), 1)
        
        formatting_pass_pct = ((checked - violations) / checked) * 100
        return round(formatting_pass_pct, 2)
    except Exception as e:
        print(f"  ⚠️  flake8 error: {e}")
        return 0.0


def run_pytest_for_variant(test_file, variant):
    """
    Run pytest for a specific test file and variant.
    Returns pytest_pass_pct: (passed / total) * 100
    """
    try:
        # Run pytest with the specific variant parameter
        result = subprocess.run(
            ["pytest", str(test_file), "-v", "-k", variant],
            capture_output=True,
            text=True,
            timeout=120,
        )
        
        # Parse pytest output for pass/fail counts
        passed = 0
        total = 0
        
        for line in result.stdout.splitlines():
            # Look for: "test_taskXa.py::test_taskXa[variant] PASSED"
            if "PASSED" in line:
                passed += 1
                total += 1
            elif "FAILED" in line or "ERROR" in line:
                total += 1
        
        # Also check summary line: "1 passed in 0.05s"
        for line in result.stdout.splitlines():
            if " passed" in line or " failed" in line:
                match = re.search(r"(\d+)\s+passed", line)
                if match:
                    passed = int(match.group(1))
                match = re.search(r"(\d+)\s+failed", line)
                if match:
                    total = passed + int(match.group(1))
                match = re.search(r"(\d+)\s+error", line)
                if match:
                    total = passed + int(match.group(1))
        
        if total == 0:
            return 0.0
        
        pytest_pass_pct = (passed / total) * 100
        return round(pytest_pass_pct, 2)
    except Exception as e:
        print(f"  ⚠️  pytest error: {e}")
        return 0.0


def compute_checksum(data_bytes):
    """Compute SHA256 checksum of bytes."""
    return hashlib.sha256(data_bytes).hexdigest()


def evaluate_sql_task(task_num, variant):
    """
    Evaluate a single SQL task against a dataset variant.
    Returns dict of metrics.
    """
    print(f"  📊 SQL Task {task_num}, Variant: {variant}")
    
    sql_file = SQL_DIR / f"task{task_num}a.sql"
    
    # Read SQL content
    with open(sql_file, 'r') as f:
        sql_content = f.read()
    
    # Token counting
    prompt = SQL_PROMPTS[task_num]
    token_input = count_tokens(prompt)
    token_output = count_tokens(sql_content)
    
    # Formatting check (same for all variants)
    formatting_pass_pct = run_sqlfluff(sql_file)
    
    # Get dataset paths
    datasets = get_dataset_paths(variant)
    
    # Prepare SQL by replacing table names with variant-specific paths
    sql_executed = sql_content
    for table_type, path in datasets.items():
        # Replace synthetic_clean_X with synthetic_{variant}_X
        old_pattern = f"synthetic_clean_{table_type}"
        new_table = f"synthetic_{variant}_{table_type}"
        sql_executed = sql_executed.replace(old_pattern, new_table)
    
    # Execute SQL with DuckDB
    runtime_ms = None
    checksum = None
    row_count = None
    snapshot_pass = False
    
    try:
        conn = duckdb.connect(":memory:")
        
        # Load datasets using pandas first (handles comment lines)
        for table_type, path in datasets.items():
            table_name = f"synthetic_{variant}_{table_type}"
            # Load with pandas, parsing date columns
            parse_dates = []
            if table_type == "accounts":
                parse_dates = ["account_open_date"]
            elif table_type == "transactions":
                parse_dates = ["txn_date"]
            elif table_type == "daily_balances":
                parse_dates = ["balance_date"]
            
            df = pd.read_csv(path, comment='#', parse_dates=parse_dates)
            # Register DataFrame with DuckDB
            conn.register(table_name, df)
        
        # Execute query with timing
        start = time.perf_counter()
        result = conn.execute(sql_executed).df()
        runtime_ms = int((time.perf_counter() - start) * 1000)
        
        # Compute metrics
        row_count = len(result)
        
        # Convert to CSV bytes for checksum
        csv_buffer = io.StringIO()
        result.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue().encode('utf-8')
        checksum = compute_checksum(csv_bytes)
        
        # For now, snapshot_pass is always False (would need reference CSVs)
        snapshot_pass = False
        
        conn.close()
    except Exception as e:
        print(f"    ❌ SQL execution error: {e}")
        runtime_ms = 0
        row_count = 0
        checksum = ""
    
    return {
        "filename": f"task{task_num}a.sql",
        "dataset_variant": variant,
        "token_usage_input": token_input,
        "token_usage_output": token_output,
        "runtime_ms": runtime_ms,
        "peak_memory_bytes": None,  # SQL doesn't track memory
        "formatting_pass_pct": formatting_pass_pct,
        "pytest_filename": None,
        "pytest_pass_pct": None,
        "checksum": checksum,
        "row_count": row_count,
        "snapshot_pass": snapshot_pass,
    }


def evaluate_python_task(task_num, variant):
    """
    Evaluate a single Python task against a dataset variant.
    Returns dict of metrics.
    """
    print(f"  🐍 Python Task {task_num}, Variant: {variant}")
    
    py_file = PYTHON_DIR / f"task{task_num}a.py"
    test_file = PYTEST_DIR / f"test_task{task_num}a.py"
    
    # Read Python content
    with open(py_file, 'r') as f:
        py_content = f.read()
    
    # Token counting
    prompt = PYTHON_PROMPTS[task_num]
    token_input = count_tokens(prompt)
    token_output = count_tokens(py_content)
    
    # Formatting check (same for all variants)
    formatting_pass_pct = run_flake8(py_file)
    
    # Get dataset paths
    datasets = get_dataset_paths(variant)
    
    # Run pytest for this variant
    pytest_pass_pct = run_pytest_for_variant(test_file, variant)
    
    # Measure runtime and memory by running the task directly
    runtime_ms = None
    peak_memory_bytes = None
    
    try:
        # Load the module dynamically
        spec = importlib.util.spec_from_file_location(f"task{task_num}a", py_file)
        module = importlib.util.module_from_spec(spec)
        
        # Start memory tracking
        tracemalloc.start()
        
        # Run with timing
        start = time.perf_counter()
        
        try:
            # Most tasks have a run() function
            if hasattr(module.__dict__, 'run'):
                spec.loader.exec_module(module)
                module.run(
                    datasets["accounts"],
                    datasets["transactions"],
                    datasets["balances"]
                )
            else:
                # Just load the module
                spec.loader.exec_module(module)
        except Exception as e:
            print(f"    ⚠️  Task execution warning: {e}")
        
        runtime_ms = int((time.perf_counter() - start) * 1000)
        
        # Get peak memory
        _, peak = tracemalloc.get_traced_memory()
        peak_memory_bytes = peak
        
        tracemalloc.stop()
    except Exception as e:
        print(f"    ❌ Python execution error: {e}")
        runtime_ms = 0
        peak_memory_bytes = 0
        if tracemalloc.is_tracing():
            tracemalloc.stop()
    
    return {
        "filename": f"task{task_num}a.py",
        "dataset_variant": variant,
        "token_usage_input": token_input,
        "token_usage_output": token_output,
        "runtime_ms": runtime_ms,
        "peak_memory_bytes": peak_memory_bytes,
        "formatting_pass_pct": formatting_pass_pct,
        "pytest_filename": f"test_task{task_num}a.py",
        "pytest_pass_pct": pytest_pass_pct,
        "checksum": None,  # Python doesn't have checksum
        "row_count": None,
        "snapshot_pass": None,
    }


def main():
    """Main evaluation runner."""
    print("🚀 Starting evaluation of 60 tasks × 5 variants = 300 runs\n")
    
    results = []
    
    # Evaluate all SQL tasks
    print("=" * 60)
    print("SQL TASKS (30 tasks × 5 variants = 150 runs)")
    print("=" * 60)
    for task_num in range(1, 31):
        print(f"\n📝 Task {task_num}/30")
        for variant in VARIANTS:
            result = evaluate_sql_task(task_num, variant)
            results.append(result)
    
    # Evaluate all Python tasks
    print("\n" + "=" * 60)
    print("PYTHON TASKS (30 tasks × 5 variants = 150 runs)")
    print("=" * 60)
    for task_num in range(1, 31):
        print(f"\n📝 Task {task_num}/30")
        for variant in VARIANTS:
            result = evaluate_python_task(task_num, variant)
            results.append(result)
    
    # Write results to CSV
    print(f"\n💾 Writing results to {RESULTS_CSV}")
    
    fieldnames = [
        "filename",
        "dataset_variant",
        "token_usage_input",
        "token_usage_output",
        "runtime_ms",
        "peak_memory_bytes",
        "formatting_pass_pct",
        "pytest_filename",
        "pytest_pass_pct",
        "checksum",
        "row_count",
        "snapshot_pass",
    ]
    
    with open(RESULTS_CSV, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"✅ Complete! {len(results)} results written to {RESULTS_CSV}")


if __name__ == "__main__":
    main()
