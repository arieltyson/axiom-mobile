# AXIOM-Mobile: Measuring Minimal Training Data Requirements for On-Device Domain Reasoning Under Mobile Constraints

**Annie Boltwood, Mahim Chaudhary, Ariel Tyson**
Simon Fraser University -- CMPT 416

*Draft v3 -- 2026-04-13. Updated with v1 model regime (128-class, dataset v2, class-weighted training) and expanded on-device profiling.*

---

## Abstract

We present AXIOM-Mobile, a system and experimental framework for measuring the minimal training set size (k\*) required for effective visual question answering on mobile devices under strict quality, latency, energy, and memory constraints. Our approach combines a SwiftUI + Core ML testbed app with a Python training/evaluation pipeline, enabling reproducible end-to-end experiments from dataset curation through on-device profiling. We report results across two experimental regimes. In the v0 regime (52 examples, 24 answer classes), we compare three data selection strategies -- random sampling, uncertainty-based selection, and diversity-based selection -- across six label budgets using bootstrap confidence intervals and paired resampling; no strategy achieves the 70% exact match target. In the v1 regime, we scale to 452 examples (128 answer classes) and retrain with class-weighted cross-entropy loss, improving test EM from 10% to 27.5% -- still far below the 70% target but demonstrating that dataset scale is indeed the binding constraint. Physical-device profiling on an iPhone 15 Pro Max (A17 Pro) yields inference latency of p50 = 14.0--14.5 ms across both model versions, well within the 400 ms / 600 ms thresholds. Energy and memory profiling remain outstanding. All experiment code, analysis scripts, and reproducible artifacts are included in the repository.

---

## 1. Introduction

Mobile devices increasingly serve as primary computing platforms, yet deploying domain-specific reasoning models on-device faces a fundamental tension: achieving acceptable quality requires sufficient training data, while mobile deployment imposes hard constraints on latency, energy, memory, and model size that preclude large foundation models.

**Research question.** What is the minimal training set size k\* that achieves *effective* domain reasoning on mobile devices, where effectiveness is defined jointly over quality and device constraints?

**Operational definition of effective** (all must hold simultaneously):
- Exact Match (EM) >= 70% on held-out test set
- Latency: p50 <= 400 ms, p95 <= 600 ms per query (measured on physical device)
- Energy: < 5% battery drain per hour during continuous use
- Model size: < 100 MB total app footprint
- Memory: peak < 500 MB RAM during inference

This paper contributes:
1. An end-to-end iOS/macOS testbed app with real Core ML inference, benchmark mode, and structured CSV/metadata export for reproducible on-device evaluation.
2. A comparison of three selection strategies (random, uncertainty, diversity) across six label budgets with bootstrap confidence intervals (v0 regime, 52 examples).
3. A statistical analysis pipeline with an explicit status vocabulary that prevents accidental overstatement of results.
4. A scaled dataset (v2: 452 examples, 128 answer classes) and retrained model (`tiny_multimodal_v1`) demonstrating a 2.75x improvement in test EM (10% to 27.5%), confirming that dataset scale is the primary lever for quality improvement.
5. Physical-device latency profiling on iPhone 15 Pro Max (A17 Pro) demonstrating that both v0 and v1 Core ML models meet latency thresholds with wide margin (p50 = 14.0--14.5 ms). Energy and memory profiling remain outstanding.

---

## 2. Related Work

**Data-efficient learning.** Active learning and core-set methods have shown that strategic data selection can reduce annotation requirements while maintaining model quality [Sener and Savarese 2018; Ash et al. 2020]. Our work applies this principle to a mobile VQA setting where the effectiveness criterion includes device constraints beyond accuracy alone.

**On-device ML.** Core ML [Apple 2023] and TensorFlow Lite enable deploying models on mobile hardware, but most benchmarking studies report only accuracy or use desktop profiling. We measure latency, memory, and energy on the target hardware using Apple Instruments, following the methodology of [Ignatov et al. 2019] for mobile AI benchmarking.

