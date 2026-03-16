# Annie Task Guide

Below is the complete, optimal, hand-held solution for the next logical chunk for Annie:

**Baseline Results Summary + Reporting Script**

Follow it exactly and you will end with a clean PR that helps the team explain the current ML scaffold to the professor and reuse baseline outputs later.

---

## Goal of This Step

By the end, the repo will contain:

- `ml/scripts/summarize_baseline.py`
- `docs/BASELINE_RESULTS.md`
- a clean PR that documents what the current executable baseline does and what it does **not** prove

This task is important because the repo now has a runnable baseline (`question_lookup_v0`), but the outputs are still raw files. The team needs a reproducible summary layer on top of those artifacts.

---

## What You Will Accomplish in This Chunk

1. Read the current baseline artifact from `results/baselines/question_lookup_v0_seed0/`
2. Add a small Python script that summarizes a baseline run from `run_result.json`
3. Write a human-readable results note in `docs/BASELINE_RESULTS.md`
4. Open a PR that makes the baseline easier to discuss in meetings and reports

---

## 1) Create a New Branch for This Step

From inside the repo:

```bash
git checkout main
git pull upstream main
git checkout -b analysis/baseline-results-v0
```

---

## 2) Inspect the Existing Baseline Artifact

Before writing anything, inspect:

- `results/baselines/question_lookup_v0_seed0/run_result.json`
- `results/baselines/question_lookup_v0_seed0/model_state.json`
- `results/baselines/question_lookup_v0_seed0/predictions_val.jsonl`
- `results/baselines/question_lookup_v0_seed0/predictions_test.jsonl`

Understand these facts:

- `question_lookup_v0` is a lightweight heuristic baseline
- it is only for **pipeline validation**
- it is **not** a deployable multimodal model
- the key metrics right now are exact-match scores on `pool`, `val`, and `test`

Do **not** change the artifact files. They are generated outputs.

---

## 3) Create the Baseline Summary Script

Create:

- `ml/scripts/summarize_baseline.py`

### Script behavior requirements

The script should:

1. accept `--run-dir` as an argument
2. default to:
   - `results/baselines/question_lookup_v0_seed0`
3. read:
   - `run_result.json`
4. print a concise summary containing:
   - `run_id`
   - `model.display_name`
   - `dataset.split_counts`
   - `dataset.fingerprint.combined_sha256` (shortened to first 12 chars is fine)
   - `exact_match` for `pool`, `val`, and `test`
   - one-line notes field
5. fail clearly if the run directory or `run_result.json` is missing

### Implementation constraints

- use only Python stdlib
- keep it short and readable
- do not hardcode the metrics; read them from JSON

### Expected example run

From repo root:

```bash
python3 ml/scripts/summarize_baseline.py
```

Expected style of output:

- one short block with run metadata
- one short block with split metrics
- one short concluding line

---

## 4) Create the Baseline Results Note

Create:

- `docs/BASELINE_RESULTS.md`

### Required sections

Use these sections:

1. `Purpose`
2. `Current Executable Baseline`
3. `Frozen Dataset Snapshot`
4. `Observed Metrics`
5. `What This Baseline Proves`
6. `What This Baseline Does Not Prove Yet`
7. `Next Decision Enabled by This Run`

### Required content

Include:

- the current model id: `question_lookup_v0`
- the frozen split:
  - `pool=37`
  - `val=5`
  - `test=10`
- the observed EM values from `run_result.json`
- a short explanation that this baseline validates:
  - result writing
  - metric plumbing
  - dataset fingerprinting
  - experiment reproducibility
- a short explanation that it does **not** validate:
  - multimodal reasoning quality
  - mobile deployment feasibility
  - Core ML conversion

Keep the writing factual and concise.

---

## 5) Validate Everything Locally

From repo root:

```bash
python3 ml/scripts/run_baseline.py
python3 ml/scripts/summarize_baseline.py
python3 ml/scripts/inspect_dataset.py
python3 ml/scripts/annotation_qc.py
```

Your new script should run cleanly without modifying dataset files.

---

## 6) Check Your Changes Before Committing

Run:

```bash
git status
```

You should see changes to:

- `ml/scripts/summarize_baseline.py`
- `docs/BASELINE_RESULTS.md`

You may also see regenerated result artifacts locally, but those should stay ignored by git.

---

## 7) Commit Cleanly

```bash
git add ml/scripts/summarize_baseline.py docs/BASELINE_RESULTS.md
git commit -m "analysis: add baseline summary script and results note"
```

---

## 8) Push Your Branch

```bash
git push -u origin analysis/baseline-results-v0
```

---

## 9) Open a PR to the Team Repo

Use:

- Base repository: `AIML-Research-SFU/axiom-mobile`
- Base branch: `main`
- Compare branch: `analysis/baseline-results-v0`

### PR title

```text
analysis: add baseline summary script and results note
```

### PR description

```text
Adds a small baseline-run summary script and a docs note describing the current executable baseline, frozen split, and exact-match results.
```

---

## Done Definition

You are done with this chunk when:

- `ml/scripts/summarize_baseline.py` runs successfully
- `docs/BASELINE_RESULTS.md` is written and accurate
- the PR is open
- the team can explain the current baseline in one minute using repo files alone
