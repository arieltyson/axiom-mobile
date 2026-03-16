# AXIOM-Mobile Model Selection and Baseline Scaffold

Last updated: 2026-03-15

## Purpose

Phase 2 starts with two separate needs:

1. A runnable end-to-end offline baseline so the team can validate experiment plumbing.
2. A structured shortlist of real VLM candidates for later training and Core ML work.

These are not the same requirement. The runnable baseline exists to prove the pipeline works now. The VLM shortlist exists to guide the next model-selection decision.

## Executable Baseline

The current executable model is:

- `question_lookup_v0`

It is a zero-dependency heuristic baseline that:

- memorizes the most common answer for each normalized training question
- falls back to the global majority answer when the question is unseen

This model is intentionally simple. It is not a deployable multimodal model. Its job is to validate:

- data loading
- split handling
- metrics computation
- artifact writing
- result schema stability

Run it with:

```bash
python3 ml/scripts/run_baseline.py
```

Outputs are written to:

- `results/baselines/question_lookup_v0_seed0/`

## Candidate Shortlist

The current VLM candidate configs live in:

- `ml/configs/models/florence_2_base.json`
- `ml/configs/models/llava_mobile.json`
- `ml/configs/models/qwen_vl_chat_int4.json`

These are config-only placeholders until the team locks:

- exact checkpoints
- dependency versions
- hardware feasibility
- Core ML conversion approach

## Selection Rubric

The baseline candidate decision should be made using this rubric:

1. Mobile feasibility
   - plausible path to `< 100 MB` deployed footprint after compression
   - realistic on-device latency path on iPhone/M-series hardware

2. Multimodal fit
   - supports image + text reasoning directly
   - suitable for screenshot QA rather than generic captioning only

3. Engineering feasibility
   - clear Python inference/training path
   - clear export/conversion story
   - manageable dependency surface for a class project timeline

4. Research value
   - credible baseline for later selection-strategy comparisons
   - not so large that deployment becomes the only challenge

## Result Artifact Contract

Every baseline run should write:

- `run_result.json`
- `model_state.json`
- `predictions_pool.jsonl`
- `predictions_val.jsonl`
- `predictions_test.jsonl`

The result JSON must include:

- model metadata
- dataset fingerprint
- split counts
- training summary
- per-split exact-match metrics
- artifact paths
