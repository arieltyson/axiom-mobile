# Device Profile Summary Report

Generated: 2026-04-12T17:57:33Z
Sessions: 2
Models: question_lookup_v0
Devices: Mac (15.4), iPhone (26.0)
Placeholder sessions: 2
Real sessions: 0

## Notes

- All sessions use placeholder inference. These results validate the instrumentation pipeline but are not publishable device-performance data.

## iphone14pro_question_lookup_v0_20260415T143000Z

- **Model:** question_lookup_v0
- **Device:** iPhone (26.0)
- **Placeholder:** Yes
- **Records:** 20 total (20 benchmark, 0 single)
- **Latency:** min=145ms, mean=150.7ms, p50=150.5ms, p95=156.1ms, max=157ms

### Threshold Evaluation

| Metric | Threshold | Measured | Status | Reason |
|--------|-----------|----------|--------|--------|
| latency_p50 | <= 400 ms | 150.5 ms | **placeholder** | Latency is simulated (PlaceholderInferenceService). Not valid for device-performance conclusions. |
| latency_p95 | <= 600 ms | 156.1 ms | **placeholder** | Latency is simulated (PlaceholderInferenceService). Not valid for device-performance conclusions. |
| peak_memory | < 500 MB | — | **unavailable** | No trace_metrics.json with peak_memory_mb. Run Instruments Allocations template. |
| energy | < 5.0% battery/hr | — | **unavailable** | No trace_metrics.json with energy data. Run Instruments Energy Log on physical device. |
| exact_match | >= 70% EM | — | **unavailable** | Quality metrics (EM, BLEU, hallucination rate) are not captured in device benchmark sessions. These require offline evaluation against ground-truth labels from data/manifests/. |
| model_size | < 100 MB | — | **unavailable** | Model size is not captured in device benchmark sessions. Requires measuring .mlpackage size after Core ML conversion (Phase 4). |

## m2mac_question_lookup_v0_20260416T090000Z

- **Model:** question_lookup_v0
- **Device:** Mac (15.4)
- **Placeholder:** Yes
- **Records:** 11 total (10 benchmark, 1 single)
- **Latency:** min=141ms, mean=144.7ms, p50=144.0ms, p95=148.5ms, max=149ms
- **Peak Memory:** 45.2 MB
- **CPU Energy Level:** 2/20

### Threshold Evaluation

| Metric | Threshold | Measured | Status | Reason |
|--------|-----------|----------|--------|--------|
| latency_p50 | <= 400 ms | 144.0 ms | **placeholder** | Latency is simulated (PlaceholderInferenceService). Not valid for device-performance conclusions. |
| latency_p95 | <= 600 ms | 148.5 ms | **placeholder** | Latency is simulated (PlaceholderInferenceService). Not valid for device-performance conclusions. |
| peak_memory | < 500 MB | 45.2 MB | **pass** | Peak memory within budget. |
| energy | < 5.0% battery/hr | CPU energy level: 2/20 | **unavailable** | Instruments Energy Log reports relative levels (0-20 scale), not battery %/hr directly. Manual interpretation required. Energy level is recorded for reference. |
| exact_match | >= 70% EM | — | **unavailable** | Quality metrics (EM, BLEU, hallucination rate) are not captured in device benchmark sessions. These require offline evaluation against ground-truth labels from data/manifests/. |
| model_size | < 100 MB | — | **unavailable** | Model size is not captured in device benchmark sessions. Requires measuring .mlpackage size after Core ML conversion (Phase 4). |

