# Implementation Plan: Feature 5 — Comparative Scorecard

**Branch**: `005-comparative-scorecard` | **Date**: 2026-04-08 | **Last Updated**: 2026-04-18 | **Spec**: `specs/005-comparative-scorecard/spec.md`
**Input**: Feature specification from `/specs/005-comparative-scorecard/spec.md`

> **Amendment A3 — April 2026 (ratified 2026-04-18):** The pre-recorded data layer consumed by Features 1–4 has been consolidated into a two-table design: `assets/task_bank.csv` (master index, prompts inline, per-model filenames) and `assets/eval_results.csv` (unified metrics, up to 3,000 rows). Feature 5 is largely insulated from this change because `collector.py` reads `result.json` artifacts from `outputs/` — not the pre-recorded data directly. The F5-facing effects are narrow: (1) `result.json` now carries `formatting_violations` (replacing `flake8_violation_count` and `sqlfluff_violation_count`), `pytest_pass` (Python) or `checksum` + `row_count` + `snapshot_pass` (SQL) as correctness primitives, and no `generation_time_ms` field; (2) `collector.py` continues to cross-validate contracted task IDs against `assets/task_bank.csv`, which remains the single source of truth for the `contracted` flag. See Constitution Amendment A3 for full rationale.

> **Amendment A1 — April 2026 (ratified 2026-04-09):** Full scorecard ceiling raised from 600 to 3,000 scored comparisons. `--contracted-only` CLI flag added to produce the client-facing 40-task scorecard. `contracted` flag propagated from upstream `result.json` artifacts into scorecard output. `collector.py` cross-validates contracted task IDs against `assets/task_bank.csv`. These changes remain in effect under A3.

> **Amendment A2 — April 2026 (ratified 2026-04-13):** `generation_time_ms` removed from all schemas and output artifacts including the unified scorecard JSON and the markdown scorecard.

---

## Summary

Feature 5 implements the comparative scorecard pipeline — the final aggregation layer that consumes all quantitative and qualitative artifacts produced by the SQL skill (Features 1–2) and the Python skill (Features 3–4) and emits two outputs:

1. **Unified JSON** — a single machine-readable file covering all models × tasks × variants across both SQL and Python. One record per model × task × variant, containing: correctness score, formatting score (from the `formatting_violations` field propagated via upstream `result.json`), performance metrics (runtime, peak memory, token usage), variant pass/fail status, `variant_mismatch` flag (derived at harness runtime by `schema_checker.py` and surfaced in `result.json`), and `contracted` flag (resolved from `task_bank.csv`). All metric fields are fully populated — both SQL and Python skills pre-record all metrics in the unified `assets/eval_results.csv` table under the A3 two-table architecture, and Features 1 and 3 propagate those values into the `result.json` artifacts that F5 reads. Each record includes a reference path to its corresponding Critic review `.md`.

2. **Markdown Scorecard** — a human-readable report that surfaces per-model aggregates (correctness pass rate, mean formatting violations, mean runtime, mean peak memory, mean token usage), pass rates across dataset variants, performance delta vs. the ChatGPT 5.2 Codex baseline (filename letter `c`), failure category breakdowns (correctness failure, variant mismatch, edge-case failure), condensed Critic review summaries per model, and suggested mitigations. Critic summaries and mitigations are extracted by **deterministic text parsing** of the known four-section Critic `.md` structure (strengths, failures, mitigation strategies, observations) — no LLM summarization is used.

The pipeline reads `result.json` and `critic_review.md` artifacts from the `outputs/` directory — it never re-runs evaluation logic or reads pre-recorded asset data directly. It operates on whatever artifacts exist: if only Python features have run, the scorecard covers Python only; if both SQL and Python artifacts are present, the scorecard covers both. Model identifiers — kept anonymized throughout Features 1–4 via the filename-letter convention (`a`/`b`/`c`) and `model_token` in `outputs/` paths — are **re-associated** with real model names at scorecard generation time, after all numeric scoring is complete.

All aggregation is deterministic and script-enforced; no LLM judgment is used in numeric scoring, ranking, or Critic summary extraction. Scoring weights and acceptance thresholds are deferred to post-V1 [TBD] per Constitution — the scorecard reports raw scores and deltas without applying pass/fail thresholds.

**Contracted vs. full scorecard**: When `--contracted-only` is passed, the scorecard covers only the 40 contracted tasks (SQL-001–SQL-020 + PY-001–PY-020) and is the version delivered to the Banking Institution — labelled clearly as the client deliverable. When omitted, the full 200-task scorecard is produced as a value-add. Both modes use identical aggregation logic; the filter operates on the `contracted` field in each `result.json` artifact (which itself is sourced from `task_bank.csv` during upstream feature execution). `collector.py` cross-validates contracted task IDs against `assets/task_bank.csv` before emitting the scorecard.

