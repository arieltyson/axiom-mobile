# AXIOM-Mobile iOS App

## Testbed Shell (Phase 2)

The app currently provides a **testbed shell** for exercising the screenshot QA flow before real model inference is available.

### What it does

1. **Screenshot import** — pick any image from the photo library.
2. **Question input** — type a natural-language question about the screenshot.
3. **Model picker** — choose from the four model IDs defined in `ml/configs/models/`:
   - `question_lookup_v0` (executable baseline)
   - `florence_2_base` (VLM candidate)
   - `llava_mobile` (VLM candidate)
   - `qwen_vl_chat_int4` (VLM candidate)
4. **Run** — triggers a placeholder inference pass with simulated latency.
5. **Answer card** — displays the demo result.
6. **Debug metrics card** — shows model ID, image status, question length, and latency.

### Architecture

```
AXIOMMobile/
├── AXIOMMobileApp.swift            App entry point (TipKit configured)
├── ContentView.swift               Root view (launch screen → TestbedView)
├── DesignSystem/                   Semantic design tokens + reusable components
│   ├── AXColor.swift               Adaptive color roles (accent, background, glass, status)
│   ├── AXSpacing.swift             4-pt grid spacing scale
│   ├── AXShape.swift               Corner radii and stroke widths
│   ├── AXTypography.swift          Semantic font roles (Dynamic Type)
│   ├── AXMotion.swift              Animation presets (Reduce Motion aware)
│   ├── AXElevation.swift           Shadow/depth tokens
│   ├── AXHaptics.swift             Haptic feedback tokens (SensoryFeedback mapping)
│   ├── AXLayout.swift              Responsive layout tokens (iPad adaptation)
│   ├── AXTransition.swift          Transition presets + staggered entrance modifier
│   └── Components/
│       ├── GlassCard.swift         Glass-material card container (3 hierarchy levels)
│       ├── AXButtonStyle.swift     Primary, secondary, compact button styles
│       ├── StatusBadge.swift       Status pill/chip (5 variants)
│       └── SectionHeader.swift     Consistent icon + title section header
├── Models/
│   ├── ModelCatalog.swift          Model metadata matching repo configs
│   ├── InferenceResult.swift       Inference result value type
│   ├── BenchmarkRecord.swift       Structured benchmark log record
│   └── SessionMetadata.swift       Device/session metadata for reproducibility
├── Services/
│   ├── InferenceService.swift      Protocol + placeholder implementation
│   ├── CoreMLInferenceService.swift  Real Core ML inference (v0/v1 model dispatch)
│   ├── BenchmarkExporter.swift     CSV export to Documents directory
│   └── BenchmarkInputProvider.swift  Repeatable benchmark input (persisted/synthetic screenshot)
├── Resources/
│   ├── TinyMultimodal.mlpackage         Exported Core ML model v0 (96KB, 24 classes)
│   ├── TinyMultimodalV1.mlpackage       Exported Core ML model v1 (128 classes, dataset v2)
│   ├── tiny_multimodal_v0_labels.json   Label vocabulary v0 (24 classes)
│   ├── tiny_multimodal_v0_metadata.json Model metadata sidecar v0
│   ├── tiny_multimodal_v1_labels.json   Label vocabulary v1 (128 classes)
│   └── tiny_multimodal_v1_metadata.json Model metadata sidecar v1 (calibrated threshold)
└── Features/
    ├── Onboarding/
    │   ├── AXTips.swift            TipKit tips (research context, screenshot, benchmark, CoreML)
    │   └── LaunchScreen.swift      Branded launch screen + programmatic AppIconView
    └── Testbed/
        ├── TestbedView.swift       Main testbed screen (staggered entrance, haptics, tips)
        ├── TestbedViewModel.swift  @Observable view model (routes real vs placeholder)
        └── Views/
            ├── ScreenshotSection.swift     Hero card with empty-state and image preview
            ├── QuestionInputSection.swift  Glass-enclosed text field
            ├── ModelPickerSection.swift    Model picker with status badge + CoreML tip
            ├── AnswerCard.swift            Elevated hero result card with entrance animation
            ├── DebugMetricsCard.swift      Collapsible subdued metrics card
            ├── BenchmarkConfigSection.swift Compact benchmark toggle + benchmark tip
            └── BenchmarkSummaryCard.swift  Metric tiles with export actions + haptics
```

### Design System

The app includes a design-system layer (`DesignSystem/`) that provides semantic tokens for color, spacing, shape, typography, motion, elevation, haptics, layout, and transitions. All feature views consume these tokens — no magic numbers or raw colors in view code.

Key additions in the v1 pass:
- **AXHaptics** — maps logical events (inference complete, export, clear) to `SensoryFeedback` types
- **AXLayout** — responsive container modifier for iPad/larger displays (`axResponsiveContainer()`)
- **AXTransition** — card entrance, result appearance, and staggered cascade presets (Reduce Motion aware)
- **Light mode polish** — increased contrast ratios for glass fills, strokes, tertiary text, and accent colors

