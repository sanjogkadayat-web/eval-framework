---
description: "Task list for Feature 4 — Python Qualitative Evaluation"
---

# Tasks: Feature 4 — Python Qualitative Evaluation

**Input**: Design documents from `specs/004-python-qual-eval/`
**Prerequisites**: `feature4_plan.md` (required), `spec.md` (required for user stories), `constitution.md` (required for all guardrails), Feature 3 complete and passing (required — Feature 4 extends `python-skill/` in place and depends on `anonymizer.py`, `artifact_store.py`, and `eval_task.py` from F3)

**Tests**: Harness self-tests are included. Critic invocation is mocked at unit test level — LLM calls are never tested directly. The integration test verifies end-to-end artifact persistence using a mocked Critic response.

**Organization**: Feature 4 has one user story (US4 — Python Qualitative Evaluation, Priority P2). It is co-equal with US3 — the four-dimension rubric is incomplete without it. All tasks extend `python-skill/` in place; no new top-level directories are created. The pattern mirrors Feature 2 exactly, applied to the Python skill tree.

**Architecture**: Amendments A1, A2, and A3 are all ratified. Under A3, the Critic reads the anonymized `.py` code file directly from `assets/tasks/[task_id]/task{N}{a|b|c}.py` — there is no intermediate per-task `answers.csv` or `variant_results.csv` extraction step. The formatting violation count is the `formatting_violations` field in `eval_results.csv`, pre-read by Feature 3 into `result.json`. All paths resolve through `assets/task_bank.csv`.

> 📝 **Re-check gate**: Constitution Check item 7 requires manual verification that `python_critic_persona.md` contains no model identifiers once authored (T064). This check must be completed and documented before T067 (`critic_runner.py`) is marked done.

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US4)
- Task IDs continue from Feature 3 (T063+) to support cross-feature traceability
- Paths follow the A3 unified architecture: prompts in `assets/task_bank.csv`, metrics in `assets/eval_results.csv`, model code files under `assets/tasks/[task_id]/`, all path resolution via `task_bank.csv`

---

## Phase 1: Setup

**Purpose**: One new asset directory and persona template stub. No new top-level directories — Feature 4 extends `python-skill/` in place. `python-skill/assets/personas/` was scaffolded in Feature 3 (T041) and should already exist.

- [ ] T063 Add `python_critic_persona.md` stub to `python-skill/assets/personas/` — file must exist before `critic_runner.py` is implemented; stub may contain section headers only (strengths, failures, mitigation strategies, observations) with placeholder content. Confirm the directory exists from F3 scaffold (T041); create if absent.

**Checkpoint**: `python-skill/assets/personas/python_critic_persona.md` exists. No other structural changes required.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The Python Critic persona template must be fully authored and verified clean of model identifiers before `critic_runner.py` is implemented. This mirrors the F2 gate for the SQL Critic persona exactly.

**⚠️ CRITICAL**: `critic_runner.py` must not be implemented until T064 is complete and the Constitution Check item 7 re-check is documented as passing.

- [ ] T064 Author `python-skill/assets/personas/python_critic_persona.md` — manually authored; enforces four-section output structure (strengths, failures, mitigation strategies, observations); instructs Critic to produce no numeric score; instructs Critic to produce no model identifier in any section; written in plain language per constitution Principle 3; self-contained within `python-skill/` — independent from `sql-skill/assets/personas/sql_critic_persona.md`. **After authoring: perform explicit line-by-line check for the strings "Claude", "Gemini", "ChatGPT", "Sonnet", "Flash", "Codex", and any other model name variant — document the result of this check before proceeding to T067.**

**Checkpoint**: `python_critic_persona.md` is fully authored, reviewed, and confirmed clean of model identifiers. Constitution Check item 7 re-check is documented and passing.

---

## Phase 3: User Story 4 — Python Qualitative Evaluation (Priority: P2) 🎯

**Goal**: At the end of every `eval-task --engine python` invocation, the Python Critic persona is automatically invoked on the anonymized `.py` code file, returns structured four-section commentary with no numeric score and no model identifier, and the output is persisted as `critic_review.md` keyed by `task_id/model/category`. The Critic review is also invocable independently via `eval-qualitative --engine python`.

**Independent Test**: Run `eval-qualitative --engine python --task-id PY-001` against fixture data with a mocked Critic response. Verify: (1) the anonymized `.py` file (e.g., `assets/tasks/PY-001/task1a.py`) is passed to the Critic — only the filename letter reveals the model, no real name; (2) the Critic output contains all four sections (strengths, failures, mitigation strategies, observations); (3) no numeric score appears anywhere in the output; (4) `critic_review.md` is written to `outputs/PY-001/[model]/[category]/critic_review.md`; (5) `result.json` for the same run has `critic_review_path` populated. Run `eval-task --engine python --task-id PY-001` end-to-end and verify the Critic is invoked automatically as a subprocess without requiring a separate manual call.

### Harness Self-Tests for User Story 4 ⚠️

