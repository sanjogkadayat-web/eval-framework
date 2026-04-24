"""
python-skill/scripts/run_eval.py
Computes quantitative scores across four dimensions (25 pts each, 100 total)
and writes a scorecard with structured Critic Review placeholders.
The Critic Review is completed by the AI running this skill using the
persona at python-skill/assets/personas/python_critic_persona.md.

Usage (from repo root):
  python python-skill/scripts/run_eval.py
  python python-skill/scripts/run_eval.py --task-id PY-001
"""

import argparse, csv, json, re, statistics
from datetime import datetime
from datetime import datetime
from collections import defaultdict
from pathlib import Path

REPO_ROOT    = Path(__file__).resolve().parents[2]
TASK_BANK    = REPO_ROOT / "assets" / "task_bank.csv"
EVAL_RESULTS = REPO_ROOT / "assets" / "eval_results.csv"
OUTPUTS_BASE = REPO_ROOT / "outputs"

VARIANTS  = ["clean", "null_heavy", "duplicate_heavy", "medium", "large"]
NON_CLEAN = ["null_heavy", "duplicate_heavy", "medium", "large"]

MODEL_NAMES = {
    "a": "Claude Sonnet 4.5",
    "b": "ChatGPT 5.2 Codex",
    "c": "Gemini 2.5 Flash",
}
BASELINE = "b"

BANDS = [25.0, 22.5, 20.0, 17.5, 15.0, 12.5, 10.0, 7.5, 5.0, 2.5]

PY_RUNTIME_THRESHOLDS = [3, 4, 6, 7, 9, 11, 24, 44, 186]
PY_MEMORY_THRESHOLDS  = [5871, 6097, 6830, 330108, 351566, 454303, 490933, 1456692, 12611584]
PY_TOKEN_THRESHOLDS   = [164, 192, 210, 230, 248, 278, 327, 363, 431]

METRIC_KEY = """## Metric Key

- **Correctness /25** — `pytest_pass_pct = 100` on clean variant → 25 pts, else 0.
- **Formatting /25** — Mean `formatting_pass_pct` across 5 variants via flake8 (PEP 8), scaled 0–25.
- **Performance /25 ↑** — Mean of 3 sub-scores (runtime, memory, tokens), each banded into 10 percentile brackets: top 10% = 25, bottom 10% = 2.5. Higher is better. No baseline dependency.
- **Reliability /25** — Pass rate across 4 stress variants (null_heavy, duplicate_heavy, medium, large) × 25. Only scored if clean correctness passes. Ticks show null_heavy / duplicate_heavy / medium / large.
- **Δ Total** — vs ChatGPT 5.2 Codex. Positive = better, negative = worse.
"""


def safe_float(val, default=0.0):
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def band_score(value, thresholds):
    for i, t in enumerate(thresholds):
        if value <= t:
            return BANDS[i]
    return BANDS[-1]


