# AXIOM-Mobile Demo Flow

Last updated: 2026-04-13

## Demo Goal

Demonstrate the AXIOM-Mobile end-to-end pipeline: a user imports a screenshot, asks a question, and receives an on-device answer from a real Core ML model -- with visible latency, model metadata, and benchmark capabilities. The demo should communicate the research contribution (measuring minimal training data for on-device reasoning) without overstating current results.

## Prerequisites

- Xcode 26.0+ installed
- AXIOM-Mobile project builds successfully
- Either: physical iPhone (preferred) or iOS Simulator

## Demo Path A: Interactive Demo (Recommended)

### Setup (before audience arrives)

1. Open Xcode, select the `AXIOMMobile` scheme targeting your device/simulator
2. Build and run (Cmd+R)
3. Verify the app launches to the "AXIOM Testbed" screen
4. Have 2-3 screenshots ready in the Photos library (diverse iOS apps: Settings, Messages, Maps)

### Script

**[1] Introduction (30s)**
> "AXIOM-Mobile investigates how much training data is needed for a mobile device to answer questions about what's on screen -- under strict latency, energy, and size constraints. This is the testbed app running a real Core ML model on-device."

**[2] Import screenshot (15s)**
1. Tap the photo picker
2. Select a prepared screenshot
3. Point out: "The image is loaded locally -- no data leaves the device."

**[3] Ask a question (15s)**
1. Type a question relevant to the screenshot (e.g., "What app is this?" or "What is shown on screen?")
2. Point out the model picker showing `tiny_multimodal_v1`

**[4] Run inference (15s)**
1. Tap "Run Inference"
2. Point out the answer card and latency in the debug metrics
3. Say: "This is real Core ML inference -- a 47K-parameter model running entirely on-device. The latency you see is wall-clock time including image preprocessing. The app uses model metadata sidecars to set confidence thresholds automatically (0.45 for v1)."

**[5] Discuss the model honestly (30s)**
> "This is tiny_multimodal_v1, a 47K-parameter model trained on 382 examples from 152 screenshots across 128 answer classes. It achieves about 27.5% test exact match -- a 2.75x improvement over v0's 10%, but still far from the 70% target. The real research question is how many examples we need to reach 70% accuracy under mobile constraints. Learning curves and selection sweeps are still from the v0/dataset-v1 regime (52 examples) and need to be re-run with dataset v2."

**[6] Show benchmark mode (30s)**
1. Toggle Benchmark Mode ON
2. Set iterations to 5 (for demo speed)
3. Tap "Run Benchmark"
4. Show the benchmark summary card with latency statistics
5. Say: "The benchmark mode runs repeated inference for stable latency profiling. Each run is logged with timestamps, model metadata, and whether it's real or placeholder inference."

**[7] Show export capability (15s)**
1. Tap "Export CSV"
2. Show the share sheet
3. Say: "Every session exports structured CSV and companion JSON metadata -- device name, OS version, model ID, iteration count. This feeds directly into the Python analysis pipeline."

**[8] Wrap up (30s)**
> "The analysis pipeline computes bootstrap confidence intervals, fits learning curves, and compares selection strategies -- all with an explicit status system that marks what's simulator-only versus physical-device validated. The paper draft and all analysis artifacts are in the repository."

### Total: ~3 minutes

## Demo Path B: Auto-Benchmark (Headless)

Use when you want to show the profiling workflow without manual interaction.

```bash
# Simulator
xcrun simctl launch booted com.arieljtyson.AXIOMMobile --auto-benchmark

# Physical device (when available)
xcrun devicectl device process launch \
    --device <DEVICE_ID> \
    com.arieljtyson.AXIOMMobile -- --auto-benchmark
```

This automatically:
1. Selects `tiny_multimodal_v1`
2. Loads a benchmark image (persisted screenshot or synthetic test pattern)
3. Sets question: "What is shown on screen?"
4. Runs 50 iterations with real Core ML inference
5. Exports CSV + metadata JSON to Documents

After completion, stage and analyze:

