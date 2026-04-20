# Implementation Plan: Feature 4 — Python Qualitative Evaluation

**Branch**: `004-python-qual-eval` | **Date**: 2026-04-08 | **Last Updated**: 2026-04-18 | **Spec**: `specs/004-python-qual-eval/spec.md`
**Input**: Feature specification from `/specs/004-python-qual-eval/spec.md`

> **Amendment A3 — April 2026 (ratified 2026-04-18):** Per-task `answers.csv` and `variant_results.csv` references throughout this plan are replaced with the two-table architecture (`assets/task_bank.csv` for master index and prompts inline, `assets/eval_results.csv` for unified metrics). The formatting violation count is read from the `formatting_violations` field in `eval_results.csv` (not a per-task file). Critic input is the anonymized `.py` code file at `assets/tasks/[task_id]/task{N}{a|b|c}.py`.

---

## Summary

Feature 4 implements the Python Critic persona review within the `python-skill/` Agent Skill. It is triggered automatically at the end of every `eval-task --engine python` invocation and is also invocable as a standalone CLI command (`eval-qualitative --engine python`) for cases where the Critic review needs to be run independently from Feature 3. The `eval-qualitative` entry point is supplementary — FR-013 defines `eval-task` and `scorecard` as the minimal required CLI commands.

Feature 4 adds one output per attempt to the existing Feature 3 results:

- **Critic Review** — the Python Critic persona is automatically invoked on the anonymized model Python code file after every eval run. All three models submit anonymized code — identity is encoded as the filename letter (`a`/`b`/`c`) at the asset layer from ingestion onward, making the anonymized filename the working identifier throughout. The Critic returns structured commentary in four sections: **strengths** (what the code does well), **failures** (concrete problems or anti-patterns), **mitigation strategies** (suggested fixes for identified failures), and **observations** (neutral notes on style, structure, or approach). The Critic produces no numeric score and must not contain any model identifier in its output. Because model identity is never exposed to the Critic — only the anonymized filename is — identifier leakage in Critic output is not a production risk; no retry logic is applied. Output is stored as `.md` keyed by `task_id/model/category`.

The flake8 formatting score is pre-recorded as the `formatting_violations` field in `assets/eval_results.csv` and written to `result.json` by Feature 3 during the quantitative pipeline. Feature 4 does not invoke flake8 — it focuses exclusively on the Critic persona review, which is the only LLM-generated content produced at harness runtime.

---

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: No third-party packages required for Feature 4; Critic persona is invoked within the Claude Agent Skill execution context — no external API dependency
**Storage**: Flat files only — `.md` for Critic output. No database.
**Testing**: pytest — harness self-tests only. Verify Critic output contains all four sections (strengths, failures, mitigation strategies, observations); verify no numeric score in Critic output. Critic invocation is mocked at unit test level — LLM calls are not tested directly.
**Target Platform**: Local development, Linux/macOS — no cloud, no Docker, no containerization
**Project Type**: CLI skill — invoked automatically via `eval-task --engine python` and independently via `eval-qualitative --engine python` (supplementary to FR-013 minimal CLI requirements)
**Performance Goals**: No latency SLA in V1. Critic response time is determined by Claude's execution context — not measured or reported.
**Constraints**:
- No numeric scoring by Critic
- No model identifiers in Critic input or output
- Flat-file storage only
- Critic output structure enforced via persona template in `assets/personas/`
- No code execution at runtime — Critic review is the only LLM-generated content (Principle 6)
- No GPU dependencies

**Scale/Scope**: Up to 20–40 tasks × 3 models = **up to 120 Critic reviews** — one per attempt, not per variant. Critic reviews code quality, not dataset behaviour, so variant comparisons do not produce new Critic reviews.

---

## Constitution Check

*GATE: All items must pass (or have an approved amendment in progress) before implementation begins. Re-check after technical design is finalized.*

| # | Rule | Source | Status | Notes |
|---|---|---|---|---|
| 1 | Python 3.11+ only | Tech Stack | ✅ Pass | No third-party packages in Feature 4 |
| 2 | No web/API framework | Explicit Prohibitions | ✅ Pass | Critic invoked within Claude Agent Skill context — no FastAPI/Flask, no external HTTP calls |
| 3 | Flat files only — no database | Explicit Prohibitions | ✅ Pass | `.md` for Critic output |
| 4 | No Docker / cloud / containerization | Explicit Prohibitions | ✅ Pass | Local execution only |
| 5 | Model anonymization before Critic | Principle 2 / Security | ✅ Pass | Anonymization is structural — model identity is encoded as the filename letter (`a`/`b`/`c`) at the asset layer. Critic input is the anonymized `.py` file; no real model names are ever exposed. Consistent with Feature 1 → Feature 2 pattern for SQL. |
| 6 | Critic produces no numeric score | Principle 2 / FR-009 | ✅ Pass | Enforced via Critic persona template in `assets/personas/`; four output sections are qualitative only |
| 7 | No model identifiers in Critic input or output | Principle 2 / Security | ✅ Pass | Identifier stripping enforced structurally at the asset layer. Critic persona template is authored manually and contains no model identifiers by construction. **Must be verified for absence of model identifiers once `python_critic_persona.md` is manually authored.** |
| 8 | No code execution at runtime | Principle 6 / Explicit Prohibitions | ✅ Pass | No flake8 invocation — `formatting_violations` is pre-recorded in `eval_results.csv` and written to `result.json` by Feature 3. Only LLM Critic invocation occurs at runtime |
| 9 | All numeric scoring deterministic — no LLM judgment in numeric results | Principle 2 | ✅ Pass | Critic produces no numeric score; `formatting_violations` is pre-recorded |
| 10 | Synthetic data only, labeled in filename and header | Security / FR-016 | ✅ Pass | Datasets inherited from Feature 3 — labeling rules already enforced |
| 11 | No PII, no real financial identifiers | Security | ✅ Pass | No new datasets introduced in Feature 4 |
| 12 | Artifact key format `task_id/model/category` | FR-011 (amended) | ✅ Pass | Consistent with PM-ratified amendment |
| 13 | No GPU dependencies | Explicit Prohibitions | ✅ Pass | No third-party packages |
| 14 | No `when_to_use` field in `SKILL.md` | Tech Stack | ✅ Pass | Prompt Engineer to enforce during `SKILL.md` authoring |
| 15 | LLM-generated output in artifact store | Principle 2 / Governance | ✅ Pass | Feature 4 persists LLM-generated content (Critic `.md`) as an artifact — consistent with Feature 2 treatment of SQL Critic output. Critic output is qualitative only and carries no numeric weight. Flagged for PM awareness. |

