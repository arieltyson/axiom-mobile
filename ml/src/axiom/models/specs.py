"""Structured model specifications loaded from config files."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ModelSpec:
    model_id: str
    display_name: str
    family: str
    backend: str
    stage: str
    description: str
    source: str
    notes: str = ""
    executable: bool = False
    coreml_ready: bool = False
    params_millions: float | None = None
    expected_app_footprint_mb: float | None = None
    quantization: str | None = None
    priority_rank: int = 0
    supported_capabilities: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ModelSpec":
        return cls(
            model_id=str(payload["model_id"]),
            display_name=str(payload["display_name"]),
            family=str(payload["family"]),
            backend=str(payload["backend"]),
            stage=str(payload["stage"]),
            description=str(payload["description"]),
            source=str(payload["source"]),
            notes=str(payload.get("notes", "")),
            executable=bool(payload.get("executable", False)),
            coreml_ready=bool(payload.get("coreml_ready", False)),
            params_millions=(
                float(payload["params_millions"])
                if payload.get("params_millions") is not None
                else None
            ),
            expected_app_footprint_mb=(
                float(payload["expected_app_footprint_mb"])
                if payload.get("expected_app_footprint_mb") is not None
                else None
            ),
            quantization=(
                str(payload["quantization"])
                if payload.get("quantization") is not None
                else None
            ),
            priority_rank=int(payload.get("priority_rank", 0)),
            supported_capabilities=tuple(payload.get("supported_capabilities", [])),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "display_name": self.display_name,
            "family": self.family,
            "backend": self.backend,
            "stage": self.stage,
            "description": self.description,
            "source": self.source,
            "notes": self.notes,
            "executable": self.executable,
            "coreml_ready": self.coreml_ready,
            "params_millions": self.params_millions,
            "expected_app_footprint_mb": self.expected_app_footprint_mb,
            "quantization": self.quantization,
            "priority_rank": self.priority_rank,
            "supported_capabilities": list(self.supported_capabilities),
        }