---

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: `csv` / `json` (flat-file I/O — stdlib); `pathlib` (directory traversal — stdlib); `statistics` (mean aggregation — stdlib). No third-party packages required.
**Storage**: Flat files only — reads `.json` and `.md` from the shared `outputs/` directory at zip root (both skills write here); writes unified scorecard `.json` and scorecard `.md` to the path specified by `--outdir`. Also reads `assets/task_bank.csv` for contracted-flag cross-validation. No database.
**Testing**: pytest — unit tests for aggregation logic, JSON schema validation, markdown rendering, delta computation, contracted flag filtering, and CLI flag handling; integration test for end-to-end scorecard generation from fixture artifacts covering both full and contracted-only modes.
**Target Platform**: Local development, Linux/macOS — no cloud, no Docker, no containerization
**Project Type**: CLI command — `scorecard` script lives at **zip root** (shared level, not inside either skill) since it spans both `sql-skill/` and `python-skill/` output. Invoked via `scorecard --outdir <path>` with optional filter flags: `--engine` (sql | python | all), `--dataset-variant`, `--model`, `--contracted-only` — per FR-013.
**Performance Goals**: No latency SLA in V1. Scorecard generation is a single-pass aggregation over flat files — expected to complete in seconds for the full ceiling of 3,000 `result.json` artifacts.
**Constraints**: No API calls; no database; no GPU dependencies; no LLM invocation of any kind; no code execution; flat-file storage only; all aggregation and ranking logic deterministic and script-enforced; scoring weights and acceptance thresholds deferred to post-V1 [TBD] per Constitution.

**Scale/Scope**:
- Full build ceiling: Up to 3,000 `result.json` artifacts (200 tasks × 3 models × 5 variants) plus up to 600 `critic_review.md` files (200 tasks × 3 models — one per task × model, not per variant).
- Client-contracted ceiling (`--contracted-only`): 300 `result.json` artifacts (40 tasks × 3 models × 5 variants) plus up to 120 `critic_review.md` files.
- Outputs one unified `.json` and one scorecard `.md` per invocation. When filter flags are applied, outputs cover only the matching subset.

---

## Constitution Check

*GATE: All items must pass (or have an approved amendment in progress) before implementation begins. Re-check after technical design is finalized.*

