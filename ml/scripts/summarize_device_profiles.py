#!/usr/bin/env python3
"""Device-profile ingestion and metric-summary pipeline.

Scans results/device_profiles/ for valid session folders, parses
benchmark CSV + metadata JSON, optionally merges trace_metrics.json,
computes per-session and aggregate summaries, and writes reusable
analysis artifacts.

Usage:
    python3 ml/scripts/summarize_device_profiles.py
    python3 ml/scripts/summarize_device_profiles.py --profiles-dir results/device_profiles

Outputs written to results/device_profiles/analysis/:
    session_{session_id}.json   — per-session summary
    summary.json                — aggregate summary
    summary.csv                 — flat aggregate CSV
    summary.md                  — human-readable markdown report
"""

from __future__ import annotations

import csv
import json
import math
import sys
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any

# Resolve project root so imports work when run as a script
_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT / "ml" / "src"))

from axiom.results.device_profiles import (
    AggregateSummary,
    BenchmarkCSVRow,
    LatencyStats,
    SessionMetadata,
    SessionSummary,
    ThresholdEvaluation,
    TraceMetrics,
)

# ---------------------------------------------------------------------------
# Thresholds from SPEC.md / README.md
# ---------------------------------------------------------------------------

THRESHOLDS = {
    "latency_p50_ms": 400,
    "latency_p95_ms": 600,
    "peak_memory_mb": 500,
    "energy_battery_pct_per_hr": 5.0,
}


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------


def _parse_bool(raw: str) -> bool:
    return raw.strip().lower() in ("true", "1", "yes")


def parse_csv(csv_path: Path) -> list[BenchmarkCSVRow]:
    """Parse an app-exported benchmark CSV into typed rows."""
    text = csv_path.read_text(encoding="utf-8")
    reader = csv.DictReader(StringIO(text))
    rows: list[BenchmarkCSVRow] = []
    for raw in reader:
        rows.append(
            BenchmarkCSVRow(
                timestamp=raw["timestamp"],
                model_id=raw["model_id"],
                image_loaded=_parse_bool(raw["image_loaded"]),
                question_length=int(raw["question_length"]),
                latency_ms=int(raw["latency_ms"]),
                is_placeholder=_parse_bool(raw["is_placeholder"]),
                run_kind=raw["run_kind"],
                iteration_index=int(raw["iteration_index"]),
            )
        )
    return rows


def parse_metadata(meta_path: Path) -> SessionMetadata:
    """Parse an app-exported _meta.json into a typed struct."""
    raw = json.loads(meta_path.read_text(encoding="utf-8"))
    return SessionMetadata(
        session_id=raw["session_id"],
        export_timestamp=raw["export_timestamp"],
        device_name=raw["device_name"],
        device_model=raw["device_model"],
        system_name=raw["system_name"],
        system_version=raw["system_version"],
        app_version=raw["app_version"],
        app_build=raw["app_build"],
        model_id=raw["model_id"],
        is_placeholder=raw["is_placeholder"],
        benchmark_iterations=raw["benchmark_iterations"],
        record_count=raw["record_count"],
    )


