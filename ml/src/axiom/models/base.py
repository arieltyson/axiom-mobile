"""Abstract interfaces for runnable reasoning models."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from .specs import ModelSpec


class ReasoningModel(ABC):
    """Minimal interface shared by executable offline baselines."""

    def __init__(self, spec: ModelSpec) -> None:
        self.spec = spec

    @abstractmethod
    def train(
        self,
        train_rows: Sequence[dict[str, Any]],
        *,
        val_rows: Sequence[dict[str, Any]] | None = None,
        seed: int = 0,
    ) -> dict[str, Any]:
        """Fit or initialize the model from training rows."""

    @abstractmethod
    def predict_one(self, row: dict[str, Any]) -> str:
        """Predict a short answer for one dataset row."""

    def predict_many(self, rows: Sequence[dict[str, Any]]) -> list[str]:
        return [self.predict_one(row) for row in rows]

    def export_coreml(self, output_dir: str) -> dict[str, Any]:
        raise NotImplementedError(
            f"Model '{self.spec.model_id}' does not implement Core ML export yet."
        )
