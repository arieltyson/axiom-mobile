"""Typed result schema for baseline experiment runs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class SplitMetrics:
    split_name: str
    num_examples: int
    num_correct: int
    exact_match: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BaselineRunResult:
    run_id: str
    created_at_utc: str
    model: dict[str, Any]
    dataset: dict[str, Any]
    training: dict[str, Any]
    metrics: dict[str, dict[str, Any]]
    artifacts: dict[str, str]
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
