# Mahim Task Guide

Below is the complete, optimal, hand-held solution for the next logical chunk for Mahim:

**Model Config Validation + CI Enforcement**

Follow it exactly and you will end with a clean PR that makes the model-config layer reliable before the team starts adding real VLM backends.

---

## Goal of This Step

By the end, the repo will contain:

- `ml/scripts/validate_model_configs.py`
- `ml/configs/models/README.md`
- `.github/workflows/python-checks.yml` updated to run the new validator

This task matters because the repo now has a model registry and candidate config files, but nothing prevents broken or inconsistent configs from being merged.

---

## What You Will Accomplish in This Chunk

1. Add a config validator for `ml/configs/models/*.json`
2. Define the config contract in writing
3. Make CI fail if model configs drift out of spec
4. Open a PR that protects the Phase 2 scaffold from bad metadata

---

## 1) Create a New Branch for This Step

From inside the repo:

```bash
git checkout main
git pull upstream main
git checkout -b ml/model-config-validation-v0
```

---

## 2) Inspect the Existing Model Config Layer

Read these files first:

- `ml/configs/models/question_lookup_v0.json`
- `ml/configs/models/florence_2_base.json`
- `ml/configs/models/llava_mobile.json`
- `ml/configs/models/qwen_vl_chat_int4.json`
- `ml/src/axiom/models/specs.py`
- `ml/src/axiom/models/registry.py`

Understand:

- the repo currently has one executable baseline
- the other configs are structured placeholders
- config metadata will be reused later for candidate selection and experiment logging

---

## 3) Create the Model Config Validator

Create:

- `ml/scripts/validate_model_configs.py`

### Script behavior requirements

The script should:

1. load all configs via the existing registry / spec loader
2. fail if there are zero configs
3. fail if two configs share the same `model_id`
4. fail if any required text field is empty:
   - `model_id`
   - `display_name`
   - `family`
   - `backend`
   - `stage`
   - `description`
   - `source`
5. fail if `stage` is not one of:
   - `baseline`
   - `candidate`
6. fail if `backend` is not one of:
   - `heuristic`
   - `transformers`
7. fail if no model is marked `executable=true`
8. print a short summary containing:
   - total config count
   - executable config count
   - candidate config count
   - model ids in priority order

### Implementation constraints

- use Python stdlib + the repo’s existing `axiom.models` code
- do not duplicate config parsing logic if the registry already provides it
- keep errors explicit and readable

### Expected run

From repo root:

```bash
python3 ml/scripts/validate_model_configs.py
```

---

## 4) Document the Config Contract

Create:

- `ml/configs/models/README.md`

### Required sections

Use these sections:

1. `Purpose`
2. `Required Fields`
3. `Allowed Values`
4. `Executable vs Candidate Configs`
5. `Validation Workflow`

### Required content

Document:

- what each config file represents
- which fields are mandatory
- what `stage=baseline` means
- what `stage=candidate` means
- why only one config is executable right now
- how to validate configs locally before opening a PR

---

## 5) Add the Validator to CI

Update:

- `.github/workflows/python-checks.yml`

Add one more step after the existing dataset/QC checks:

```bash
python3 ml/scripts/validate_model_configs.py
```

The goal is simple: if configs are malformed, the PR should fail automatically.

---

## 6) Validate Everything Locally

From repo root:

```bash
python3 ml/scripts/validate_model_configs.py
python3 ml/scripts/run_baseline.py
python3 ml/scripts/inspect_dataset.py
python3 ml/scripts/annotation_qc.py
```

The baseline run is just a quick smoke test to make sure the model registry still works after your changes.

---

## 7) Check Your Changes Before Committing

Run:

```bash
git status
```

You should see changes to:

- `ml/scripts/validate_model_configs.py`
- `ml/configs/models/README.md`
- `.github/workflows/python-checks.yml`

---

## 8) Commit Cleanly

```bash
git add ml/scripts/validate_model_configs.py ml/configs/models/README.md .github/workflows/python-checks.yml
git commit -m "ml: validate model configs in CI"
```

---

## 9) Push Your Branch

```bash
git push -u origin ml/model-config-validation-v0
```

---

## 10) Open a PR to the Team Repo

Use:

- Base repository: `AIML-Research-SFU/axiom-mobile`
- Base branch: `main`
- Compare branch: `ml/model-config-validation-v0`

### PR title

```text
ml: validate model configs in CI
```

### PR description

```text
Adds a model-config validator, documents the config contract, and runs the validator in GitHub Actions so malformed configs fail CI.
```

---

## Done Definition

You are done with this chunk when:

- `ml/scripts/validate_model_configs.py` runs cleanly
- `ml/configs/models/README.md` exists and is accurate
- CI is updated to run the validator
- the PR is open