def load_task_bank(task_id_filter=None):
    tasks = []
    with open(TASK_BANK, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not row["task_id"].startswith("PY-"):
                continue
            if task_id_filter and row["task_id"] != task_id_filter:
                continue
            tasks.append(row)
    return tasks


def load_eval_results():
    results = {}
    with open(EVAL_RESULTS, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not row["filename"].endswith(".py"):
                continue
            results[(row["filename"], row["dataset_variant"])] = row
    return results


def score_correctness(rbv):
    clean = rbv.get("clean")
    if not clean:
        return 0.0, False
    passes = safe_float(clean.get("pytest_pass_pct", 0)) == 100.0
    return (25.0 if passes else 0.0), passes


def score_formatting(rbv):
    vals = [safe_float(rbv[v].get("formatting_pass_pct", 0)) for v in VARIANTS if v in rbv]
    return (statistics.mean(vals) / 100.0) * 25.0 if vals else 0.0


def score_performance(rbv):
    def mean_field(field):
        vals = [
            safe_float(rbv[v].get(field))
            for v in VARIANTS
            if v in rbv and rbv[v].get(field) not in (None, "", "None")
            and safe_float(rbv[v].get(field)) > 0
        ]
        return statistics.mean(vals) if vals else 0.0

    mean_rt  = mean_field("runtime_ms")
    mean_mem = mean_field("peak_memory_bytes")
    clean    = rbv.get("clean", {})
    tokens   = safe_float(clean.get("token_usage_input", 0)) + \
               safe_float(clean.get("token_usage_output", 0))

    rt_score  = band_score(mean_rt,  PY_RUNTIME_THRESHOLDS)  if mean_rt  > 0 else 25.0
    mem_score = band_score(mean_mem, PY_MEMORY_THRESHOLDS)   if mean_mem > 0 else 25.0
    tok_score = band_score(tokens,   PY_TOKEN_THRESHOLDS)    if tokens   > 0 else 25.0

    return statistics.mean([rt_score, mem_score, tok_score]), {
        "runtime_ms":        {"mean": round(mean_rt),  "band_score": rt_score},
        "peak_memory_bytes": {"mean": round(mean_mem), "band_score": mem_score},
        "tokens":            {"total": round(tokens),  "band_score": tok_score},
    }


def score_reliability(rbv, clean_passed):
    if not clean_passed:
        return 0.0, {}
    pv = {
        v: v in rbv and safe_float(rbv[v].get("pytest_pass_pct", 0)) == 100.0
        for v in NON_CLEAN
    }
    return (sum(pv.values()) / len(NON_CLEAN)) * 25.0, pv


def run(task_id_filter=None):
    run_dir = OUTPUTS_BASE / datetime.now().strftime("%Y-%m-%d_%H-%M")
    run_dir.mkdir(parents=True, exist_ok=True)
    tasks   = load_task_bank(task_id_filter)
    metrics = load_eval_results()

    if not tasks:
        print("No Python tasks found.")
        return

    records = []
    summary = defaultdict(lambda: defaultdict(list))

    for task in tasks:
        task_id  = task["task_id"]
        prompt   = task.get("prompt", "")
        category = task.get("category", "")
        task_num = int(re.search(r"\d+", task_id).group())

        filenames  = {l: f"task{task_num}{l}.py" for l in "abc"}
        model_rows = {
            letter: {v: metrics.get((fn, v)) for v in VARIANTS if metrics.get((fn, v))}
            for letter, fn in filenames.items()
        }

        base_rbv       = model_rows.get(BASELINE, {})
        b_cor, b_clean = score_correctness(base_rbv)
        b_fmt          = score_formatting(base_rbv)
        b_perf, _      = score_performance(base_rbv)
        b_rel, _       = score_reliability(base_rbv, b_clean)
        b_total        = b_cor + b_fmt + b_perf + b_rel

        for letter in ["a", "b", "c"]:
            rbv = model_rows.get(letter, {})
            if not rbv:
                continue

            is_base           = letter == BASELINE
            cor, clean_pass   = score_correctness(rbv)
            fmt               = score_formatting(rbv)
            perf, perf_detail = score_performance(rbv)
            rel, rel_pv       = score_reliability(rbv, clean_pass)
            total             = cor + fmt + perf + rel

            delta = None if is_base else {
                "correctness": round(cor   - b_cor,   2),
                "formatting":  round(fmt   - b_fmt,   2),
                "performance": round(perf  - b_perf,  2),
                "reliability": round(rel   - b_rel,   2),
                "total":       round(total - b_total, 2),
            }

            records.append({
                "task_id":    task_id, "prompt": prompt, "category": category,
                "model":      letter,  "model_name": MODEL_NAMES[letter],
                "is_baseline": is_base,
                "scores": {
                    "correctness": round(cor,   2), "formatting":  round(fmt,   2),
                    "performance": round(perf,  2), "reliability": round(rel,   2),
                    "total":       round(total, 2),
                },
                "delta_vs_baseline":  delta,
                "correctness_detail": {"clean_gate_passed": clean_pass},
                "reliability_detail": {"per_variant": rel_pv},
                "performance_detail": perf_detail,
            })

            for dim, val in [("correctness", cor), ("formatting", fmt),
                             ("performance", perf), ("reliability", rel), ("total", total)]:
                summary[letter][dim].append(val)

    # Aggregates
    aggregates = {}
    for letter in ["a", "b", "c"]:
        s = summary[letter]
        if not s["total"]:
            continue
        aggregates[letter] = {
            "model_name": MODEL_NAMES[letter],
            "task_count": len(s["total"]),
            "mean_scores": {
                dim: round(statistics.mean(s[dim]), 2)
                for dim in ["correctness", "formatting", "performance", "reliability", "total"]
            },
        }

    # JSON
    file_tag = task_id_filter if task_id_filter else "all"
    json_out = run_dir / f"python_scorecard_{file_tag}.json"
    with open(json_out, "w", encoding="utf-8") as f:
        json.dump({"aggregates": aggregates, "records": records}, f, indent=2)
    print(f"✓ JSON  → {json_out}")

    # Markdown
    md_out = run_dir / f"python_scorecard_{file_tag}.md"
    with open(md_out, "w", encoding="utf-8") as f:
        scope = f"Task: {next((t["prompt"] for t in tasks if t["task_id"] == task_id_filter), task_id_filter)}" if task_id_filter else f"{len(tasks)} tasks"
        f.write("# Python Evaluation Scorecard\n\n")
        f.write(f"{scope} | 3 models | Baseline reference: {MODEL_NAMES[BASELINE]}\n\n")

        if not task_id_filter:
            f.write("## Summary — Mean Scores\n\n")
            f.write("| Model | Correctness /25 | Formatting /25 | Performance /25 ↑ | Reliability /25 | **Total /100** |\n")
            f.write("|---|---|---|---|---|---|\n")
            for letter in ["a", "b", "c"]:
                if letter not in aggregates:
                    continue
                ms  = aggregates[letter]["mean_scores"]
                tag = " *(baseline)*" if letter == BASELINE else ""
                f.write(f"| {MODEL_NAMES[letter]}{tag} | {ms['correctness']} | {ms['formatting']} "
                        f"| {ms['performance']} | {ms['reliability']} | **{ms['total']}** |\n")

            f.write("\n## Delta vs Baseline (ChatGPT 5.2 Codex)\n\n")
            f.write("Positive = better than baseline. Negative = worse.\n\n")
            f.write("| Model | Δ Correctness | Δ Formatting | Δ Performance | Δ Reliability | Δ Total |\n")
            f.write("|---|---|---|---|---|---|\n")
            for letter in ["a", "c"]:
                dr = [r for r in records if r["model"] == letter and r["delta_vs_baseline"]]
                if not dr:
                    continue
                f.write(f"| {MODEL_NAMES[letter]} "
                        f"| {round(statistics.mean(r['delta_vs_baseline']['correctness'] for r in dr), 2):+} "
                        f"| {round(statistics.mean(r['delta_vs_baseline']['formatting']  for r in dr), 2):+} "
                        f"| {round(statistics.mean(r['delta_vs_baseline']['performance'] for r in dr), 2):+} "
                        f"| {round(statistics.mean(r['delta_vs_baseline']['reliability'] for r in dr), 2):+} "
                        f"| {round(statistics.mean(r['delta_vs_baseline']['total']       for r in dr), 2):+} |\n")

        # Per-task
        f.write("\n## Quantitative Assessment\n\n")
        current_task = None
        for r in records:
            if r["task_id"] != current_task:
                current_task = r["task_id"]
                f.write(f"---\n\n### {r['prompt']} ({r['category']})\n\n")
                f.write("| Model | Correctness /25 | Formatting /25 | Performance /25 ↑ | Reliability /25 | Total /100 | Δ Total |\n")
                f.write("|---|---|---|---|---|---|---|\n")

            s   = r["scores"]
            d   = r["delta_vs_baseline"]
            tag = " *(baseline)*" if r["is_baseline"] else ""
            rv  = r["reliability_detail"].get("per_variant", {})
            rel_cell = f"{s['reliability']} `" + " ".join(
                "✓" if rv.get(v) else "✗" for v in NON_CLEAN
            ) + "`" if rv else str(s["reliability"])

            f.write(f"| {r['model_name']}{tag} "
                    f"| {s['correctness']} | {s['formatting']} "
                    f"| {s['performance']} | {rel_cell} "
                    f"| {s['total']} "
                    f"| " + (f"{d['total']:+}" if d else "—") + " |\n")

        # Critic review section — grouped by section, one bullet per model
        # The AI running this skill fills these in using the persona at:
        # python-skill/assets/personas/python_critic_persona.md
        f.write("\n---\n\n")
        f.write("## Critic Review\n\n")

        seen_tasks = []
        for r in records:
            if r["task_id"] in seen_tasks:
                continue
            seen_tasks.append(r["task_id"])
            tid    = r["task_id"]
            num    = str(int(re.search(r"\d+", tid).group()))
            prompt = r["prompt"]
            f.write(f"### {prompt}\n\n")
            for section in ["Strengths", "Failures", "Mitigation Strategies", "Observations"]:
                f.write(f"**{section}**\n")
                for letter, name in [("a", "Claude Sonnet 4.5"), ("b", "ChatGPT 5.2 Codex"), ("c", "Gemini 2.5 Flash")]:
                    f.write(f"- **{name}:** <!-- CRITIC:{tid}:{letter}:{section.replace(' ','_')} -->\n")
                f.write("\n")

        # Metric key — at the bottom
        f.write("---\n\n")
        f.write(METRIC_KEY)

        # Raw Metrics Table
        f.write("\n---\n\n## Raw Metrics\n\n")
        f.write("| Model | Task | Runtime (ms) | Peak Memory (bytes) | Input Tokens | Output Tokens |\n")
        f.write("|:------|:-----|-------------:|--------------------:|-------------:|--------------:|\n")
        for r in records:
            pd = r["performance_detail"]
            clean = metrics.get((f"task{int(re.search(r'\\d+', r['task_id']).group())}{r['model']}.py", "clean"), {})
            f.write(f"| {r['model_name']} | {r['task_id']} "
                    f"| {pd['runtime_ms']['mean']} "
                    f"| {pd['peak_memory_bytes']['mean']} "
                    f"| {round(safe_float(clean.get('token_usage_input', 0)))} "
                    f"| {round(safe_float(clean.get('token_usage_output', 0)))} |\n")

    print(f"✓ MD    → {md_out}")
    print(f"\n{'='*50}")
    print("  PYTHON SCORECARD")
    print(f"{'='*50}")
    for letter in ["a", "b", "c"]:
        if letter in aggregates:
            tag = " (baseline)" if letter == BASELINE else ""
            print(f"  {MODEL_NAMES[letter]}{tag}: {aggregates[letter]['mean_scores']['total']} / 100")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Python evaluation scorecard")
    parser.add_argument("--task-id", default=None, help="Score a single task, e.g. PY-001")
    args = parser.parse_args()
    run(task_id_filter=args.task_id)
