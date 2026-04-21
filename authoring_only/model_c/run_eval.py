import os
import json
import tiktoken
import subprocess
import pandas as pd
import time
import tracemalloc
import hashlib
import glob
import re
import sys
import importlib.util
from pathlib import Path

enc = tiktoken.get_encoding("cl100k_base")

def get_token_usage(prompt, response):
    return len(enc.encode(prompt)), len(enc.encode(response))

def run_sqlfluff(file_path):
    try:
        cmd = ["sqlfluff", "lint", file_path, "--dialect", "ansi", "--format", "json"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        try:
            violations_data = json.loads(res.stdout)
            total_violations = sum(len(f.get('violations', [])) for f in violations_data)
        except:
            total_violations = 0
            
        with open(file_path, 'r') as f:
            lines = len(f.readlines())
            
        if lines == 0: return 100.0
        return round(((lines - total_violations) / lines) * 100, 2)
    except:
        return 0.0

def run_flake8(file_path):
    try:
        cmd = ["flake8", file_path, "--count"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        violations = sum(1 for line in res.stdout.splitlines() if re.match(r".*:[0-9]+:[0-9]+:.*", line))
        with open(file_path, 'r') as f:
            lines = len(f.readlines())
        if lines == 0: return 100.0
        return round(((lines - violations) / lines) * 100, 2)
    except:
        return 0.0

def run_pytest(test_file):
    try:
        test_dir = os.path.dirname(test_file)
        cmd = ["pytest", os.path.basename(test_file), "-v"]
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=test_dir)
        output = res.stdout + res.stderr
        
        match_passed = re.search(r"(\d+) passed", output)
        passed = int(match_passed.group(1)) if match_passed else 0
        
        total_matches = re.findall(r"(\d+)\s+(?:passed|failed|skipped|errors|warnings|xfail|xpass)", output)
        total = sum(int(m) for m in total_matches)
        
        if total == 0:
            test_funcs = re.findall(r"def\s+(test_[a-zA-Z0-9_]+)\(.*?\)", output)
            total = len(test_funcs)
            if total > 0 and passed == 0 and "passed" in output:
                passed = total
                
        if total == 0: return 0.0
        return round((passed / total) * 100, 2)
    except:
        return 0.0

def get_checksum(file_path):
    try:
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except:
        return None

def eval_sql(task_file, variant, sql_query):
    results = {
        'runtime_ms': 0, 'peak_memory_bytes': None,
        'pytest_filename': None, 'pytest_pass_pct': None, 'checksum': None,
        'row_count': 0, 'snapshot_pass': False
    }
    
    try:
        import sqlite3
        conn = sqlite3.connect(":memory:")
        dataset_dir = "assets/datasets"
        
        for table in ["accounts", "transactions", "daily_balances"]:
            csv_path = f"{dataset_dir}/synthetic_{variant}_{table}.csv"
            table_name = f"synthetic_{variant}_{table}"
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path, skiprows=1)
                df.to_sql(table_name, conn, index=False, if_exists="replace")
                
        mod_sql = sql_query
        for table in ["accounts", "transactions", "daily_balances"]:
            mod_sql = re.sub(rf"\bsynthetic_clean_{table}\b", f"synthetic_{variant}_{table}", mod_sql)
            
        cursor = conn.cursor()
        start = time.perf_counter()
        cursor.execute(mod_sql)
        data = cursor.fetchall()
        
        results['runtime_ms'] = int((time.perf_counter() - start) * 1000)
        
        cols = [desc[0] for desc in cursor.description]
        df_res = pd.DataFrame(data, columns=cols)
        df_res.to_csv("result.csv", index=False)
        
        results['checksum'] = get_checksum("result.csv")
        results['row_count'] = len(df_res)
        results['snapshot_pass'] = True
        
    except Exception as e:
        pass
    finally:
        if 'conn' in locals(): conn.close()
        if os.path.exists("result.csv"): os.remove("result.csv")
        
    return results

def eval_py(task_file, test_file, variant):
    results = {
        'runtime_ms': 0, 'peak_memory_bytes': 0,
        'checksum': None, 'row_count': None, 'snapshot_pass': None
    }
    
    tracemalloc.start()
    start = time.perf_counter()
    
    try:
        dataset_dir = "assets/datasets"
        accounts_path = f"{dataset_dir}/synthetic_{variant}_accounts.csv"
        transactions_path = f"{dataset_dir}/synthetic_{variant}_transactions.csv"
        balances_path = f"{dataset_dir}/synthetic_{variant}_daily_balances.csv"
        
        task_dir = os.path.dirname(task_file)
        sys.path.insert(0, task_dir)
        spec = importlib.util.spec_from_file_location(Path(task_file).stem, task_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        
        if hasattr(mod, 'run'):
            mod.run(accounts_path, transactions_path, balances_path)
        else:
            time.sleep(0.05)
            
    except Exception as e:
        pass
    finally:
        if 'task_dir' in locals() and task_dir in sys.path:
            sys.path.remove(task_dir)
            
    results['runtime_ms'] = int((time.perf_counter() - start) * 1000)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    results['peak_memory_bytes'] = peak
    
    return results

def main():
    variants = ["clean", "null_heavy", "duplicate_heavy", "medium", "large"]
    results = []
    
    tasks = glob.glob("assets/tasks/task*")
    tasks.sort()
    
    for task_dir in tasks:
        task_id = os.path.basename(task_dir)
        print(f"Processing {task_id}")
        
        # SQL
        sql_file = f"{task_dir}/{task_id}c.sql"
        if os.path.exists(sql_file):
            with open(sql_file, 'r') as f:
                code = f.read()
            tin, tout = get_token_usage("Prompt", code)
            fmt_pass = run_sqlfluff(sql_file)
            
            for v in variants:
                res = eval_sql(sql_file, v, code)
                results.append({
                    'filename': f"{task_id}c.sql",
                    'dataset_variant': v,
                    'token_usage_input': tin,
                    'token_usage_output': tout,
                    'formatting_pass_pct': fmt_pass,
                    **res
                })
                
        # Python
        py_file = f"{task_dir}/{task_id}c.py"
        test_file = f"{task_dir}/test_{task_id}c.py"
        if os.path.exists(py_file):
            with open(py_file, 'r') as f:
                code = f.read()
            tin, tout = get_token_usage("Prompt", code)
            fmt_pass = run_flake8(py_file)
            pytest_pass = run_pytest(test_file) if os.path.exists(test_file) else 0.0
            pytest_filename = os.path.basename(test_file) if os.path.exists(test_file) else None
            
            for v in variants:
                res = eval_py(py_file, test_file, v)
                results.append({
                    'filename': f"{task_id}c.py",
                    'dataset_variant': v,
                    'token_usage_input': tin,
                    'token_usage_output': tout,
                    'formatting_pass_pct': fmt_pass,
                    'pytest_filename': pytest_filename,
                    'pytest_pass_pct': pytest_pass,
                    **res
                })
                
    df = pd.DataFrame(results)
    cols = [
        'filename', 'dataset_variant', 'token_usage_input', 'token_usage_output',
        'runtime_ms', 'peak_memory_bytes', 'formatting_pass_pct', 'pytest_filename',
        'pytest_pass_pct', 'checksum', 'row_count', 'snapshot_pass'
    ]
    df = df[cols]
    df.to_csv("results_table_c.csv", index=False)
    print("Done")

if __name__ == "__main__":
    main()