**All 15 items pass. Constitution Check gate is clear.**

> 📝 **Re-check required**: Item 7 must be verified for absence of model identifiers once `python_critic_persona.md` is manually authored.

---

## Project Structure

### Documentation (this feature)

```text
specs/004-python-qual-eval/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

Single-project CLI skill — Option 1 applies. Feature 4 extends `python-skill/` in place.

```text
python-skill/
├── SKILL.md
├── scripts/
│   ├── eval_task.py              # Existing — invokes eval_qualitative.py as subprocess
│   │                             # at end of every run; the two features are independently
│   │                             # testable via separate entry points
│   ├── eval_qualitative.py       # NEW — standalone CLI: eval-qualitative --engine python
│   │                             # (supplementary to FR-013 minimal CLI)
│   ├── anonymizer.py             # Existing — shared with Feature 3
│   ├── critic_runner.py          # NEW — invokes Python Critic persona on the anonymized
│   │                             # .py code file from assets/tasks/[task_id]/;
│   │                             # persists .md output
│   ├── schema_validator.py       # Existing
│   ├── scorer.py                 # Existing
│   ├── artifact_store.py         # Existing — extended to persist critic_review.md
│   └── schema_checker.py         # Existing
└── assets/
    ├── task_bank.csv             # Existing — master index, prompts inline
    ├── eval_results.csv          # Existing — unified pre-recorded metrics
    ├── tasks/
    │   └── [task_id]/
    │       ├── task{N}a.py       # Claude Sonnet 4.5's generated Python
    │       ├── task{N}b.py       # Gemini 2.5 Flash's generated Python
    │       ├── task{N}c.py       # ChatGPT 5.2 Codex's generated Python
    │       ├── reference_solution.py
    │       └── test_solution.py
    ├── datasets/
    │   ├── synthetic_clean_*.csv
    │   ├── synthetic_null_heavy_*.csv
    │   ├── synthetic_duplicate_heavy_*.csv
    │   ├── synthetic_medium_*.csv
    │   └── synthetic_large_*.csv
    └── personas/
        └── python_critic_persona.md   # NEW — manually authored; no model identifiers;
                                       # enforces four-section output structure:
                                       # strengths, failures, mitigation strategies,
                                       # observations. Self-contained within
                                       # python-skill/ — independent from
                                       # sql-skill/assets/personas/

outputs/
    └── [task_id]/
        └── [model]/
            └── [category]/
                ├── result.json        # Existing (from Feature 3) —
                │                      # already contains
                │                      # formatting_violations
                └── critic_review.md   # NEW — Python Critic four-section commentary

references/
├── methodology.md
├── rubric.md
├── file-schema.md
└── deterministic-rules.md

requirements.txt                       # No new dependencies for Feature 4

tests/
├── unit/
│   ├── test_anonymizer.py
│   ├── test_scorer.py
│   ├── test_schema_validator.py
│   ├── test_artifact_store.py
│   └── test_critic_runner.py          # NEW — Critic must be mocked;
│                                      # LLM invocation not tested at unit level
└── integration/
    ├── test_eval_task_pipeline.py     # Updated — verifies subprocess call to
    │                                  # eval_qualitative.py completes successfully
    └── test_eval_qualitative_pipeline.py  # NEW — end-to-end: Critic invocation
                                           # + artifact persistence
```

**Structure Decision**: Feature 4 extends `python-skill/` in place — no new top-level directories. `sql-skill/` and `python-skill/` are fully independent directory trees; no assets, personas, or scripts are shared between them — consistent with the Feature 2 pattern for SQL. `eval_task.py` invokes `eval_qualitative.py` as a subprocess, keeping the two features independently testable. One new script (`critic_runner.py`) and one new CLI entry point (`eval_qualitative.py`) are added under `scripts/`. The Critic reads the anonymized `.py` code file directly from `assets/tasks/[task_id]/` — no intermediate per-task `answers.csv` extraction step is required under the A3 two-table architecture. No `flake8_runner.py` is needed — the `formatting_violations` count is pre-recorded in `eval_results.csv` during dataset preparation and written to `result.json` by Feature 3's quantitative pipeline. The Python Critic persona template lives under `python-skill/assets/personas/` — self-contained within the Python skill tree, independent from `sql-skill/assets/personas/`. The Critic review is persisted as `critic_review.md` alongside `result.json` under the same `task_id/model/category` key.

---

## Complexity Tracking

N/A — no unresolved Constitution violations. All 15 Constitution Check items pass.

> 📝 **Re-check required**: Item 7 must be verified for absence of model identifiers once `python_critic_persona.md` is manually authored.