**Visual question answering.** VQA tasks [Antol et al. 2015] typically assume server-side inference. Mobile VQA for domain-specific screenshots (app UIs, settings panels, notifications) is underexplored. Our dataset targets this niche with screenshot-question-answer triples grounded in real iOS content.

**Learning curves and scaling laws.** Power-law relationships between dataset size and performance are well-documented [Hestness et al. 2017; Kaplan et al. 2020]. We attempt power-law fits on our learning curves but report honestly when the data is too sparse or degenerate for meaningful extrapolation.

---

## 3. System Overview

AXIOM-Mobile consists of two components:

### 3.1 iOS/macOS App (SwiftUI + Core ML)

The app provides:
- **Screenshot import** from the photo library
- **Question input** for natural-language queries about the screenshot
- **Model picker** supporting multiple model backends
- **Real Core ML inference** via `CoreMLInferenceService` for models with bundled `.mlpackage` files
- **Model metadata sidecar** system providing per-model metadata (class count, confidence threshold, training provenance) without hardcoding values in the app binary
- **Benchmark mode** with configurable iterations (1-50), per-inference CSV logging, and structured metadata export
- **Auto-benchmark mode** (`--auto-benchmark`) for headless profiling workflows with deterministic benchmark input

The benchmark pipeline uses `BenchmarkInputProvider` for repeatable inputs: a persisted real screenshot from the app's Documents directory, or a deterministic 390x844 synthetic test pattern that exercises the full CVPixelBuffer resize/BGRA conversion pipeline.

### 3.2 Python Training and Analysis Pipeline

The Python side provides:
- **Dataset management** with JSONL manifests and split validation
- **Model harness** with a shared interface (`train()`, `predict()`, `export_coreml()`)
- **Selection strategies** (random, uncertainty, diversity) with a sweep runner
- **PyTorch -> Core ML export** with post-conversion accuracy gate (<= 3% drop)
- **Statistical analysis** with bootstrap CIs, paired comparisons, power-law fits, and Pareto views
- **Device-profile ingestion** with threshold evaluation against the effectiveness criteria

---

## 4. Dataset

### 4.1 Dataset v1: Initial Collection (52 examples)

We curated 52 screenshot-question-answer triples from real iOS app content. Each example consists of:
- A screenshot image (stored privately, not in the Git repository)
- A natural-language question about the screenshot content
- A ground-truth answer string

Screenshots were collected from diverse iOS apps and reviewed in two passes with a shared Google Drive workflow.

**Splits (dataset v1):**

| Split | Count | Purpose |
|-------|-------|---------|
| Pool  | 37    | Available for selection/training |
| Val   | 5     | Held-out validation |
| Test  | 10    | Held-out evaluation |

There are 24 distinct answer classes across all examples.

Dataset v1 is used for all learning curve and selection strategy sweep experiments reported in Sections 6--7.2.

### 4.2 Dataset v2: Scaled Collection (452 examples)

To address the data scarcity bottleneck identified in the v0 regime, we expanded the dataset to 452 examples drawn from 152 unique screenshots (52 manual captures + 100 auto-generated screenshots). Answer strings were normalized into 128 distinct answer classes.

**Splits (dataset v2):**

| Split | Count | Purpose |
|-------|-------|---------|
| Pool  | 382   | Available for selection/training |
| Val   | 30    | Held-out validation |
| Test  | 40    | Held-out evaluation |

The 8.7x increase in pool size (37 to 382) and 5.3x increase in answer classes (24 to 128) represent a substantial scaling step, though the dataset remains small by VQA standards.

### 4.3 Limitations