| # | Rule | Source | Status | Notes |
|---|---|---|---|---|
| 1 | Python 3.11+ only | Tech Stack | ✅ Pass | All dependencies are stdlib — no third-party packages |
| 2 | No web/API framework | Explicit Prohibitions | ✅ Pass | No FastAPI/Flask; CLI-only |
| 3 | Flat files only — no database | Explicit Prohibitions | ✅ Pass | Reads `.json`/`.md` from `outputs/` and `task_bank.csv` from `assets/`; writes `.json`/`.md` to `--outdir` |
| 4 | No Docker / cloud / containerization | Explicit Prohibitions | ✅ Pass | Local execution only |
| 5 | Model identifiers re-associated only after all scoring complete | Principle 2 / Security | ✅ Pass | Anonymization in Features 1–4 is structural (filename letter `a`/`b`/`c` at the asset layer) — scoring scripts never see real model names in code content. Filesystem paths in `outputs/` contain `model_token` (derived from the filename letter at load time) — this is by design (artifact keying). Feature 5 runs after all numeric scoring is complete; re-association with real model names at this stage is compliant. |
| 6 | All scoring/ranking logic deterministic — no LLM judgment | Principle 2 | ✅ Pass | Aggregation, delta computation, contracted-flag filtering, and Critic summary extraction are all script-enforced. No LLM invocation of any kind in Feature 5 |
| 7 | Synthetic data only, labeled in filename and header | Security / FR-016 | ✅ Pass | No new datasets introduced — reads artifacts produced from upstream synthetic data |
| 8 | No PII, no real financial identifiers | Security | ✅ Pass | No new data introduced; scorecard contains aggregated metrics and parsed Critic text only |
| 9 | Artifact key format `task_id/model/category` | FR-011 (amended) | ✅ Pass | Reads existing artifact keys; scorecard output written to `--outdir`, outside the artifact tree |
| 10 | No GPU dependencies | Explicit Prohibitions | ✅ Pass | stdlib only |
| 11 | No `when_to_use` field in `SKILL.md` | Tech Stack | ✅ Pass | Scorecard script lives at zip root — not inside a `SKILL.md`. Rule noted for awareness |
| 12 | Critic persona not invoked in this feature | Principle 2 / FR-008/009 | ✅ Pass | Feature 5 parses existing Critic `.md` files via deterministic text extraction — it does not invoke either Critic persona |
| 13 | Scorecard reports raw scores — no pass/fail thresholds | Constitution [TBD] | ✅ Pass | Scoring weights and thresholds deferred to post-V1. Scorecard emits raw values and deltas only — no model is declared a "winner" and no pass/fail judgment is applied. This is intentional, not a gap. |
| 14 | CLI flags per FR-013 | FR-013 | ✅ Pass | `scorecard` supports `--outdir`, `--engine`, `--dataset-variant`, `--model`, `--contracted-only` |
| 15 | Client referred to as "Banking Institution" only | Security / Client Identity | ✅ Pass | No client name in any script, output template, or generated report |
| 16 | Float comparisons use epsilon from `references/deterministic-rules.md` | Deterministic Rules / FR-014 | ✅ Pass | Any mean or delta computation on runtime or memory values must read epsilon tolerance from `references/deterministic-rules.md` — never hardcoded in scripts |
| 17 | No code execution at runtime | Principle 6 / Explicit Prohibitions | ✅ Pass | Feature 5 reads scored artifacts only — no code execution, no tool invocation |
| 18 | All metric fields fully populated from both skills | FR-006 / FR-010 | ✅ Pass | Both SQL (Feature 1) and Python (Feature 3) pre-record all metrics in the unified `eval_results.csv` and propagate them into `result.json`. No nullable metric fields in the unified JSON beyond the per-language pattern (e.g., `peak_memory_bytes` is null in SQL records; `checksum` is null in Python records) |
| 19 | Full scorecard ceiling raised to 3,000 (A1) | Amendment A1 | ✅ Pass | Full ceiling raised from 600 to 3,000 (200 tasks × 3 models × 5 variants). Contracted ceiling 300 (40 tasks × 3 models × 5 variants) unchanged. A1 ratified. |
| 20 | `contracted` flag propagation and `--contracted-only` filter (A1) | Amendment A1 | ✅ Pass | `contracted` field from upstream `result.json` (sourced from `task_bank.csv`) read by `collector.py` for `--contracted-only` filtering and surfaced in the unified scorecard JSON. `collector.py` cross-validates contracted task IDs against `assets/task_bank.csv` before emitting scorecard. A1 ratified. |
| 21 | Two-table unified architecture (A3) | Amendment A3 | ✅ Pass | Upstream `result.json` now carries field names consistent with `eval_results.csv` (`formatting_violations`, `pytest_pass`, `checksum`, `row_count`, `snapshot_pass`). No `flake8_violation_count` / `sqlfluff_violation_count` / `correctness_pass` / `correctness_detail` / `generation_time_ms` fields. A3 ratified. |


**All 21 items pass. Constitution Check gate is clear for A3-aligned implementation.**

---

## Project Structure

### Documentation (this feature)

