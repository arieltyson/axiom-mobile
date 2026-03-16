"""Offline evaluation metrics for lightweight baselines."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any


def normalize_text(text: str) -> str:
    return " ".join(text.strip().lower().split())


def normalize_answer_text(text: str) -> str:
    return normalize_text(text)


def compute_exact_match_metrics(
    rows: Sequence[dict[str, Any]],
    predictions: Sequence[str],
) -> dict[str, Any]:
    if len(rows) != len(predictions):
        raise ValueError(
            "Prediction length mismatch: "
            f"expected {len(rows)} predictions, got {len(predictions)}"
        )

    correct = 0
    for row, predicted in zip(rows, predictions):
        gold = normalize_text(str(row["answer"]))
        guess = normalize_text(str(predicted))
        if gold == guess:
            correct += 1

    total = len(rows)
    exact_match = correct / total if total else 0.0
    return {
        "num_examples": total,
        "num_correct": correct,
        "exact_match": exact_match,
    }