See `docs/DESIGN_SYSTEM.md` for full documentation of token categories, component usage rules, and accessibility behavior.

### Onboarding (TipKit)

The app uses Apple TipKit for contextual first-run tips:
- **Research Context** — explains AXIOM on first launch
- **Screenshot Import** — shown until the user imports their first screenshot
- **Benchmark Mode** — appears after 3+ single-run inferences
- **Core ML Model** — shown when the user selects a placeholder model

Tips respect system tip display preferences and are shown at most once.

### Launch Screen

A branded launch screen displays the AXIOM icon and tagline for ~1.2 seconds on app start, then crossfades to the main testbed view. The `AppIconView` component renders the icon programmatically for use in both the launch screen and as a preview — the actual app icon assets are exported via `app/scripts/export_app_icon.swift`.

### Real Core ML inference

The app includes real Core ML inference for the `tiny_multimodal` model family (v0 and v1):

1. **`CoreMLInferenceService`** dispatches by model ID to load the correct `.mlpackage` and label vocabulary (e.g. `TinyMultimodalV1.mlpackage` + `tiny_multimodal_v1_labels.json` for v1).
2. It preprocesses the screenshot (resize to 128×128, BGRA pixel buffer) and question (ASCII character-level encoding, padded to 128 chars).
3. It runs Core ML prediction and decodes the argmax of the logit output into an answer string with softmax confidence.
4. `TestbedViewModel` routes to `CoreMLInferenceService` when `isCoreMLReady` is true, otherwise falls back to `PlaceholderInferenceService`.
5. The `isPlaceholder` field is `false` for real Core ML runs, so benchmark exports accurately distinguish real from simulated inference.
6. **Confidence thresholds** are loaded from per-model metadata sidecars (`{model_id}_metadata.json`), not hardcoded. v0 uses 0.40 (heuristic), v1 uses 0.45 (empirically calibrated from val/test confidence distributions).

### Refreshing or adding a model version

To update the bundled model after re-training/re-exporting:

```bash
# 1. Train v1 on dataset v2
python3 ml/scripts/run_trainable_baseline.py \
    --model-id tiny_multimodal_v1 \
    --image-root /path/to/screenshots_v1 \
    --epochs 40 --class-weighted --output-suffix _v2

# 2. Export to Core ML
python3 ml/scripts/export_coreml.py \
    --model-id tiny_multimodal_v1 \
    --checkpoint-dir results/trainable_baselines/tiny_multimodal_v1_seed0_v2/checkpoint \
    --image-root /path/to/screenshots_v1 \
    --output-dir results/coreml_exports/tiny_multimodal_v1_seed0_v2

# 3. Copy artifacts into app
cp -R results/coreml_exports/tiny_multimodal_v1_seed0_v2/TinyMultimodal.mlpackage \
    app/AXIOMMobile/AXIOMMobile/Resources/TinyMultimodalV1.mlpackage
cp results/coreml_exports/tiny_multimodal_v1_seed0_v2/label_vocab.json \
    app/AXIOMMobile/AXIOMMobile/Resources/tiny_multimodal_v1_labels.json

# 4. Rebuild in Xcode
```

### Extending with additional models

To add a new model version:

1. Add a `ModelResources` mapping in `CoreMLInferenceService.swift` (model ID → `.mlpackage` + labels resource name)
2. Add a `ModelInfo` entry to `ModelCatalog.swift`
3. Create a `{model_id}_metadata.json` sidecar with calibrated threshold, class count, and supported question types
4. Copy the `.mlpackage`, labels JSON, and metadata JSON into `Resources/`
5. Rebuild — no other Swift changes needed (all UI copy is metadata-driven)

## Benchmark Mode (Phase 5 Instrumentation)

The testbed includes a benchmark mode for repeated inference runs and structured logging.

### How it works

1. Toggle **Benchmark Mode** in the config section.
2. Set the iteration count (1-50) with the stepper.
3. Tap **Run Benchmark** — the app runs inference N times and logs each result.
4. View aggregate statistics in the **Benchmark Summary** card (runs, avg/min/max latency, model ID, export status).
5. Tap **Export CSV** to save results to the app's Documents directory.
6. Use **Share** to send the CSV via AirDrop, email, or other share targets.
7. Tap **Clear** to reset the session.

Single-run inference (benchmark mode off) also logs records with `run_kind: single`.

### CSV schema

