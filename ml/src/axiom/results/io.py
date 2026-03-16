"""Helpers for writing baseline run artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .schema import BaselineRunResult


def write_json(path: str | Path, payload: dict[str, Any]) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return output_path


def write_jsonl(path: str | Path, rows: list[dict[str, Any]]) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    return output_path


def write_run_result(path: str | Path, result: BaselineRunResult) -> Path:
    return write_json(path, result.to_dict())
