#!/usr/bin/env python3
"""Generate learning-curve analysis artifacts from a selection sweep.

Reads a sweep ``summary.json``, aggregates per-strategy metrics across
seeds, and writes:

- ``learning_curve_summary.json``  — structured aggregate data
- ``learning_curve_summary.csv``   — flat table for spreadsheets
- ``learning_curve_val.svg``       — validation EM vs budget plot
- ``learning_curve_test.svg``      — test EM vs budget plot

All output is deterministic and stdlib-only (no matplotlib).

Example
-------
    python3 ml/scripts/generate_learning_curves.py \\
        --sweep-dir results/selection_sweeps/sweep_v0

    python3 ml/scripts/generate_learning_curves.py \\
        --sweep-dir results/selection_sweeps/sweep_v0 \\
        --output-dir results/selection_sweeps/analysis
"""

from __future__ import annotations

import argparse
import csv
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

# ── Colorblind-friendly palette (Tol bright) ────────────────────────
STRATEGY_COLORS: dict[str, str] = {
    "random": "#4477AA",
    "uncertainty": "#EE6677",
    "diversity": "#228833",
    "kg_guided": "#CCBB44",
}
STRATEGY_ORDER = ["random", "uncertainty", "diversity", "kg_guided"]


# ── Aggregation ─────────────────────────────────────────────────────