```csv
timestamp,model_id,image_loaded,question_length,latency_ms,is_placeholder,run_kind,iteration_index
```

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | ISO 8601 | When the inference completed |
| `model_id` | string | Model identifier from `ModelCatalog` |
| `image_loaded` | bool | Whether a screenshot was loaded |
| `question_length` | int | Character count of the question |
| `latency_ms` | int | Inference latency in milliseconds |
| `is_placeholder` | bool | Whether the result came from placeholder service |
| `run_kind` | string | `single` or `benchmark` |
| `iteration_index` | int | 0 for single runs; 0..N-1 for benchmark iterations |

### Export location

CSV files are written to the app's Documents directory with filenames like:

```
axiom_benchmark_20260412T101500Z.csv
```

A companion metadata JSON is exported alongside each CSV:

```
axiom_benchmark_20260412T101500Z_meta.json
```

The metadata file captures device and session context for reproducibility:

| Field | Description |
|-------|-------------|
| `session_id` | Unique UUID per export |
| `export_timestamp` | ISO 8601 export time |
| `device_name` | `UIDevice.current.name` |
| `device_model` | `UIDevice.current.model` (iPhone, iPad) |
| `system_name` / `system_version` | OS name and version |
| `app_version` / `app_build` | Bundle short version and build number |
| `model_id` | Model used for the benchmark |
| `is_placeholder` | Whether inference was simulated |
| `benchmark_iterations` | Number of benchmark-mode runs |
| `record_count` | Total records in the CSV |

The **Share** button (appears after export) sends both the CSV and metadata JSON via the system share sheet.

### Real vs placeholder inference

| Model | Service | `isPlaceholder` |
|-------|---------|-----------------|
| `tiny_multimodal_v1` | `CoreMLInferenceService` | `false` |
| `tiny_multimodal_v0` | `CoreMLInferenceService` | `false` |
| `question_lookup_v0` | `PlaceholderInferenceService` | `true` |
| `florence_2_base` | `PlaceholderInferenceService` | `true` |
| `llava_mobile` | `PlaceholderInferenceService` | `true` |
| `qwen_vl_chat_int4` | `PlaceholderInferenceService` | `true` |

The routing is automatic: `TestbedViewModel` checks `selectedModel.isCoreMLReady` and dispatches to the appropriate service. Benchmark CSV exports and `_meta.json` accurately record which service was used via the `is_placeholder` field.

## Demo Mode

For presentation setup with a single inference, launch the app with `--demo-mode`:

```bash
# Via Simulator:
xcrun simctl launch booted com.arieljtyson.AXIOMMobile --demo-mode

# Via Xcode scheme:
# Edit Scheme > Run > Arguments > Add "--demo-mode"
```

This automatically:
1. Selects the first Core ML-ready model (currently `tiny_multimodal_v1`)
2. Loads a representative image via `BenchmarkInputProvider`
3. Sets a canonical demo question ("What is shown on screen?")
4. Runs **one** inference
5. Leaves the UI in a demo-ready state showing the result

Unlike `--auto-benchmark`, demo mode does not run multiple iterations or auto-export. It sets up the app for an interactive presentation starting point. See `docs/DEMO_FLOW.md` for the full rehearsable demo script.

## Auto-Benchmark Mode

For repeatable profiling without manual UI interaction, launch the app with the `--auto-benchmark` argument:

```bash
# Via Simulator:
xcrun simctl launch booted com.arieljtyson.AXIOMMobile --auto-benchmark

# Via Xcode scheme:
# Edit Scheme > Run > Arguments > Add "--auto-benchmark"
```

This automatically:
1. Selects the first Core ML-ready model (currently `tiny_multimodal_v1`)
2. Loads a representative benchmark image via `BenchmarkInputProvider`
3. Sets a fixed question ("What is shown on screen?")
4. Runs 50 benchmark iterations with real Core ML inference
5. Exports CSV + `_meta.json` to the app's Documents directory

### Benchmark Input

The auto-benchmark uses `BenchmarkInputProvider` to ensure the full image preprocessing pipeline is exercised:

1. **Persisted screenshot** (preferred): If `benchmark_screenshot.png` exists in the app's Documents directory, it is loaded. This is the ideal path for publishable profiling.
2. **Synthetic test pattern** (fallback): If no persisted screenshot is found, a deterministic 390×844 gradient+noise image is generated. This exercises the full `CVPixelBuffer` resize/conversion pipeline with non-trivial pixel data.

To persist a real screenshot for future runs:

```bash
# Option A: Use the app UI — import a screenshot, then tap "Save as Benchmark Input"

# Option B: Copy directly to Documents (Simulator):
DOCS=$(xcrun simctl get_app_container booted com.arieljtyson.AXIOMMobile data)/Documents
cp /path/to/screenshot.png "$DOCS/benchmark_screenshot.png"
```

### Staging results

```bash
python3 ml/scripts/stage_device_profile_session.py \
    --from-simulator \
    --device-name "iphone17pro-sim"
```

## Requirements

- Xcode 26.0+
- iOS 26.0+
- No third-party dependencies