- **Scale.** 452 examples is still below the 500-example target in the original proposal, and far below typical VQA benchmarks. Learning curves and strategy comparisons have only been run on dataset v1 (52 examples, 24 classes); no selection sweep has been run on dataset v2. This is an important gap.
- **Annotator agreement.** Dual-annotator agreement (Cohen's kappa >= 0.75) was planned but not implemented. Current labels reflect single-annotator judgments.
- **Answer granularity.** With 128 answer classes in dataset v2 and 40 test examples, the random baseline for exact match is approximately 0.8%. With 24 answer classes in dataset v1 and 10 test examples, the random baseline is approximately 4%.
- **Auto-generated screenshots.** 100 of 152 screenshots were auto-generated. While they exercise the data pipeline, their diversity and realism may differ from manually curated screenshots.

---

## 5. Models

### 5.1 Heuristic Baseline: question_lookup_v0

A zero-dependency lookup that memorizes the most common answer for each normalized training question, falling back to the global majority answer for unseen questions. This validates the experiment pipeline but has no visual understanding.

**Performance (dataset v1):**
- Pool EM: 72.97% (memorization, not generalization)
- Test EM: 10.00% (1/10 correct)
- Val EM: 0.00%

### 5.2 Trainable Baseline: tiny_multimodal_v0

A deliberately small (~40K parameters) multimodal model:
- **Image encoder:** 3-layer CNN (conv2d -> relu x3, adaptive avg pool) on 128x128 RGB -> 64-dim
- **Text encoder:** character-level embedding (ASCII, 128-vocab) + mean pool -> linear -> 64-dim
- **Fusion:** concatenation -> 128-dim
- **Head:** linear -> relu -> linear -> 24 classes

**Performance (dataset v1):**
- Pool EM: 16.22%
- Test EM: 10.00% (1/10 correct)
- Val EM: 0.00%
- Core ML artifact: 96 KB (well under 100 MB target)
- Parameters: ~40K (0.05M)

This model is designed to unblock the Core ML deployment pipeline, not to serve as the final research model. Its accuracy is low because it trains from scratch on 37 examples with no pretrained weights or transfer learning.

### 5.3 Retrained Model: tiny_multimodal_v1

The same architecture as v0 (3-layer CNN + character-level text encoder + concatenation fusion) but retrained on dataset v2 with the following changes:
- **Output classes:** 128 (up from 24)
- **Parameters:** ~47K (up from ~40K, due to larger output head)
- **Loss:** class-weighted cross-entropy with inverse-frequency weighting, capped at 10x, to handle the long-tailed answer distribution in 128 classes
- **Training:** 40 epochs on dataset v2 pool (382 examples)
- **Core ML export:** accuracy gate PASSED (0% drop between PyTorch and Core ML)

**Performance (dataset v2):**

| Metric | v0 (dataset v1) | v1 (dataset v2) | Change |
|--------|-----------------|-----------------|--------|
| Pool EM | 16.22% | 30.9% | +14.7 pp |
| Val EM | 0.00% | 26.7% | +26.7 pp |
| Test EM | 10.00% | 27.5% | +17.5 pp |
| Parameters | ~40K | ~47K | +7K |
| Output classes | 24 | 128 | +104 |

The v1 model is now the default model in the app, with a calibrated confidence threshold of 0.45 (set empirically).

**Interpretation.** The 2.75x improvement in test EM (10% to 27.5%) is encouraging as evidence that dataset scale is the primary lever, but 27.5% remains far below the 70% target. The model still trains from scratch with no pretrained backbone, and 47K parameters is extremely small. Reaching the quality target will likely require both more data and a stronger architecture (e.g., a pretrained vision-language model adapted via LoRA).

---

## 6. Selection Strategies

We compare three strategies for selecting training subsets from the pool:

| Strategy | Method | Implementation |
|----------|--------|----------------|
| Random (RAND) | Uniform random sampling | `random.sample(pool, k)` |
| Uncertainty (UNC) | Highest-entropy examples under current model | Prediction entropy ranking |
| Diversity (DIV) | Maximum feature-space coverage | k-center greedy selection |

A fourth strategy (KG-guided) is specified in the proposal but blocked pending knowledge graph infrastructure.

### 6.1 Sweep Configuration

> **Important:** All selection sweep experiments reported below were run on dataset v1 (52 examples, 24 answer classes) with the heuristic baseline. No sweep has been run on dataset v2 (452 examples, 128 classes). Results in this section should be interpreted as pipeline validation on a small dataset, not as evidence about strategy effectiveness at scale.

- **Budgets:** k = {5, 10, 15, 20, 25, 37}
- **Seeds:** 3 per strategy-budget combination
- **Model:** question_lookup_v0 (heuristic, used as the baseline for the sweep)
- **Total runs:** 3 strategies x 6 budgets x 3 seeds = 54

---

## 7. Experiments

### 7.1 Offline Evaluation (Learning Curves)

> **Note:** All learning curve results are from the v0 regime (dataset v1, 52 examples, 24 classes, heuristic baseline). They have not been rerun on dataset v2.

Each sweep run trains on the selected subset and evaluates test EM. Results are averaged across 3 seeds with bootstrap 95% confidence intervals (10,000 resamples, percentile method).

**Table 1: Learning curves by strategy (test EM, mean +/- 95% CI)**

| Budget | Random | Diversity | Uncertainty |
|--------|--------|-----------|-------------|
| 5      | 0.100 [0.000, 0.200] | 0.067 [0.000, 0.100] | 0.000 [0.000, 0.000] |
| 10     | 0.033 [0.000, 0.100] | 0.067 [0.000, 0.100] | 0.000 [0.000, 0.000] |
| 15     | 0.067 [0.000, 0.100] | 0.133 [0.000, 0.200] | 0.000 [0.000, 0.000] |
| 20     | 0.067 [0.000, 0.100] | 0.133 [0.000, 0.200] | 0.000 [0.000, 0.000] |
| 25     | 0.067 [0.000, 0.100] | 0.067 [0.000, 0.100] | 0.000 [0.000, 0.000] |
| 37     | 0.100 [0.100, 0.100] | 0.100 [0.100, 0.100] | 0.100 [0.100, 0.100] |

All strategies converge to identical test EM (10%) at the full pool budget (k=37). The uncertainty strategy is degenerate at sub-pool budgets, producing zero test EM.

**Power-law fits** (y = a * x^b, log-log OLS):
- Diversity: a=0.052, b=0.201, R^2=0.172
- Random: a=0.055, b=0.078, R^2=0.019
- Uncertainty: degenerate (only 1 non-zero y value; fit not attempted)

The low R^2 values indicate that power-law scaling is not a good fit for this data, which is expected given the tiny dataset and the heuristic baseline's limited capacity for learning from additional examples.

### 7.2 Strategy Comparisons

> **Note:** These comparisons are from the v0 regime only (dataset v1, heuristic baseline).

Paired bootstrap comparison (matched by seed) at full-pool budget (k=37):

| Comparison | Mean diff | 95% CI | Seeds |
|-----------|-----------|--------|-------|
| Diversity - Random | 0.000 | [0.000, 0.000] | 3 |
| Diversity - Uncertainty | 0.000 | [0.000, 0.000] | 3 |
| Random - Uncertainty | 0.000 | [0.000, 0.000] | 3 |

No strategy differences are detectable. All comparisons are based on only 3 paired seeds and should not be interpreted as evidence of equivalence.

### 7.3 On-Device Latency

#### Simulator Latency (Pipeline Validation)

> **Simulator measurements validate the instrumentation pipeline but are NOT publishable on-device evidence. The Simulator has no Neural Processing Unit (NPU), no real thermal behavior, and no meaningful energy data.**

**Table 2a: Simulator latency for tiny_multimodal_v0**

| Session | Iterations | Build | Input | p50 (ms) | p95 (ms) | Mean (ms) |
|---------|-----------|-------|-------|----------|----------|-----------|
| Session 1 | 20 | Debug | Blank | 199.5 | 304.2 | 220.2 |
| Session 2 | 50 | Release | Synthetic | 98.0 | 112.8 | 103.3 |

**Table 2b: Simulator latency for tiny_multimodal_v1**

| Session | Iterations | Build | Input | p50 (ms) | p95 (ms) | Mean (ms) |
|---------|-----------|-------|-------|----------|----------|-----------|
| Session 1 | 50 | Release | Synthetic | 125.0 | -- | -- |

The v1 model shows slightly higher simulator latency (125 ms vs 98 ms at p50), consistent with the marginally larger output head (128 vs 24 classes). Simulator latency is not meaningful for threshold evaluation.

#### Physical-Device Latency (iPhone 15 Pro Max, A17 Pro)

> **Physical-device measurements on AT-X (iPhone 15 Pro Max, A17 Pro, iOS 26.4.1). These are publishable on-device latency evidence.**

**Table 2c: Physical-device latency for tiny_multimodal_v0**

| Session | Iterations | Condition | p50 (ms) | p95 (ms) | Mean (ms) | Threshold |
|---------|-----------|-----------|----------|----------|-----------|-----------|
| Session 1 | 50 | Cold start | 14.0 | 26.2 | 18.0 | PASS |
| Session 2 | 50 | Warm, Time Profiler attached | 14.5 | 22.0 | 16.8 | PASS |

**Table 2d: Physical-device latency for tiny_multimodal_v1**

| Session | Iterations | Condition | p50 (ms) | p95 (ms) | Mean (ms) | Threshold |
|---------|-----------|-----------|----------|----------|-----------|-----------|
| Session 1 | 50 | Standard | 14.5 | 24.6 | -- | PASS |

All physical-device sessions pass all latency thresholds with wide margin (p50 <= 400 ms: 14.0--14.5 ms actual; p95 <= 600 ms: 22.0--26.2 ms actual). The v1 model (47K params, 128 classes) shows negligible latency difference compared to v0 (40K params, 24 classes) on physical hardware: p50 of 14.5 ms vs 14.0 ms. This confirms that the output head size change does not meaningfully affect on-device inference time on A17 Pro hardware.

**Energy and memory data are not yet available.** No `trace_metrics.json` sidecar exists for the physical-device sessions. Instruments Allocations and Energy Log traces remain outstanding.

### 7.4 Model Comparison (Pareto View)

**Table 3: Quality vs efficiency**

| Model | Dataset | Test EM | Latency p50 (ms) | Lat. Env | Size (MB) | Params |
|-------|---------|---------|------------------|----------|-----------|--------|
| question_lookup_v0 | v1 | 0.100 | -- | N/A | 0.1 | -- |
| tiny_multimodal_v0 | v1 | 0.100 | 14.0 | Physical | 0.5 | ~40K |
| tiny_multimodal_v1 | v2 | 0.275 | 14.5 | Physical | -- | ~47K |

`tiny_multimodal_v1` dominates both v0 models on quality (27.5% vs 10% test EM) with negligible latency increase (14.5 ms vs 14.0 ms). It is the sole Pareto-optimal point; the v0 models are now dominated. However, the Pareto frontier remains preliminary with only three points, all far below the 70% EM target. The frontier will become meaningful for the research question once models approaching the quality threshold are added.

---

## 8. Limitations and Threats to Validity

### 8.1 Quality Gap

The 70% EM target from the research proposal is not met. The best model achieves 27.5% test EM (v1 regime), up from 10% (v0 regime). The primary causes remain:
1. **Dataset scale:** 452 examples (382 pool) with 128 answer classes is an improvement over the v0 regime (52 examples, 37 pool, 24 classes) but still small by VQA standards. The v0-to-v1 improvement (+17.5 pp) suggests that further data scaling would continue to help, but the rate of improvement is not sufficient to reach 70% by linear extrapolation from current data.
2. **Model capacity:** `tiny_multimodal_v1` (47K params, no pretrained weights) cannot learn robust visual patterns even from 382 examples. It is a from-scratch model with a 3-layer CNN and character-level text encoder -- far weaker than pretrained vision-language models.
3. **No sweep on dataset v2.** The learning curve and selection strategy experiments (Section 7.1--7.2) were conducted only on dataset v1 (52 examples). It is unknown whether strategy differences become detectable at dataset v2 scale.

### 8.2 Physical-Device Evidence

Physical-device latency profiling is now available from 3 sessions across 2 model versions on AT-X (iPhone 15 Pro Max, A17 Pro), with p50 = 14.0--14.5 ms -- well within thresholds. However, the following remain outstanding:
- **Peak memory** (requires Instruments Allocations template on physical device -- trace not yet captured)
- **Energy consumption** (requires Instruments Energy Log -- not available on Simulator, not yet captured on device)
- **Thermal throttling effects** (longer sustained workloads needed to observe throttling behavior)

### 8.3 Statistical Limitations

- **3 seeds per condition:** Bootstrap CIs are computed honestly but are unreliable with only 3 observations.
- **No dual-annotator agreement:** Labels are single-annotator; potential noise in ground truth.
- **No KG-guided strategy:** The fourth selection strategy is blocked on knowledge graph infrastructure.
- **Power-law fits are poor:** Low R^2 values indicate the current data does not support scaling law extrapolation.
- **No sweep on dataset v2:** Selection strategy comparisons have not been rerun at 452-example scale.

### 8.4 Scope

- No ablation studies (single model architecture per category)
- No cross-validation (fixed splits only)
- No comparison to production VLMs (Florence, LLaVA, Qwen-VL remain config-only candidates)

---

## 9. Discussion

The primary contribution of this work at its current stage is **infrastructure validation with preliminary scaling evidence and physical-device latency profiling**. We have demonstrated:

1. **An end-to-end reproducible pipeline** from dataset curation through Core ML deployment and on-device benchmarking, with structured exports and automated analysis.
2. **Honest status tracking** via an explicit vocabulary (complete, partial, blocked, simulator_only, degenerate, etc.) that propagates through all analysis outputs, preventing accidental overstatement.
3. **A statistical analysis framework** (bootstrap CIs, paired comparisons, power-law fitting with degenerate-data guards) that will absorb stronger results as the dataset and models scale.
4. **Physical-device latency profiling** on iPhone 15 Pro Max (A17 Pro) showing that both v0 and v1 Core ML models achieve p50 = 14.0--14.5 ms inference latency -- 28x below the 400 ms threshold and 7x faster than iOS Simulator. The v0-to-v1 transition (24 to 128 output classes, 40K to 47K params) adds negligible latency on physical hardware.
5. **Preliminary scaling evidence.** The v0-to-v1 regime transition (52 to 452 examples, 24 to 128 classes, unweighted to class-weighted loss) improved test EM from 10% to 27.5%. While the architecture is unchanged and the absolute accuracy remains low, this confirms that dataset scale -- not model architecture -- is the binding constraint for this class of tiny models.

The path to publishable empirical results requires:
- Running the selection strategy sweep on dataset v2 to determine whether strategy differences emerge at scale
- Training a stronger model (LoRA-adapted VLM or similar) to test whether the quality gap closes
- Instruments traces for memory and energy evaluation on physical device
- Additional physical-device sessions for thermal throttling characterization
- Increasing seed count (>= 10 seeds) for statistically reliable strategy comparisons

---

## 10. Conclusion

We presented AXIOM-Mobile, a system for studying minimal training data requirements for on-device domain reasoning. The current implementation provides a fully functional iOS testbed with Core ML inference, a Python experiment pipeline with three selection strategies, and a statistical analysis package that honestly tracks what the data supports. Across two experimental regimes -- v0 (52 examples, 10% test EM) and v1 (452 examples, 27.5% test EM) -- we observe that dataset scaling is the primary lever for quality improvement, while on-device latency remains well within thresholds (p50 = 14.0--14.5 ms on iPhone 15 Pro Max). The 70% EM quality target, energy/memory profiling, selection strategy sweeps at v2 scale, and a production-grade model remain outstanding. The infrastructure is complete and designed to absorb future improvements with no code changes.

---

## References

- Antol, S., et al. "VQA: Visual Question Answering." ICCV 2015.
- Apple. "Core ML Documentation." developer.apple.com/documentation/coreml, 2023.
- Ash, J. T., et al. "Deep Batch Active Learning by Diverse, Uncertain Gradient Lower Bounds." ICLR 2020.
- Hestness, J., et al. "Deep Learning Scaling is Predictable, Empirically." arXiv:1712.00409, 2017.
- Ignatov, A., et al. "AI Benchmark: All About Deep Learning on Smartphones." ICCV Workshop 2019.
- Kaplan, J., et al. "Scaling Laws for Neural Language Models." arXiv:2001.08361, 2020.
- Sener, O. and Savarese, S. "Active Learning for Convolutional Neural Networks: A Core-Set Approach." ICLR 2018.

---

## Appendix A: Reproduction

All results in this paper can be reproduced from the repository:

```bash
# === v0 regime (dataset v1, 52 examples, 24 classes) ===

# 1. Run baseline experiments
python3 ml/scripts/run_baseline.py
python3 ml/scripts/run_trainable_baseline.py --image-root /path/to/screenshots_v1

# 2. Run selection sweep (dataset v1 only)
python3 ml/scripts/run_selection_sweep.py

# 3. Export Core ML model (v0)
python3 ml/scripts/export_coreml.py \
    --checkpoint-dir results/trainable_baselines/tiny_multimodal_v0_seed0/checkpoint \
    --image-root /path/to/screenshots_v1

# === v1 regime (dataset v2, 452 examples, 128 classes) ===

# 4. Train v1 model on dataset v2
python3 ml/scripts/run_trainable_baseline.py --image-root /path/to/screenshots_v2

# 5. Export Core ML model (v1)
python3 ml/scripts/export_coreml.py \
    --checkpoint-dir results/trainable_baselines/tiny_multimodal_v1_seed0/checkpoint \
    --image-root /path/to/screenshots_v2

# === Device profiling (both regimes) ===

# 6. Run device profiling (requires iOS Simulator or physical device)
xcrun simctl launch booted com.arieljtyson.AXIOMMobile --auto-benchmark

# 7. Stage and summarize device profiles
python3 ml/scripts/stage_device_profile_session.py --from-simulator --device-name "iphone17pro-sim"
python3 ml/scripts/summarize_device_profiles.py

# === Analysis ===

# 8. Run statistical analysis
python3 ml/scripts/run_statistical_analysis.py

# 9. Generate paper assets
python3 ml/scripts/build_paper_assets.py
```

## Appendix B: Dataset Fingerprints

### Dataset v1 (52 examples, 24 classes)

```
Combined SHA-256: bcd03f5e07337b475b28fea85ca01b0a3bb05db3e2dd3657554834ef5231446f
Pool SHA-256:     3c0cdf8dee3aa3f490c703fd1d1be5815b5351e3d0a3d39140ac171101c3b069
Test SHA-256:     08ce04944cda6a707ce4cdce3f723d33cfa884a05820af44e1c4fdbc91971b48
Val SHA-256:      6274769fa8fb0b137fe00aa167a404b726d96a1c6a8e45e2dae9e0835b2a16dd
```

### Dataset v2 (452 examples, 128 classes)

```
Combined SHA-256: [TO BE FILLED — run `python3 ml/scripts/fingerprint_dataset.py --dataset-version v2`]
Pool SHA-256:     [TO BE FILLED]
Test SHA-256:     [TO BE FILLED]
Val SHA-256:      [TO BE FILLED]
```