def parse_trace_metrics(path: Path) -> TraceMetrics:
    """Parse an optional trace_metrics.json sidecar."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    return TraceMetrics(
        peak_memory_mb=raw.get("peak_memory_mb"),
        cpu_energy_level=raw.get("cpu_energy_level"),
        gpu_energy_level=raw.get("gpu_energy_level"),
        overhead_energy_level=raw.get("overhead_energy_level"),
        cpu_time_user_s=raw.get("cpu_time_user_s"),
        cpu_time_system_s=raw.get("cpu_time_system_s"),
        notes=raw.get("notes", ""),
    )


# ---------------------------------------------------------------------------
# Computation
# ---------------------------------------------------------------------------


def _percentile(sorted_values: list[int], pct: float) -> float:
    """Compute percentile using nearest-rank method."""
    if not sorted_values:
        return 0.0
    k = (pct / 100.0) * (len(sorted_values) - 1)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return float(sorted_values[f])
    return sorted_values[f] + (k - f) * (sorted_values[c] - sorted_values[f])


def compute_latency_stats(rows: list[BenchmarkCSVRow]) -> LatencyStats:
    """Compute latency statistics from benchmark CSV rows."""
    latencies = sorted(r.latency_ms for r in rows)
    if not latencies:
        return LatencyStats(count=0, min_ms=0, max_ms=0, mean_ms=0.0, p50_ms=0.0, p95_ms=0.0)

    return LatencyStats(
        count=len(latencies),
        min_ms=latencies[0],
        max_ms=latencies[-1],
        mean_ms=round(sum(latencies) / len(latencies), 1),
        p50_ms=round(_percentile(latencies, 50), 1),
        p95_ms=round(_percentile(latencies, 95), 1),
    )


def evaluate_thresholds(
    latency: LatencyStats,
    is_placeholder: bool,
    trace: TraceMetrics | None,
) -> list[ThresholdEvaluation]:
    """Evaluate effectiveness thresholds from SPEC.md honestly."""
    evals: list[ThresholdEvaluation] = []

    # --- Latency p50 ---
    if is_placeholder:
        evals.append(ThresholdEvaluation(
            metric_name="latency_p50",
            threshold=f"<= {THRESHOLDS['latency_p50_ms']} ms",
            measured_value=f"{latency.p50_ms} ms",
            status="placeholder",
            reason="Latency is simulated (PlaceholderInferenceService). Not valid for device-performance conclusions.",
        ))
    elif latency.count == 0:
        evals.append(ThresholdEvaluation(
            metric_name="latency_p50",
            threshold=f"<= {THRESHOLDS['latency_p50_ms']} ms",
            measured_value=None,
            status="unavailable",
            reason="No benchmark records found.",
        ))
    else:
        passed = latency.p50_ms <= THRESHOLDS["latency_p50_ms"]
        evals.append(ThresholdEvaluation(
            metric_name="latency_p50",
            threshold=f"<= {THRESHOLDS['latency_p50_ms']} ms",
            measured_value=f"{latency.p50_ms} ms",
            status="pass" if passed else "fail",
            reason=f"p50 latency {'meets' if passed else 'exceeds'} threshold.",
        ))

    # --- Latency p95 ---
    if is_placeholder:
        evals.append(ThresholdEvaluation(
            metric_name="latency_p95",
            threshold=f"<= {THRESHOLDS['latency_p95_ms']} ms",
            measured_value=f"{latency.p95_ms} ms",
            status="placeholder",
            reason="Latency is simulated (PlaceholderInferenceService). Not valid for device-performance conclusions.",
        ))
    elif latency.count == 0:
        evals.append(ThresholdEvaluation(
            metric_name="latency_p95",
            threshold=f"<= {THRESHOLDS['latency_p95_ms']} ms",
            measured_value=None,
            status="unavailable",
            reason="No benchmark records found.",
        ))
    else:
        passed = latency.p95_ms <= THRESHOLDS["latency_p95_ms"]
        evals.append(ThresholdEvaluation(
            metric_name="latency_p95",
            threshold=f"<= {THRESHOLDS['latency_p95_ms']} ms",
            measured_value=f"{latency.p95_ms} ms",
            status="pass" if passed else "fail",
            reason=f"p95 latency {'meets' if passed else 'exceeds'} threshold.",
        ))

    # --- Peak memory ---
    if trace and trace.peak_memory_mb is not None:
        passed = trace.peak_memory_mb < THRESHOLDS["peak_memory_mb"]
        evals.append(ThresholdEvaluation(
            metric_name="peak_memory",
            threshold=f"< {THRESHOLDS['peak_memory_mb']} MB",
            measured_value=f"{trace.peak_memory_mb} MB",
            status="pass" if passed else "fail",
            reason=f"Peak memory {'within' if passed else 'exceeds'} budget.",
        ))
    else:
        evals.append(ThresholdEvaluation(
            metric_name="peak_memory",
            threshold=f"< {THRESHOLDS['peak_memory_mb']} MB",
            measured_value=None,
            status="unavailable",
            reason="No trace_metrics.json with peak_memory_mb. Run Instruments Allocations template.",
        ))

    # --- Energy ---
    if trace and trace.cpu_energy_level is not None:
        evals.append(ThresholdEvaluation(
            metric_name="energy",
            threshold=f"< {THRESHOLDS['energy_battery_pct_per_hr']}% battery/hr",
            measured_value=f"CPU energy level: {trace.cpu_energy_level}/20",
            status="unavailable",
            reason=(
                "Instruments Energy Log reports relative levels (0-20 scale), "
                "not battery %/hr directly. Manual interpretation required. "
                "Energy level is recorded for reference."
            ),
        ))
    else:
        evals.append(ThresholdEvaluation(
            metric_name="energy",
            threshold=f"< {THRESHOLDS['energy_battery_pct_per_hr']}% battery/hr",
            measured_value=None,
            status="unavailable",
            reason="No trace_metrics.json with energy data. Run Instruments Energy Log on physical device.",
        ))

    # --- Quality (EM) — always unavailable from device profiles ---
    evals.append(ThresholdEvaluation(
        metric_name="exact_match",
        threshold=">= 70% EM",
        measured_value=None,
        status="unavailable",
        reason=(
            "Quality metrics (EM, BLEU, hallucination rate) are not captured in "
            "device benchmark sessions. These require offline evaluation against "
            "ground-truth labels from data/manifests/."
        ),
    ))

    # --- Model size — always unavailable from device profiles ---
    evals.append(ThresholdEvaluation(
        metric_name="model_size",
        threshold="< 100 MB",
        measured_value=None,
        status="unavailable",
        reason=(
            "Model size is not captured in device benchmark sessions. "
            "Requires measuring .mlpackage size after Core ML conversion (Phase 4)."
        ),
    ))

    return evals


# ---------------------------------------------------------------------------
# Session discovery and summarization
# ---------------------------------------------------------------------------


def discover_sessions(profiles_dir: Path) -> list[Path]:
    """Find valid session directories under profiles_dir.

    A valid session directory contains at least one *_meta.json file
    and at least one .csv file.
    """
    if not profiles_dir.is_dir():
        return []

    sessions: list[Path] = []
    for child in sorted(profiles_dir.iterdir()):
        if not child.is_dir():
            continue
        # Skip the analysis output directory
        if child.name == "analysis":
            continue
        # Skip fixture directories at the top level — they live under _fixtures/
        if child.name.startswith("_"):
            continue

        has_csv = any(child.glob("*.csv"))
        has_meta = any(child.glob("*_meta.json"))
        if has_csv and has_meta:
            sessions.append(child)

    return sessions


def summarize_session(session_dir: Path) -> SessionSummary:
    """Produce a complete summary for one device-profiling session."""
    warnings: list[str] = []

    # Find required files
    csv_files = sorted(session_dir.glob("*.csv"))
    meta_files = sorted(session_dir.glob("*_meta.json"))

    if not csv_files:
        raise FileNotFoundError(f"No CSV file in {session_dir}")
    if not meta_files:
        raise FileNotFoundError(f"No _meta.json file in {session_dir}")

    if len(csv_files) > 1:
        warnings.append(f"Multiple CSV files found; using {csv_files[0].name}")
    if len(meta_files) > 1:
        warnings.append(f"Multiple _meta.json files found; using {meta_files[0].name}")

    csv_path = csv_files[0]
    meta_path = meta_files[0]

    # Parse
    rows = parse_csv(csv_path)
    metadata = parse_metadata(meta_path)

    # Validate record count
    if metadata.record_count != len(rows):
        warnings.append(
            f"Metadata claims {metadata.record_count} records but CSV has {len(rows)}."
        )

    # Compute stats
    benchmark_rows = [r for r in rows if r.run_kind == "benchmark"]
    single_rows = [r for r in rows if r.run_kind == "single"]

    # Use all rows for latency stats (both single and benchmark are real measurements)
    latency = compute_latency_stats(rows)

    # Optional trace metrics
    trace: TraceMetrics | None = None
    trace_path = session_dir / "trace_metrics.json"
    if trace_path.exists():
        trace = parse_trace_metrics(trace_path)

    # Threshold evaluation
    thresholds = evaluate_thresholds(latency, metadata.is_placeholder, trace)

    return SessionSummary(
        session_id=metadata.session_id,
        session_dir=session_dir.name,
        export_timestamp=metadata.export_timestamp,
        device_name=metadata.device_name,
        device_model=metadata.device_model,
        system_version=metadata.system_version,
        app_version=metadata.app_version,
        app_build=metadata.app_build,
        model_id=metadata.model_id,
        is_placeholder=metadata.is_placeholder,
        total_records=len(rows),
        benchmark_records=len(benchmark_rows),
        single_records=len(single_rows),
        latency=latency,
        trace_metrics=trace.to_dict() if trace else {},
        has_trace_metrics=trace is not None,
        thresholds=[t.to_dict() for t in thresholds],
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------


def build_aggregate(summaries: list[SessionSummary]) -> AggregateSummary:
    """Build an aggregate summary across all sessions."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    models = sorted(set(s.model_id for s in summaries))
    devices = sorted(set(f"{s.device_model} ({s.system_version})" for s in summaries))
    placeholder_count = sum(1 for s in summaries if s.is_placeholder)
    real_count = len(summaries) - placeholder_count

    notes: list[str] = []
    if placeholder_count > 0 and real_count == 0:
        notes.append(
            "All sessions use placeholder inference. "
            "These results validate the instrumentation pipeline but are "
            "not publishable device-performance data."
        )
    elif placeholder_count > 0:
        notes.append(
            f"{placeholder_count} of {len(summaries)} sessions use placeholder inference."
        )

    return AggregateSummary(
        created_at_utc=now,
        session_count=len(summaries),
        sessions=[s.to_dict() for s in summaries],
        models_seen=models,
        devices_seen=devices,
        placeholder_session_count=placeholder_count,
        real_session_count=real_count,
        overall_notes=notes,
    )


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------


