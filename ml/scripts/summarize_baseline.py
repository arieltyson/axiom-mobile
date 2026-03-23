#!/usr/bin/env python3

import json
import argparse
from pathlib import Path

# Default run directory
DEFAULT_RUN_DIR = Path("results/baselines/question_lookup_v0_seed0")


def load_run_result(run_dir: Path):
    path = run_dir / "run_result.json"

    if not path.exists():
        raise FileNotFoundError(f"Missing run_result.json in {run_dir}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Summarize baseline run results")
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=DEFAULT_RUN_DIR,
        help="Path to baseline run directory",
    )

    args = parser.parse_args()
    run_dir = args.run_dir

    # Check run directory exists
    if not run_dir.exists():
        raise FileNotFoundError(f"Run directory not found: {run_dir}")

    data = load_run_result(run_dir)

    # -------- Extract metadata --------
    run_id = data.get("run_id", "N/A")
    model_name = data["model"]["display_name"]

    splits = data["dataset"]["split_counts"]
    fingerprint = data["dataset"]["fingerprint"]["combined_sha256"][:12]

    notes = data.get("notes", "")

    # -------- Extract metrics --------
    metrics = data["metrics"]

    pool_em = metrics["pool"]["exact_match"]
    val_em = metrics["val"]["exact_match"]
    test_em = metrics["test"]["exact_match"]

    # -------- Print summary --------
    print("\n=== BASELINE SUMMARY ===\n")

    print(f"Run ID: {run_id}")
    print(f"Model: {model_name}")
    print(
        f"Dataset splits: pool={splits['pool']}, val={splits['val']}, test={splits['test']}"
    )
    print(f"Dataset fingerprint: {fingerprint}\n")

    print("Exact Match:")
    print(f"  pool: {pool_em:.3f}")
    print(f"  val : {val_em:.3f}")
    print(f"  test: {test_em:.3f}\n")

    print(f"Notes: {notes}\n")


if __name__ == "__main__":
    main()