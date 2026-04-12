"""Typed schemas for device-profile ingestion and summary pipeline.

These schemas define the contract for consuming exported app benchmark
sessions (CSV + _meta.json), optionally merging manual Instruments trace
metrics, and producing per-session and aggregate performance summaries.

All inference currently runs through PlaceholderInferenceService. Sessions
where is_placeholder=True are explicitly marked as *not valid* for
publishable device-performance conclusions.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Raw ingestion schemas (mirror the app export contract)
# ---------------------------------------------------------------------------


@dataclass
class BenchmarkCSVRow:
    """One row from the app-exported benchmark CSV."""

    timestamp: str
    model_id: str
    image_loaded: bool
    question_length: int
    latency_ms: int
    is_placeholder: bool
    run_kind: str  # "single" | "benchmark"
    iteration_index: int


@dataclass
class SessionMetadata:
    """Mirror of the app-exported _meta.json companion file."""

    session_id: str
    export_timestamp: str
    device_name: str
    device_model: str
    system_name: str
    system_version: str
    app_version: str
    app_build: str
    model_id: str
    is_placeholder: bool
    benchmark_iterations: int
    record_count: int


# ---------------------------------------------------------------------------
# Optional Instruments trace summary sidecar
# ---------------------------------------------------------------------------


@dataclass
class TraceMetrics:
    """Manually extracted summary from Instruments .trace files.

    Users fill this in by hand after running Instruments. The Python
    pipeline never parses .trace binaries directly.

    All fields are optional — partial sessions are expected.
    """

    peak_memory_mb: float | None = None
    cpu_energy_level: float | None = None   # 0–20 Instruments scale
    gpu_energy_level: float | None = None   # 0–20 Instruments scale
    overhead_energy_level: float | None = None
    cpu_time_user_s: float | None = None
    cpu_time_system_s: float | None = None
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None and v != ""}


# ---------------------------------------------------------------------------
# Per-session computed summary
# ---------------------------------------------------------------------------


@dataclass
class ThresholdEvaluation:
    """Evaluation of one effectiveness threshold from SPEC.md.

    status is one of:
    - "pass"       — metric meets threshold
    - "fail"       — metric does not meet threshold
    - "unavailable"— data required for evaluation is missing
    - "placeholder" — data exists but comes from simulated inference

    reason always explains the status in human-readable form.
    """

    metric_name: str
    threshold: str
    measured_value: str | None
    status: str  # "pass" | "fail" | "unavailable" | "placeholder"
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LatencyStats:
    """Latency statistics computed from benchmark CSV rows."""

    count: int
    min_ms: int
    max_ms: int
    mean_ms: float
    p50_ms: float
    p95_ms: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SessionSummary:
    """Complete summary for one device-profiling session."""

    session_id: str
    session_dir: str
    export_timestamp: str

    # Device / environment
    device_name: str
    device_model: str
    system_version: str
    app_version: str
    app_build: str

    # Model
    model_id: str
    is_placeholder: bool

    # Record counts
    total_records: int
    benchmark_records: int
    single_records: int

    # Latency (from benchmark CSV)
    latency: LatencyStats

    # Optional Instruments metrics
    trace_metrics: dict[str, Any] = field(default_factory=dict)
    has_trace_metrics: bool = False

    # Threshold evaluations
    thresholds: list[dict[str, Any]] = field(default_factory=list)

    # Validation
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# Aggregate summary across sessions
# ---------------------------------------------------------------------------


@dataclass
class AggregateSummary:
    """Summary across all valid device-profiling sessions."""

    created_at_utc: str
    session_count: int
    sessions: list[dict[str, Any]]
    models_seen: list[str]
    devices_seen: list[str]
    placeholder_session_count: int
    real_session_count: int
    overall_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
