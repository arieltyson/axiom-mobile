# Learning Curve Analysis — Phase 3

Last updated: 2026-04-12

## Overview

The learning-curve analysis layer aggregates per-run sweep results into strategy-level statistics and generates deterministic visual artifacts.  It reads a sweep `summary.json` (produced by `run_selection_sweep.py`), groups runs by `(strategy, budget)` across seeds, and outputs structured data plus SVG plots.

## Running the analysis

From the repository root:

```bash
python3 ml/scripts/generate_learning_curves.py \
    --sweep-dir results/selection_sweeps/sweep_v0
```

Custom output directory:

```bash
python3 ml/scripts/generate_learning_curves.py \
    --sweep-dir results/selection_sweeps/sweep_v0 \
    --output-dir results/selection_sweeps/analysis
```

If no `--output-dir` is given, artifacts are written to `<sweep-dir>/analysis/`.

## Output artifacts

| File | Description |
|------|-------------|
| `learning_curve_summary.json` | Structured aggregate: mean/min/max val\_em and test\_em per (strategy, budget), plus sweep metadata and skipped strategies |
| `learning_curve_summary.csv` | Flat table with one row per (strategy, budget) — importable in any spreadsheet tool |
| `learning_curve_val.svg` | Validation exact-match vs training budget, one line per strategy with min/max bands |
| `learning_curve_test.svg` | Test exact-match vs training budget, same format |

## SVG plot details

- **640 x 400 px**, white background, axis labels, grid lines.
- **Colorblind-friendly palette** (Tol bright): random `#4477AA`, uncertainty `#EE6677`, diversity `#228833`, kg\_guided `#CCBB44`.
- Each strategy is drawn as a mean polyline with dot markers, plus a translucent min/max band polygon.
- Generated with `xml.etree.ElementTree` — **no matplotlib or external dependencies**.
- Output is deterministic given the same `summary.json`.

## Interpreting current results

The current sweep uses the `question_lookup_v0` heuristic baseline over a small frozen split (`pool=37`, `val=5`, `test=10`).  Key observations:

1. **Validation EM is 0.0 for all strategies and budgets.**  The 5 val examples happen not to overlap with any memorized question→answer mapping, regardless of which pool subset is selected.
2. **Test EM is low (0–20%) and noisy.**  With only 10 test items and a lookup heuristic, small differences in selected subsets produce large per-seed variance.
3. **All strategies converge at budget=37** (full pool) — expected, since every strategy selects the same complete pool.
4. **kg\_guided is recorded as skipped** throughout the entire pipeline (sweep → summary → analysis → CSV/SVG).

These results validate the pipeline end-to-end.  They are **not** meaningful learning curves — that requires a real VLM and a larger dataset.

## Current limitations

1. **Small dataset**: 37 pool examples limits curve granularity and statistical power.
2. **Heuristic baseline**: `question_lookup_v0` memorizes exact question→answer strings; it does not learn visual features, so strategy differences are muted.
3. **No standard deviation**: with only 3 seeds, we report min/max bands rather than confidence intervals.
4. **KG-guided blocked**: requires KG v1 infrastructure (see `docs/TIMELINE.md` Phase 1).
5. **No matplotlib**: stdlib SVG generation is sufficient for the current pipeline validation stage; richer plots can be added when publication-quality figures are needed.

## Regenerating from scratch

To regenerate everything from a fresh sweep:

```bash
# 1. Run the selection sweep
python3 ml/scripts/run_selection_sweep.py \
    --output-dir results/selection_sweeps/sweep_v0

# 2. Generate learning-curve analysis
python3 ml/scripts/generate_learning_curves.py \
    --sweep-dir results/selection_sweeps/sweep_v0
```

Both scripts are deterministic given the same dataset manifests and seeds.
