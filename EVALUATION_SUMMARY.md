# Evaluation Framework Summary

## Overview
Comprehensive evaluation system for 60 coding tasks (30 SQL + 30 Python) across 5 dataset variants, generating 300 total evaluation runs.

## Results Generated
- **File**: `results_table_a.csv`
- **Total Runs**: 300 (150 SQL + 150 Python)
- **Columns**: 12 metrics per run

## Metrics Collected

### For All Tasks
- `filename`: Task file name
- `dataset_variant`: One of {clean, null_heavy, duplicate_heavy, medium, large}
- `token_usage_input`: Input tokens (task prompt)
- `token_usage_output`: Output tokens (solution code)
- `runtime_ms`: Execution time in milliseconds
- `formatting_pass_pct`: Linting score percentage

### SQL-Specific
- `checksum`: SHA256 hash of result CSV
- `row_count`: Number of rows returned
- `snapshot_pass`: Whether result matches reference (currently False)

### Python-Specific
- `peak_memory_bytes`: Peak memory usage
- `pytest_filename`: Associated test file
- `pytest_pass_pct`: Percentage of tests passed

## Success Rates
- **SQL Tasks**: 88/150 runs successful (58.7%)
  - Average runtime: 7.2 ms
  - Average formatting: 100.0%

- **Python Tasks**: 2/150 runs successful (1.3%)
  - Average runtime: 196.0 ms (successful runs)
  - Average memory: 3.4 MB
  - Average formatting: 61.3%

## Token Usage Statistics
- SQL tasks: ~19 input tokens, ~183 output tokens
- Python tasks: ~19 input tokens, ~262 output tokens

## Known Issues

### SQL Tasks
Some tasks fail due to:
1. **Table naming**: Tasks reference `synthetic_clean_daily_balances` but should use just `synthetic_clean_balances`
2. **Date type casting**: DuckDB requires explicit casting of VARCHAR to DATE for date functions
3. **SQL dialect differences**: Some ANSI SQL constructs need adaptation for DuckDB

### Python Tasks
1. **Runtime measurement**: Only first variant (clean) executes successfully for most tasks
2. **Pytest integration**: Test pass percentages showing 0.0%, requires pytest invocation fix
3. **Module loading**: Some tasks fail to load dynamically

## Files Generated
- `evaluate_tasks.py`: Main evaluation runner
- `task_prompts.py`: Task prompt definitions for token counting
- `results_table_a.csv`: Complete results table
- `evaluation_run.log`: Detailed execution log

## Usage
```bash
python3 evaluate_tasks.py
```

The script will:
1. Load all 60 task files
2. Run each against 5 dataset variants
3. Collect all metrics
4. Write results to CSV

## Future Improvements
1. Fix SQL table name references in task files
2. Add date type casting in DuckDB loader
3. Improve pytest integration for accurate test pass rates
4. Add reference CSV snapshots for snapshot_pass validation
5. Optimize Python task execution for non-clean variants