def write_json_file(path: Path, data: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return path


def write_aggregate_csv(path: Path, summaries: list[SessionSummary]) -> Path:
    """Write a flat CSV of per-session metrics for easy consumption."""
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "session_id",
        "session_dir",
        "export_timestamp",
        "device_model",
        "system_version",
        "model_id",
        "is_placeholder",
        "total_records",
        "benchmark_records",
        "latency_min_ms",
        "latency_max_ms",
        "latency_mean_ms",
        "latency_p50_ms",
        "latency_p95_ms",
        "peak_memory_mb",
        "has_trace_metrics",
    ]

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in summaries:
            writer.writerow({
                "session_id": s.session_id,
                "session_dir": s.session_dir,
                "export_timestamp": s.export_timestamp,
                "device_model": s.device_model,
                "system_version": s.system_version,
                "model_id": s.model_id,
                "is_placeholder": s.is_placeholder,
                "total_records": s.total_records,
                "benchmark_records": s.benchmark_records,
                "latency_min_ms": s.latency.min_ms,
                "latency_max_ms": s.latency.max_ms,
                "latency_mean_ms": s.latency.mean_ms,
                "latency_p50_ms": s.latency.p50_ms,
                "latency_p95_ms": s.latency.p95_ms,
                "peak_memory_mb": s.trace_metrics.get("peak_memory_mb", ""),
                "has_trace_metrics": s.has_trace_metrics,
            })

    return path


