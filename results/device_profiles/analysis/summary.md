# Device Profile Summary Report

Generated: 2026-04-13T06:35:14Z
Sessions: 4
Models: tiny_multimodal_v0
Devices: iPhone (26.4), iPhone 15 Pro Max (26.4.1)
Placeholder sessions: 0
Real sessions: 4

## atx-iphone15promax_tiny_multimodal_v0_20260413T062922Z

- **Model:** tiny_multimodal_v0
- **Device:** iPhone 15 Pro Max (26.4.1)
- **Placeholder:** No
- **Records:** 50 total (50 benchmark, 0 single)
- **Latency:** min=11ms, mean=18.0ms, p50=14.0ms, p95=26.2ms, max=104ms

### Threshold Evaluation

| Metric | Threshold | Measured | Status | Reason |
|--------|-----------|----------|--------|--------|
| latency_p50 | <= 400 ms | 14.0 ms | **pass** | p50 latency meets threshold. |
| latency_p95 | <= 600 ms | 26.2 ms | **pass** | p95 latency meets threshold. |
| peak_memory | < 500 MB | — | **unavailable** | No trace_metrics.json with peak_memory_mb. Run Instruments Allocations template. |
| energy | < 5.0% battery/hr | — | **unavailable** | No trace_metrics.json with energy data. Run Instruments Energy Log on physical device. |
| exact_match | >= 70% EM | — | **unavailable** | Quality metrics (EM, BLEU, hallucination rate) are not captured in device benchmark sessions. These require offline evaluation against ground-truth labels from data/manifests/. |
| model_size | < 100 MB | — | **unavailable** | Model size is not captured in device benchmark sessions. Requires measuring .mlpackage size after Core ML conversion (Phase 4). |

## atx-iphone15promax_tiny_multimodal_v0_20260413T063305Z

- **Model:** tiny_multimodal_v0
- **Device:** iPhone 15 Pro Max (26.4.1)
- **Placeholder:** No
- **Records:** 50 total (50 benchmark, 0 single)
- **Latency:** min=11ms, mean=16.8ms, p50=14.5ms, p95=22.0ms, max=61ms

### Threshold Evaluation

| Metric | Threshold | Measured | Status | Reason |
|--------|-----------|----------|--------|--------|
| latency_p50 | <= 400 ms | 14.5 ms | **pass** | p50 latency meets threshold. |
| latency_p95 | <= 600 ms | 22.0 ms | **pass** | p95 latency meets threshold. |
| peak_memory | < 500 MB | — | **unavailable** | No trace_metrics.json with peak_memory_mb. Run Instruments Allocations template. |
| energy | < 5.0% battery/hr | — | **unavailable** | No trace_metrics.json with energy data. Run Instruments Energy Log on physical device. |
| exact_match | >= 70% EM | — | **unavailable** | Quality metrics (EM, BLEU, hallucination rate) are not captured in device benchmark sessions. These require offline evaluation against ground-truth labels from data/manifests/. |
| model_size | < 100 MB | — | **unavailable** | Model size is not captured in device benchmark sessions. Requires measuring .mlpackage size after Core ML conversion (Phase 4). |

## iphone17pro-sim_tiny_multimodal_v0_20260412T212027Z

- **Model:** tiny_multimodal_v0
- **Device:** iPhone (26.4)
- **Placeholder:** No
- **Records:** 20 total (20 benchmark, 0 single)
- **Latency:** min=185ms, mean=220.2ms, p50=199.5ms, p95=304.2ms, max=498ms

### Threshold Evaluation

| Metric | Threshold | Measured | Status | Reason |
|--------|-----------|----------|--------|--------|
| latency_p50 | <= 400 ms | 199.5 ms | **pass** | p50 latency meets threshold. |
| latency_p95 | <= 600 ms | 304.2 ms | **pass** | p95 latency meets threshold. |
| peak_memory | < 500 MB | — | **unavailable** | No trace_metrics.json with peak_memory_mb. Run Instruments Allocations template. |
| energy | < 5.0% battery/hr | — | **unavailable** | No trace_metrics.json with energy data. Run Instruments Energy Log on physical device. |
| exact_match | >= 70% EM | — | **unavailable** | Quality metrics (EM, BLEU, hallucination rate) are not captured in device benchmark sessions. These require offline evaluation against ground-truth labels from data/manifests/. |
| model_size | < 100 MB | — | **unavailable** | Model size is not captured in device benchmark sessions. Requires measuring .mlpackage size after Core ML conversion (Phase 4). |

## iphone17pro-sim_tiny_multimodal_v0_20260413T034245Z

- **Model:** tiny_multimodal_v0
- **Device:** iPhone (26.4)
- **Placeholder:** No
- **Records:** 50 total (50 benchmark, 0 single)
- **Latency:** min=91ms, mean=103.3ms, p50=98.0ms, p95=112.8ms, max=282ms

### Threshold Evaluation

| Metric | Threshold | Measured | Status | Reason |
|--------|-----------|----------|--------|--------|
| latency_p50 | <= 400 ms | 98.0 ms | **pass** | p50 latency meets threshold. |
| latency_p95 | <= 600 ms | 112.8 ms | **pass** | p95 latency meets threshold. |
| peak_memory | < 500 MB | — | **unavailable** | No trace_metrics.json with peak_memory_mb. Run Instruments Allocations template. |
| energy | < 5.0% battery/hr | — | **unavailable** | No trace_metrics.json with energy data. Run Instruments Energy Log on physical device. |
| exact_match | >= 70% EM | — | **unavailable** | Quality metrics (EM, BLEU, hallucination rate) are not captured in device benchmark sessions. These require offline evaluation against ground-truth labels from data/manifests/. |
| model_size | < 100 MB | — | **unavailable** | Model size is not captured in device benchmark sessions. Requires measuring .mlpackage size after Core ML conversion (Phase 4). |