```bash
python3 ml/scripts/stage_device_profile_session.py --from-simulator --device-name "iphone17pro-sim"
python3 ml/scripts/summarize_device_profiles.py
python3 ml/scripts/run_statistical_analysis.py
```

## Demo Path C: Demo Mode (Single-Shot)

Use for a clean, presentation-ready demo with a single inference.

```bash
# Simulator
xcrun simctl launch booted com.arieljtyson.AXIOMMobile --demo-mode

# Physical device (when available)
xcrun devicectl device process launch \
    --device <DEVICE_ID> \
    com.arieljtyson.AXIOMMobile -- --demo-mode
```

This automatically:
1. Selects `tiny_multimodal_v1`
2. Loads a benchmark image via `BenchmarkInputProvider`
3. Sets a canonical demo question
4. Runs **one** inference
5. Leaves the UI in a predictable demo-ready state showing the result

Unlike `--auto-benchmark`, this does not run 50 iterations or auto-export. It sets up the app for an interactive demo starting point.

## Fallback: Simulator Demo

If no physical device is available:

1. Use iOS Simulator (iPhone 17 Pro recommended)
2. All interactive demo steps work identically
3. **Explicitly say:** "We're running on the Simulator today. The latency numbers you see don't reflect real-device performance -- the Simulator has no Neural Processing Unit and different CPU scheduling. Our pipeline is ready for physical-device profiling once the iPhone is connected."

## Fallback: No Real Screenshot

If no real screenshot is available in the Photos library:

1. The demo still works -- type any question and run inference
2. The model will process whatever image is loaded (or a blank if none)
3. Alternatively, use demo mode (`--demo-mode`) which loads a synthetic test pattern automatically
4. **Say:** "The model is processing a synthetic test image. With a real screenshot, the full image preprocessing pipeline is identical."

## What to Say About Results

### Safe claims
- "The pipeline works end-to-end: data curation, training, Core ML export, on-device inference, benchmarking, and statistical analysis."
- "v1 achieves 27.5% test EM on 128 classes -- 2.75x improvement over v0 -- but still far from the 70% target."
- "v1 physical-device latency (p50=14.5ms) is essentially identical to v0 (p50=14.0ms), confirming that scaling from 24 to 128 classes has negligible latency cost."
- "Dataset v2 contains 452 examples from 152 screenshots across 128 classes."
- "The app uses model metadata sidecars for per-model confidence thresholds (0.45 for v1)."
- "We compare three selection strategies with bootstrap confidence intervals (under the v0/dataset-v1 regime)."
- "The analysis package explicitly marks every result with its status -- simulator-only, partial, or blocked."

### What NOT to claim
- Do NOT say the model is accurate ("v1 achieves ~27.5% test EM, still far below the 70% target")
- Do NOT present simulator latency as on-device performance (real on-device numbers now exist: v0 p50=14.0ms, v1 p50=14.5ms on iPhone 15 Pro Max -- use those instead)
- Do NOT claim statistical significance from 3-seed comparisons
- Do NOT say any selection strategy is better than another (learning curves/selection sweeps are still from v0/dataset-v1 regime with 52 examples)
- Do NOT claim energy or memory results exist (physical device Instruments traces required)

## Explaining Simulator vs Physical Device

If asked about the distinction:

> "iOS Simulator runs on the Mac CPU -- it doesn't have the Neural Processing Unit or real thermal management that iPhones have. We've profiled both v0 and v1 on a real iPhone 15 Pro Max: v0 p50=14.0ms, v1 p50=14.5ms -- essentially identical, and about 7x faster than the Simulator's ~98ms. The Simulator is useful for pipeline validation, but the physical-device numbers are what we report. Energy and memory Instruments traces are still outstanding."

## Demo Checklist

- [ ] App builds and runs
- [ ] Model picker shows `tiny_multimodal_v1`
- [ ] Photo library has prepared screenshots (or use demo mode)
- [ ] Inference runs and shows answer + latency
- [ ] Benchmark mode runs and shows summary statistics
- [ ] Export produces CSV + metadata JSON
- [ ] You have practiced the honest framing of limitations