def write_markdown_report(path: Path, summaries: list[SessionSummary], aggregate: AggregateSummary) -> Path:
    """Write a human-readable markdown summary report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []

    lines.append("# Device Profile Summary Report")
    lines.append("")
    lines.append(f"Generated: {aggregate.created_at_utc}")
    lines.append(f"Sessions: {aggregate.session_count}")
    lines.append(f"Models: {', '.join(aggregate.models_seen) or 'none'}")
    lines.append(f"Devices: {', '.join(aggregate.devices_seen) or 'none'}")
    lines.append(f"Placeholder sessions: {aggregate.placeholder_session_count}")
    lines.append(f"Real sessions: {aggregate.real_session_count}")
    lines.append("")

    if aggregate.overall_notes:
        lines.append("## Notes")
        lines.append("")
        for note in aggregate.overall_notes:
            lines.append(f"- {note}")
        lines.append("")

    for s in summaries:
        lines.append(f"## {s.session_dir}")
        lines.append("")
        lines.append(f"- **Model:** {s.model_id}")
        lines.append(f"- **Device:** {s.device_model} ({s.system_version})")
        lines.append(f"- **Placeholder:** {'Yes' if s.is_placeholder else 'No'}")
        lines.append(f"- **Records:** {s.total_records} total ({s.benchmark_records} benchmark, {s.single_records} single)")
        lines.append(f"- **Latency:** min={s.latency.min_ms}ms, mean={s.latency.mean_ms}ms, p50={s.latency.p50_ms}ms, p95={s.latency.p95_ms}ms, max={s.latency.max_ms}ms")

        if s.has_trace_metrics:
            tm = s.trace_metrics
            if "peak_memory_mb" in tm:
                lines.append(f"- **Peak Memory:** {tm['peak_memory_mb']} MB")
            if "cpu_energy_level" in tm:
                lines.append(f"- **CPU Energy Level:** {tm['cpu_energy_level']}/20")

        lines.append("")
        lines.append("### Threshold Evaluation")
        lines.append("")
        lines.append("| Metric | Threshold | Measured | Status | Reason |")
        lines.append("|--------|-----------|----------|--------|--------|")
        for t in s.thresholds:
            measured = t.get("measured_value") or "—"
            lines.append(f"| {t['metric_name']} | {t['threshold']} | {measured} | **{t['status']}** | {t['reason']} |")
        lines.append("")

        if s.warnings:
            lines.append("### Warnings")
            lines.append("")
            for w in s.warnings:
                lines.append(f"- {w}")
            lines.append("")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Summarize device profiling sessions from results/device_profiles/",
    )
    parser.add_argument(
        "--profiles-dir",
        type=Path,
        default=_PROJECT_ROOT / "results" / "device_profiles",
        help="Root directory containing session folders (default: results/device_profiles/)",
    )
    args = parser.parse_args()

    profiles_dir: Path = args.profiles_dir.resolve()
    analysis_dir = profiles_dir / "analysis"

    print(f"Scanning: {profiles_dir}")

    sessions = discover_sessions(profiles_dir)
    if not sessions:
        print("No valid session folders found.")
        print("Expected: directories containing at least one *.csv and one *_meta.json")
        sys.exit(0)

    print(f"Found {len(sessions)} session(s): {[s.name for s in sessions]}")

    summaries: list[SessionSummary] = []
    for session_dir in sessions:
        try:
            summary = summarize_session(session_dir)
            summaries.append(summary)
            print(f"  {session_dir.name}: {summary.total_records} records, "
                  f"p50={summary.latency.p50_ms}ms, "
                  f"placeholder={summary.is_placeholder}")
        except Exception as exc:
            print(f"  {session_dir.name}: ERROR — {exc}", file=sys.stderr)

    if not summaries:
        print("No sessions could be summarized.")
        sys.exit(1)

    # Write per-session summaries
    for s in summaries:
        out = write_json_file(
            analysis_dir / f"session_{s.session_id}.json",
            s.to_dict(),
        )
        print(f"  Wrote: {out.relative_to(_PROJECT_ROOT)}")

    # Write aggregate
    aggregate = build_aggregate(summaries)

    agg_json = write_json_file(analysis_dir / "summary.json", aggregate.to_dict())
    print(f"  Wrote: {agg_json.relative_to(_PROJECT_ROOT)}")

    agg_csv = write_aggregate_csv(analysis_dir / "summary.csv", summaries)
    print(f"  Wrote: {agg_csv.relative_to(_PROJECT_ROOT)}")

    agg_md = write_markdown_report(analysis_dir / "summary.md", summaries, aggregate)
    print(f"  Wrote: {agg_md.relative_to(_PROJECT_ROOT)}")

    print(f"\nDone. {len(summaries)} session(s) summarized in {analysis_dir.relative_to(_PROJECT_ROOT)}/")


if __name__ == "__main__":
    main()
