# AXIOM-Mobile Results

This directory stores experiment artifacts that are generated locally and are not intended to be committed in full.

## Baseline Runs

The Phase 2 scaffold writes lightweight baseline runs to:

- `results/baselines/<model_id>_seed<seed>/`

Current executable baseline:

- `question_lookup_v0`

Expected files per run:

- `run_result.json`
- `model_state.json`
- `predictions_pool.jsonl`
- `predictions_val.jsonl`
- `predictions_test.jsonl`

`run_result.json` is the canonical summary artifact for later analysis.