> **Write these tests FIRST. Ensure they FAIL before writing the implementation.**

- [ ] T065 [P] [US4] Write unit test `tests/unit/test_critic_runner.py` (Python skill) — mock the Critic LLM invocation; verify `critic_runner.py` passes the anonymized `.py` file (identified only by its filename letter `a`/`b`/`c`) to the Critic — no real model identifier is ever constructed or passed; verify the returned output is parsed and contains all four sections (strengths, failures, mitigation strategies, observations); verify a missing section raises a clear validation error; verify no numeric score pattern (e.g., digits followed by `/` or `%`) appears in parsed output; verify output is written as `.md` to the correct artifact path. Note: this is a new file under `python-skill/` — independent from `tests/unit/test_critic_runner.py` under `sql-skill/`.

- [ ] T066 [P] [US4] Write integration test `tests/integration/test_eval_qualitative_pipeline.py` (Python skill) — using fixture `task_bank.csv`, `.py` code files under `assets/tasks/`, and a mocked Critic response, run the full `eval-qualitative --engine python --task-id PY-001` pipeline end-to-end; verify `critic_review.md` is written to `outputs/PY-001/[model]/[category]/`; verify `result.json` at the same path has `critic_review_path` populated; verify the pipeline completes without error for all three filename letters (`a`, `b`, `c`); verify `eval_qualitative.py` resolves all paths via `task_bank.csv` (no hardcoded paths).

- [ ] T066b [US4] Update integration test `tests/integration/test_eval_task_pipeline.py` (Python skill, from Feature 3) — extend the existing end-to-end test to verify that `eval-task --engine python --task-id PY-001` now invokes `eval_qualitative.py` as a subprocess and that `critic_review.md` is produced alongside `result.json` (depends on T065 stub existing).

### Implementation for User Story 4

- [ ] T067 [US4] Implement `python-skill/scripts/critic_runner.py` — invokes the Python Critic persona from `python-skill/assets/personas/python_critic_persona.md` within the Claude Agent Skill execution context (no external API call); reads the anonymized `.py` code file from `assets/tasks/[task_id]/task{N}{letter}.py` (resolved via `task_bank.csv` — no hardcoded paths); passes the file content to the Critic with no added model identifier; parses the returned output into four sections (strengths, failures, mitigation strategies, observations); validates that no numeric score is present and that all four sections exist; writes output to `outputs/[task_id]/[model]/[category]/critic_review.md`. Must not be implemented until T064 persona re-check is documented and passing. Must pass T065 tests.

- [ ] T068 [US4] Implement `python-skill/scripts/eval_qualitative.py` — standalone CLI entry point: `eval-qualitative --engine python [--task-id PY-001]`; resolves the three model filenames for a task via `task_bank.csv` (no hardcoded paths per FR-018); invokes `critic_runner.py` for each model's anonymized `.py` file; persists output via `artifact_store.py`. Supplementary to the minimal CLI defined in FR-013 — `eval-task` and `scorecard` remain the required commands. Must pass T066 integration test.

- [ ] T069 [US4] Extend `python-skill/scripts/artifact_store.py` (from Feature 3) — add persistence of `critic_review.md` alongside the existing `result.json`; update `result.json` to populate the `critic_review_path` field (was `null` in Feature 3) with the relative path to the Critic review file; keyed by `task_id/model/category` per FR-011. Verify existing Feature 3 unit test `tests/unit/test_artifact_store.py` still passes after extension.

- [ ] T070 [US4] Update `python-skill/scripts/eval_task.py` (from Feature 3) — add subprocess invocation of `eval_qualitative.py` at the end of every `eval-task --engine python` run; the two entry points must remain independently testable (subprocess call, not a direct import); verify Feature 3 integration test `test_eval_task_pipeline.py` still passes after the update (it will need the extension from T066b to fully pass). Must pass T066b test.

**Checkpoint**: `eval-task --engine python --task-id PY-001` runs end-to-end and produces both `result.json` and `critic_review.md`. `eval-qualitative --engine python --task-id PY-001` runs independently and produces the same `critic_review.md`. All unit and integration tests pass. No model identifier appears in any Critic output. All four sections are present in every `critic_review.md`.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Quickstart update, compliance verification, and regression check against Feature 3.

- [ ] T071 [P] Update `quickstart.md` for `python-skill/` (from Feature 3) — add section covering: how the Critic review is triggered automatically, how to invoke `eval-qualitative --engine python` independently, how to read `critic_review.md`, what to do if a section is missing from Critic output. Maintain plain language and acronym-on-first-use convention per constitution Principle 3.

- [ ] T072 [P] Verify constitution compliance for all Feature 4 files — confirm: `python_critic_persona.md` contains no model identifier strings (Claude, Gemini, ChatGPT, Sonnet, Flash, Codex, or any variant); `critic_runner.py` produces no numeric score; `critic_review.md` artifacts are stored under `task_id/model/category`; `eval_qualitative.py` resolves all paths via `task_bank.csv` and never hardcodes paths; `python-skill/assets/personas/` is fully independent from `sql-skill/assets/personas/`.

