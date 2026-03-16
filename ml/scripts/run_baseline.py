#!/usr/bin/env python3
"""Run a lightweight reproducible baseline over the frozen dataset split."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ml" / "src"))

from axiom.data import dataset_fingerprint, load_all_splits  # noqa: E402
from axiom.eval import compute_exact_match_metrics, normalize_text  # noqa: E402
from axiom.models import instantiate_model, resolve_model_spec  # noqa: E402
from axiom.results import (  # noqa: E402
    BaselineRunResult,
    SplitMetrics,
    write_json,
    write_jsonl,
    write_run_result,
)


def _default_output_dir(repo_root: Path, model_id: str, seed: int) -> Path:
    return repo_root / "results" / "baselines" / f"{model_id}_seed{seed}"


def _prediction_rows(rows: list[dict[str, Any]], predictions: list[str]) -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []
    for row, predicted in zip(rows, predictions):
        payload.append(
            {
                "id": row["id"],
                "image_filename": row["image_filename"],
                "question": row["question"],
                "gold_answer": row["answer"],
                "predicted_answer": predicted,
                "is_correct": normalize_text(str(row["answer"]))
                == normalize_text(str(predicted)),
            }
        )
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model-id",
        default="question_lookup_v0",
        help="Model identifier from ml/configs/models/*.json",
    )
    parser.add_argument("--seed", type=int, default=0, help="Run seed for metadata only.")
    parser.add_argument(
        "--repo-root",
        default=str(ROOT),
        help="Repository root containing data/manifests/",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for result artifacts. Defaults to results/baselines/<model_id>_seed<seed>",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    output_dir = (
        Path(args.output_dir).resolve()
        if args.output_dir is not None
        else _default_output_dir(repo_root, args.model_id, args.seed)
    )

    splits = load_all_splits(repo_root=repo_root, validate=True)
    spec = resolve_model_spec(args.model_id)
    model = instantiate_model(args.model_id)
    training_summary = model.train(
        splits["pool"],
        val_rows=splits["val"],
        seed=args.seed,
    )

    metrics_by_split: dict[str, dict[str, Any]] = {}
    artifact_paths: dict[str, str] = {}

    for split_name, rows in splits.items():
        predictions = model.predict_many(rows)
        metric_payload = compute_exact_match_metrics(rows, predictions)
        split_metrics = SplitMetrics(split_name=split_name, **metric_payload)
        metrics_by_split[split_name] = split_metrics.to_dict()

        prediction_path = write_jsonl(
            output_dir / f"predictions_{split_name}.jsonl",
            _prediction_rows(rows, predictions),
        )
        artifact_paths[f"predictions_{split_name}"] = str(prediction_path.relative_to(repo_root))

    model_state_path = write_json(output_dir / "model_state.json", training_summary)
    artifact_paths["model_state"] = str(model_state_path.relative_to(repo_root))

    result = BaselineRunResult(
        run_id=f"{args.model_id}_seed{args.seed}",
        created_at_utc=datetime.now(timezone.utc).isoformat(),
        model=spec.to_dict(),
        dataset={
            "fingerprint": dataset_fingerprint(repo_root=repo_root),
            "split_counts": {name: len(rows) for name, rows in splits.items()},
        },
        training={
            "train_split": "pool",
            "validation_split": "val",
            "test_split": "test",
            "seed": args.seed,
            "num_train_examples": len(splits["pool"]),
            "summary": training_summary,
        },
        metrics=metrics_by_split,
        artifacts=artifact_paths,
        notes=(
            "question_lookup_v0 is a lightweight executable baseline for "
            "Phase 2 scaffolding. It is not a deployable multimodal model."
        ),
    )

    run_result_path = write_run_result(output_dir / "run_result.json", result)

    print("Baseline run completed.")
    print(f"model_id: {args.model_id}")
    print(f"output_dir: {output_dir}")
    print(f"result_json: {run_result_path}")
    for split_name in ("pool", "val", "test"):
        split_metrics = metrics_by_split[split_name]
        print(
            f"{split_name}: EM={split_metrics['exact_match']:.3f} "
            f"({split_metrics['num_correct']}/{split_metrics['num_examples']})"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
