## eval_framework

Utilities for generating a per-model results table over a fixed task bank and 5 synthetic dataset variants.

### Setup

Install dependencies.

```bash
pip install -r requirements.txt
```

### Assets

- **Datasets**: `assets/datasets/`
  - Existing flat-variant filenames are supported: `synthetic_{variant}_{table}.csv`
  - The bootstrap step also creates `assets/datasets/{variant}/synthetic_{table}.csv` (optional convenience).
- **Tasks (model b)**: required layout is created under `assets/tasks/{task_id}/`:
  - SQL: `assets/tasks/SQL-0xx/task{N}b.sql`
  - Python: `assets/tasks/PY-0xx/task{N}b.py`
  - Tests: `assets/tasks/PY-0xx/test_task{N}b.py`
  - Prompts: `assets/tasks/*/prompt.txt` sourced from `assets/task_prompts_b.yaml`

### Generate `results_table_b.csv`

Run:

```bash
python run_scorecard.py
```

Output: `results_table_b.csv` at repo root.

SQL `snapshot_pass` is computed by comparing model-b output to a reference snapshot.
Reference snapshots are auto-generated (once) under `assets/tasks/SQL-*/reference_results/{variant}.csv`
from the existing model-c SQL files.

Optional:

```bash
python run_scorecard.py --out outputs/results_table_b.csv --variants clean,medium,large
```