```text
specs/005-comparative-scorecard/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

Feature 5 lives at **zip root** — it spans both skills and belongs to neither.

```text
eval-framework.zip
├── README.md
├── requirements.txt
├── run_scorecard.py                   # CLI entry point: scorecard --outdir <path>
│                                      # Flags: --engine, --dataset-variant, --model,
│                                      # --contracted-only
│                                      # Named run_scorecard.py to avoid import collision
│                                      # with scorecard/ package
├── scorecard/
│   ├── __init__.py
│   ├── collector.py                   # Walks outputs/ directory; reads result.json per
│   │                                  # task_id/model/category; applies --engine, --model,
│   │                                  # --dataset-variant, and --contracted-only filters;
│   │                                  # cross-validates contracted task IDs against
│   │                                  # assets/task_bank.csv before emitting records;
│   │                                  # returns list of run records
│   ├── critic_parser.py               # Parses critic_review.md four-section structure
│   │                                  # (strengths, failures, mitigation strategies,
│   │                                  # observations); returns structured dict per review
│   ├── aggregator.py                  # Computes per-model aggregates: correctness pass rate,
│   │                                  # mean formatting_violations, mean runtime_ms, mean
│   │                                  # peak_memory_bytes, mean token_usage_input +
│   │                                  # token_usage_output; variant pass rates; failure
│   │                                  # category counts. Operates on contracted or full task
│   │                                  # set depending on collector output.
│   ├── baseline_delta.py              # Computes performance delta vs. ChatGPT 5.2 Codex
│   │                                  # (filename letter c) baseline for each metric per
│   │                                  # model; reads epsilon from
│   │                                  # references/deterministic-rules.md
│   ├── json_emitter.py                # Writes unified scorecard .json — one record per
│   │                                  # model × task × variant with all metrics + critic
│   │                                  # path + contracted flag
│   └── markdown_emitter.py            # Renders human-readable scorecard .md — section order
│                                      # defined in data-model.md (Phase 1). Contracted-only
│                                      # report labelled clearly as client deliverable.
│                                      # Report title reflects any applied filter flags.
├── references/
│   ├── methodology.md
│   ├── rubric.md
│   ├── file-schema.md
│   └── deterministic-rules.md
├── assets/
│   ├── task_bank.csv                  # Master index used by collector.py to
│   │                                  # cross-validate contracted task IDs present
│   │                                  # in the artifact set
│   └── eval_results.csv               # Unified pre-recorded metrics — not read directly
│                                      # by Feature 5. F5 consumes result.json artifacts
│                                      # from outputs/ which carry the same metric values
│                                      # surfaced per model × task × variant by F1 and F3.
├── sql-skill/
│   └── ...
├── python-skill/
│   └── ...
├── outputs/                           # Runtime — not bundled in zip
│   └── [task_id]/
│       └── [model]/
│           └── [category]/
│               ├── result.json        # Contains contracted flag (from task_bank.csv),
│               │                      # formatting_violations, pytest_pass (Python) or
│               │                      # checksum/row_count/snapshot_pass (SQL),
│               │                      # runtime_ms, peak_memory_bytes (Python),
│               │                      # token_usage_input, token_usage_output,
│               │                      # variant_mismatch (runtime-derived by
│               │                      # schema_checker.py).
│               │                      # No generation_time_ms, no flake8_violation_count,
│               │                      # no sqlfluff_violation_count (removed under A2/A3).
│               └── critic_review.md
└── tests/
    ├── unit/
    │   ├── test_collector.py          # Covers --contracted-only filter logic and
    │   │                              # task_bank.csv cross-validation
    │   ├── test_critic_parser.py
    │   ├── test_aggregator.py
    │   ├── test_baseline_delta.py
    │   ├── test_json_emitter.py
    │   └── test_markdown_emitter.py
    ├── integration/
    │   └── test_scorecard_pipeline.py # End-to-end: fixture artifacts → scorecard outputs.
    │                                  # Covers both full and contracted-only modes.
    └── fixtures/
        ├── sample_result.json         # Includes contracted flag, formatting_violations,
        │                              # pytest_pass or checksum/row_count/snapshot_pass
        └── sample_critic_review.md
```

**Scorecard output** (written to `--outdir` at runtime):

```text
<outdir>/
├── scorecard.json      # Unified machine-readable output. contracted flag on every record.
└── scorecard.md        # Human-readable report. Contracted-only runs clearly labelled.
```

**Structure Decision**: Feature 5 lives at zip root as a standalone `scorecard/` package with a `run_scorecard.py` CLI entry point (named to avoid Python import collision with the package). It does not belong inside either skill because it aggregates across both. The `--contracted-only` flag is handled entirely in `collector.py` by filtering on the `contracted` field in each `result.json` — no separate code path, no duplicated logic. Upstream Features 1 and 3 source the `contracted` value from `assets/task_bank.csv` (the single source of truth under A3) and propagate it into `result.json`. `collector.py` additionally reads `assets/task_bank.csv` directly as a secondary lookup to cross-validate that all expected contracted task IDs are present in the artifact set before emitting the scorecard. `json_emitter.py` passes the `contracted` flag through to the unified JSON so downstream consumers can apply their own filtering. `markdown_emitter.py` labels contracted-only reports clearly as the client deliverable. Tests cover both full and contracted-only modes via fixture artifacts. `outputs/` is the shared runtime directory not bundled in the zip. All metric fields are fully populated from both upstream skills under the A3 unified architecture — no nullable fields in the unified JSON beyond the per-language pattern inherited from `eval_results.csv` (Python-only fields null for SQL records and vice versa). Field names in `result.json` and the unified JSON follow the A3 canonical names: `formatting_violations`, `pytest_pass`, `checksum`, `row_count`, `snapshot_pass` — legacy names (`flake8_violation_count`, `sqlfluff_violation_count`, `correctness_pass`, `correctness_detail`, `generation_time_ms`) are not present.

---

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| `--contracted-only` flag | Client contract is for 40 tasks. The team builds 200. Both scorecards must be producible from the same pipeline without separate code paths or manual task list maintenance. | Hardcoding the contracted task list in the scorecard script would require manual updates whenever the contracted set changes and creates a maintenance risk and a potential source of error. |
| Full ceiling raised to 3,000 comparisons | Follows directly from the 200-task build scope under Amendment A1. No architectural change required — purely a scale increase on the same aggregation logic. | N/A — this is not a complexity addition; it is a ceiling number update reflecting the Amendment A1 scope change. |