- [ ] T073 Regression check — run the full Feature 3 test suite (`tests/unit/test_anonymizer.py`, `test_scorer.py`, `test_schema_validator.py`, `test_artifact_store.py`, `tests/integration/test_eval_task_pipeline.py`) after all Feature 4 changes are merged; confirm zero regressions from the `artifact_store.py` extension (T069) and the `eval_task.py` update (T070).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Depends on Feature 3 complete — `python-skill/assets/personas/` directory must exist (scaffolded in F3 T041)
- **Phase 2 (Foundational)**: Depends on Phase 1 — persona stub must exist before it can be authored
- **Phase 3 (User Story 4)**: Tests (T065–T066b) can be written as soon as Phase 2 completes; implementation (T067–T070) follows tests and requires Phase 2 checkpoint to pass
- **Phase 4 (Polish)**: Depends on Phase 3 checkpoint passing

### Within Phase 3

- T065, T066 (unit + new integration tests): Write first. Ensure FAIL.
- T066b (extension to F3 integration test): Can be written in parallel with T065/T066
- T067 (`critic_runner.py`): Depends on T064 (persona re-check documented) and T065 (test exists and fails)
- T068 (`eval_qualitative.py`): Depends on T067
- T069 (`artifact_store.py` extension): No dependency on T067/T068 — can be implemented in parallel with T067
- T070 (`eval_task.py` update): Depends on T068 and T069 both complete

### Relationship to Other Features

- Feature 4 is the direct Python-side mirror of Feature 2 — the patterns are identical; only the skill tree and persona differ
- Feature 4 depends on Feature 3 being complete; it cannot be started before the F3 Phase 3 checkpoint passes
- Feature 4 is a prerequisite for Feature 5 (Comparative Scorecard) — Feature 5 parses `critic_review.md` artifacts from both skill trees; both F2 and F4 must be complete before Feature 5 begins
- Feature 4 can be developed in parallel with Feature 2 once Feature 3 is complete (Feature 2 only requires Feature 1)

### Parallel Opportunities

T065 and T066 can be written in parallel. T067 and T069 can be implemented in parallel once T065 passes. T071 and T072 (polish) can run in parallel once the Phase 3 checkpoint passes.

---

## Parallel Example: Phase 3 Tests

```bash
# Write all tests simultaneously before any implementation:
Task: "Unit test for critic_runner.py in tests/unit/test_critic_runner.py"           # T065
Task: "Integration test for eval_qualitative pipeline (Python)"                       # T066
Task: "Extend F3 integration test to verify Critic subprocess invocation"             # T066b
```

---

## Implementation Strategy

### MVP First (User Story 4 Only)

1. Confirm Feature 3 checkpoint is passing (prerequisite)
2. Complete Phase 1: confirm or create persona stub
3. Complete Phase 2: author persona fully; perform and document model identifier re-check
4. Write tests (T065, T066, T066b) — ensure they FAIL
5. Implement in dependency order: `critic_runner.py` → `artifact_store.py` extension → `eval_qualitative.py` → `eval_task.py` update
6. **STOP and VALIDATE**: Run end-to-end `eval-task --engine python` and `eval-qualitative --engine python` against fixture data; confirm both produce `critic_review.md`; run full test suite including F3 regression check
7. Complete Phase 4 polish

### Delivery Position

Features 1–4 complete deliver the full four-dimension rubric for both SQL and Python. The combined output — `result.json` (correctness, formatting, performance) and `critic_review.md` (qualitative review) — for all three models across all tasks and variants is the complete input set for Feature 5 (Comparative Scorecard). Feature 5 cannot begin until both F2 and F4 are passing.

---

## Notes

- [P] tasks = different files, no blocking dependencies between them
- [US4] label maps all tasks to User Story 4 — Python Qualitative Evaluation
- Task IDs begin at T063 to maintain cross-feature traceability (F1: T001–T029, F2: T030–T040, F3: T041–T062)
- The Critic is the **only** LLM-generated content at harness runtime — all numeric scoring remains deterministic and script-enforced
- Under A3, model anonymization is **structural** — the Critic receives an anonymized code file identified only by its filename letter. There is no separate string-stripping step for the Critic; model identity is never constructed in Feature 4's code path.
- `eval_qualitative.py` is supplementary to FR-013; `eval-task` and `scorecard` remain the required CLI entry points
- `critic_runner.py` must mock the LLM in unit tests — never test LLM calls directly
- The persona template re-check (T064) is a hard gate for T067 — do not skip it
- `python-skill/assets/personas/` and `sql-skill/assets/personas/` are fully independent — the Python Critic persona must not reference or borrow from the SQL Critic persona
- `eval_qualitative.py` must resolve all paths via `task_bank.csv` — this is the FR-018 alignment point; no hardcoded paths to code files, `eval_results.csv`, or anything else
- Commit after each task; run the F3 regression suite (T073) before marking Feature 4 complete
