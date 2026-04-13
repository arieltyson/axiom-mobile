# AXIOM-Mobile Model Selection and Baseline Scaffold

Last updated: 2026-04-13

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

## Trainable Multimodal Baseline

As of 2026-04-12, the repo now has a second executable model:

- `tiny_multimodal_v0`

This is the first **real trainable multimodal model** in the repo. It is deliberately simple and small (~39K parameters), designed to unblock Phase 4 (Core ML conversion), not to be the final research model.

### Architecture

- **Image encoder:** 3-layer CNN (conv2d → relu × 3, adaptive_avg_pool2d) on 128×128 RGB input → 64-dim feature
- **Text encoder:** character-level embedding (ASCII, 128-vocab) + mean pool → linear → 64-dim feature
- **Fusion:** concatenation → 128-dim
- **Head:** linear → relu → linear → answer classes

### Why this model

1. **Unblocks Phase 4:** Produces a real `.pt` checkpoint that can be traced/scripted for Core ML conversion
2. **Export-friendly ops:** Only conv2d, relu, linear, embedding, adaptive_avg_pool2d — all have clean `coremltools` mappings
3. **Fixed input sizes:** 128×128 image, 128-char text — no variable-length sequences
4. **Small footprint:** ~160KB checkpoint, well under the 100MB target
5. **Image-aware:** Actually processes screenshot pixels, unlike `question_lookup_v0`

### What this model does NOT do

- It is not a strong model — accuracy on 37 training examples will be low
- It does not use pretrained weights or transfer learning
- It does not implement attention, transformers, or any VLM architecture
- It is not the final candidate for publication

### How to run

```bash
# With private screenshots:
python3 ml/scripts/run_trainable_baseline.py --image-root /path/to/screenshots_v1

# With synthetic fixtures (for testing):
python3 ml/scripts/run_trainable_baseline.py \
    --image-root results/trainable_fixtures/images \
    --manifest-dir results/trainable_fixtures/manifests \
    --output-dir results/trainable_fixtures/run_output
```

### What becomes possible after this

1. **Phase 4 Core ML conversion:** `torch.jit.trace()` the `TinyMultimodalNet` → `coremltools.convert()` → `.mlpackage`
2. **App integration:** Load the `.mlpackage` in `CoreMLInferenceService`, replacing the placeholder
3. **Real on-device profiling:** Benchmark actual model inference, not simulated latency
4. **Model upgrade path:** Replace `TinyMultimodalNet` with a stronger architecture (e.g., LoRA fine-tuned VLM) while keeping the same training/export pipeline

### Phase 4 status

- [x] `torch.jit.trace()` the trained model — implemented in `TinyMultimodalBaseline.export_coreml()`
- [x] `coremltools.convert()` to produce `.mlpackage` — 96KB output, well under 100MB target
- [x] Post-conversion accuracy gate (<= 3% drop) — `ml/scripts/export_coreml.py` compares PyTorch vs Core ML on val/test splits
- [x] Real-data training run — 37 pool / 5 val / 10 test on 52 real screenshots; 24 answer classes; train EM=16.2%, test EM=10%
- [x] App integration — `CoreMLInferenceService` loads bundled `.mlpackage`, preprocesses image+text, runs real Core ML prediction
- [x] Model catalog — `tiny_multimodal_v0` is first entry with `isCoreMLReady: true`
- [x] Benchmark pipeline — `isPlaceholder=false` for real Core ML runs; CSV + `_meta.json` export works
- [ ] Quantization — deferred (model is already 96KB)
- [ ] Real on-device profiling — unblocked, not yet run

## Trainable Multimodal Baseline v1 (Dataset v2 Refresh)

As of 2026-04-13, the repo has a second version of the trainable baseline:

- `tiny_multimodal_v1`

This model uses the **same architecture** as v0 (3-layer CNN + char-level text encoder + concat fusion) but is trained on **dataset v2** (382 pool examples, 128 normalized answer classes) with class-weighted cross-entropy loss.

### v0 → v1 comparison

| Metric | v0 (24 classes, dataset v1) | v1 (128 classes, dataset v2) |
|--------|----------------------------|------------------------------|
| Pool EM | 16.2% | 30.9% |
| Val EM | 0.0% | 26.7% |
| Test EM | 10.0% | 27.5% |
| Parameters | 40,376 | 47,136 |
| Training epochs | 20 | 40 |
| Class-weighted loss | No | Yes |
| Core ML accuracy drop | 0% | 0% |

### What changed

1. **128 normalized answer classes** (vs 24): classification head widened from 24 to 128 outputs
2. **Class-weighted CE loss**: inverse-frequency weights (capped at 10×) mitigate severe long-tail answer imbalance
3. **40 training epochs** (vs 20): longer training schedule for larger dataset
4. **Dataset v2**: 382 pool examples from 152 unique screenshots (vs 37 pool from 52 screenshots)

### Confidence calibration

v1 ships with an empirically calibrated confidence threshold (0.45) instead of v0's heuristic (0.40):

- **Correct predictions**: min confidence ~0.48, mean ~0.74–0.79
- **Incorrect predictions**: median confidence ~0.04, max ~0.50–0.64
- **Threshold 0.45**: preserves ~88–91% of correct predictions, filters most incorrect ones
- **Random baseline**: 1/128 = 0.78% (vs 1/24 = 4.2% for v0)

The threshold is stored in a per-model metadata sidecar (`tiny_multimodal_v1_metadata.json`), not hardcoded in Swift.

### How to run

```bash
# Train v1 on dataset v2:
python3 ml/scripts/run_trainable_baseline.py \
    --model-id tiny_multimodal_v1 \
    --image-root /path/to/screenshots_v1 \
    --epochs 40 \
    --class-weighted \
    --output-suffix _v2

# Export to Core ML:
python3 ml/scripts/export_coreml.py \
    --model-id tiny_multimodal_v1 \
    --checkpoint-dir results/trainable_baselines/tiny_multimodal_v1_seed0_v2/checkpoint \
    --image-root /path/to/screenshots_v1 \
    --output-dir results/coreml_exports/tiny_multimodal_v1_seed0_v2

# Copy artifacts into app:
cp -R results/coreml_exports/tiny_multimodal_v1_seed0_v2/TinyMultimodal.mlpackage \
    app/AXIOMMobile/AXIOMMobile/Resources/TinyMultimodalV1.mlpackage
cp results/coreml_exports/tiny_multimodal_v1_seed0_v2/label_vocab.json \
    app/AXIOMMobile/AXIOMMobile/Resources/tiny_multimodal_v1_labels.json
```

### App integration

v1 is the default model in the app. The `CoreMLInferenceService` dispatches by model ID to load the correct `.mlpackage` and label vocab. Both v0 and v1 are available in the model picker.

Model-specific behavior (confidence threshold, class count, supported question types) is driven by metadata sidecars (`{model_id}_metadata.json`) bundled in app Resources, so adding future model versions requires no Swift code changes.

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