def _aggregate(
    runs: list[dict[str, Any]],
    skipped: list[dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Group completed runs by (strategy, budget), compute statistics."""
    buckets: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for r in runs:
        key = (r["strategy"], r["budget"])
        buckets.setdefault(key, []).append(r)

    rows: list[dict[str, Any]] = []
    for (strategy, budget), group in sorted(buckets.items()):
        val_scores = [r["val_em"] for r in group]
        test_scores = [r["test_em"] for r in group]
        n = len(group)
        rows.append(
            {
                "strategy": strategy,
                "budget": budget,
                "num_seeds": n,
                "val_em_mean": sum(val_scores) / n,
                "val_em_min": min(val_scores),
                "val_em_max": max(val_scores),
                "test_em_mean": sum(test_scores) / n,
                "test_em_min": min(test_scores),
                "test_em_max": max(test_scores),
                "status": "completed",
            }
        )

    skipped_rows: list[dict[str, str]] = []
    for s in skipped:
        skipped_rows.append(
            {"strategy": s["strategy"], "reason": s["reason"], "status": "skipped"}
        )

    return rows, skipped_rows


# ── SVG chart generation (stdlib-only) ──────────────────────────────

_SVG_NS = "http://www.w3.org/2000/svg"
_W, _H = 640, 400
_ML, _MR, _MT, _MB = 65, 25, 35, 55  # margins


def _make_chart(
    rows: list[dict[str, Any]],
    metric_key: str,
    title: str,
    y_label: str,
) -> str:
    """Render a learning-curve SVG for one metric."""
    # Group by strategy.
    by_strategy: dict[str, list[dict[str, Any]]] = {}
    for r in rows:
        by_strategy.setdefault(r["strategy"], []).append(r)

    # Determine axis ranges.
    budgets = sorted({r["budget"] for r in rows})
    all_vals: list[float] = []
    for r in rows:
        all_vals.extend([r[f"{metric_key}_min"], r[f"{metric_key}_max"]])
    y_min_data = min(all_vals) if all_vals else 0.0
    y_max_data = max(all_vals) if all_vals else 1.0
    # Pad Y axis.
    y_range = max(y_max_data - y_min_data, 0.05)
    y_lo = max(0.0, y_min_data - y_range * 0.15)
    y_hi = min(1.0, y_max_data + y_range * 0.25)
    if y_hi - y_lo < 0.1:
        y_hi = min(1.0, y_lo + 0.1)

    plot_w = _W - _ML - _MR
    plot_h = _H - _MT - _MB

    def x_pos(budget: int) -> float:
        idx = budgets.index(budget)
        return _ML + (idx / max(len(budgets) - 1, 1)) * plot_w

    def y_pos(val: float) -> float:
        if y_hi == y_lo:
            return _MT + plot_h / 2
        return _MT + (1.0 - (val - y_lo) / (y_hi - y_lo)) * plot_h

    ET.register_namespace("", _SVG_NS)
    svg = ET.Element("svg", xmlns=_SVG_NS, width=str(_W), height=str(_H))

    # White background.
    ET.SubElement(svg, "rect", width=str(_W), height=str(_H), fill="white")

    # Title.
    t = ET.SubElement(
        svg, "text",
        x=str(_W // 2), y=str(_MT - 12),
        fill="#333333",
    )
    t.set("text-anchor", "middle")
    t.set("font-family", "system-ui, -apple-system, Helvetica, Arial, sans-serif")
    t.set("font-size", "14")
    t.set("font-weight", "600")
    t.text = title

    # Y-axis label.
    yl = ET.SubElement(svg, "text", x="0", y="0", fill="#555555")
    yl.set("text-anchor", "middle")
    yl.set("font-family", "system-ui, -apple-system, Helvetica, Arial, sans-serif")
    yl.set("font-size", "11")
    yl.set("transform", f"translate(16, {_MT + plot_h // 2}) rotate(-90)")
    yl.text = y_label

    # X-axis label.
    xl = ET.SubElement(
        svg, "text",
        x=str(_ML + plot_w // 2), y=str(_H - 8),
        fill="#555555",
    )
    xl.set("text-anchor", "middle")
    xl.set("font-family", "system-ui, -apple-system, Helvetica, Arial, sans-serif")
    xl.set("font-size", "11")
    xl.text = "Training budget (examples)"

    # Grid lines and Y tick labels.
    num_y_ticks = 5
    for i in range(num_y_ticks + 1):
        frac = i / num_y_ticks
        val = y_lo + frac * (y_hi - y_lo)
        yp = y_pos(val)
        ET.SubElement(
            svg, "line",
            x1=str(_ML), y1=f"{yp:.1f}",
            x2=str(_ML + plot_w), y2=f"{yp:.1f}",
            stroke="#EEEEEE",
        )
        tick = ET.SubElement(
            svg, "text",
            x=str(_ML - 8), y=f"{yp + 4:.1f}",
            fill="#777777",
        )
        tick.set("text-anchor", "end")
        tick.set("font-family", "system-ui, -apple-system, Helvetica, Arial, sans-serif")
        tick.set("font-size", "10")
        tick.text = f"{val:.2f}"

    # X tick labels.
    for b in budgets:
        xp = x_pos(b)
        tick = ET.SubElement(
            svg, "text",
            x=f"{xp:.1f}", y=str(_MT + plot_h + 18),
            fill="#777777",
        )
        tick.set("text-anchor", "middle")
        tick.set("font-family", "system-ui, -apple-system, Helvetica, Arial, sans-serif")
        tick.set("font-size", "10")
        tick.text = str(b)

    # Axis border.
    ET.SubElement(
        svg, "rect",
        x=str(_ML), y=str(_MT),
        width=str(plot_w), height=str(plot_h),
        fill="none", stroke="#CCCCCC",
    )

    # Draw series.
    for strategy in STRATEGY_ORDER:
        if strategy not in by_strategy:
            continue
        color = STRATEGY_COLORS.get(strategy, "#999999")
        data = sorted(by_strategy[strategy], key=lambda r: r["budget"])

        # Min/max band.
        band_points_top = [
            f"{x_pos(r['budget']):.1f},{y_pos(r[f'{metric_key}_max']):.1f}"
            for r in data
        ]
        band_points_bot = [
            f"{x_pos(r['budget']):.1f},{y_pos(r[f'{metric_key}_min']):.1f}"
            for r in reversed(data)
        ]
        band_poly = ET.SubElement(
            svg, "polygon",
            points=" ".join(band_points_top + band_points_bot),
            fill=color, opacity="0.12",
        )

        # Mean line.
        mean_points = " ".join(
            f"{x_pos(r['budget']):.1f},{y_pos(r[f'{metric_key}_mean']):.1f}"
            for r in data
        )
        ET.SubElement(
            svg, "polyline",
            points=mean_points,
            fill="none", stroke=color,
        ).set("stroke-width", "2")

        # Data point dots.
        for r in data:
            ET.SubElement(
                svg, "circle",
                cx=f"{x_pos(r['budget']):.1f}",
                cy=f"{y_pos(r[f'{metric_key}_mean']):.1f}",
                r="3.5",
                fill=color,
            )

    # Legend.
    legend_x = _ML + 12
    legend_y = _MT + 12
    for i, strategy in enumerate(STRATEGY_ORDER):
        if strategy not in by_strategy:
            continue
        color = STRATEGY_COLORS.get(strategy, "#999999")
        ly = legend_y + i * 18
        ET.SubElement(
            svg, "rect",
            x=str(legend_x), y=str(ly - 5),
            width="12", height="12",
            fill=color, rx="2",
        )
        lt = ET.SubElement(
            svg, "text",
            x=str(legend_x + 18), y=str(ly + 5),
            fill="#333333",
        )
        lt.set("font-family", "system-ui, -apple-system, Helvetica, Arial, sans-serif")
        lt.set("font-size", "11")
        lt.text = strategy

    return ET.tostring(svg, encoding="unicode", xml_declaration=True)


# ── CLI and main ────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--sweep-dir",
        required=True,
        help="Directory containing summary.json from a selection sweep",
    )
    p.add_argument(
        "--output-dir",
        default=None,
        help="Output directory (default: <sweep-dir>/analysis)",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    sweep_dir = Path(args.sweep_dir).resolve()
    summary_path = sweep_dir / "summary.json"

    if not summary_path.exists():
        print(f"ERROR: {summary_path} not found")
        return 1

    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    output_dir = (
        Path(args.output_dir).resolve()
        if args.output_dir
        else sweep_dir / "analysis"
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    # Aggregate.
    agg_rows, skipped_rows = _aggregate(
        summary["runs"],
        summary.get("strategies_skipped", []),
    )

    # ── Write learning_curve_summary.json ───────────────────────────
    lc_summary: dict[str, Any] = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "sweep_source": str(summary_path),
        "model_id": summary["config"]["model_id"],
        "dataset": summary["dataset"],
        "strategies_executed": summary["strategies_executed"],
        "strategies_skipped": skipped_rows,
        "curves": agg_rows,
    }
    lc_json_path = output_dir / "learning_curve_summary.json"
    lc_json_path.write_text(
        json.dumps(lc_summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    # ── Write learning_curve_summary.csv ────────────────────────────
    csv_path = output_dir / "learning_curve_summary.csv"
    fieldnames = [
        "strategy", "budget", "num_seeds", "status",
        "val_em_mean", "val_em_min", "val_em_max",
        "test_em_mean", "test_em_min", "test_em_max",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        for r in agg_rows:
            w.writerow(
                {k: f"{v:.4f}" if isinstance(v, float) else v for k, v in r.items()}
            )
        for s in skipped_rows:
            w.writerow({"strategy": s["strategy"], "status": s["status"]})

    # ── Generate SVG plots ──────────────────────────────────────────
    val_svg = _make_chart(
        agg_rows,
        metric_key="val_em",
        title="Learning Curve — Validation Exact Match",
        y_label="Exact Match (val)",
    )
    val_path = output_dir / "learning_curve_val.svg"
    val_path.write_text(val_svg, encoding="utf-8")

    test_svg = _make_chart(
        agg_rows,
        metric_key="test_em",
        title="Learning Curve — Test Exact Match",
        y_label="Exact Match (test)",
    )
    test_path = output_dir / "learning_curve_test.svg"
    test_path.write_text(test_svg, encoding="utf-8")

    print("Learning curve analysis complete.")
    print(f"  Summary JSON: {lc_json_path}")
    print(f"  Summary CSV:  {csv_path}")
    print(f"  Val plot:     {val_path}")
    print(f"  Test plot:    {test_path}")
    print(f"  Strategies:   {summary['strategies_executed']}")
    print(f"  Skipped:      {[s['strategy'] for s in skipped_rows]}")
    print(f"  Budgets:      {sorted({r['budget'] for r in agg_rows})}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
