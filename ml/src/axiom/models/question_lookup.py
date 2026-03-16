"""Executable lightweight baseline for Phase 2 scaffolding."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Sequence
from typing import Any

from axiom.eval import normalize_text

from .base import ReasoningModel


class QuestionLookupBaseline(ReasoningModel):
    """Memorize the most common answer per normalized question."""

    def __init__(self, spec) -> None:
        super().__init__(spec)
        self._question_to_answer: dict[str, str] = {}
        self._default_answer: str = ""
        self._is_trained = False

    def train(
        self,
        train_rows: Sequence[dict[str, Any]],
        *,
        val_rows: Sequence[dict[str, Any]] | None = None,
        seed: int = 0,
    ) -> dict[str, Any]:
        del val_rows
        del seed

        grouped_answers: dict[str, list[str]] = defaultdict(list)
        answer_counts: Counter[str] = Counter()

        for row in train_rows:
            question = normalize_text(str(row["question"]))
            answer = str(row["answer"]).strip()
            grouped_answers[question].append(answer)
            answer_counts[answer] += 1

        if not answer_counts:
            raise ValueError("Cannot train question-lookup baseline on an empty split.")

        self._question_to_answer = {
            question: Counter(answers).most_common(1)[0][0]
            for question, answers in grouped_answers.items()
        }
        self._default_answer = answer_counts.most_common(1)[0][0]
        self._is_trained = True

        return {
            "train_examples": len(train_rows),
            "unique_questions": len(self._question_to_answer),
            "unique_answers": len(answer_counts),
            "default_answer": self._default_answer,
        }

    def predict_one(self, row: dict[str, Any]) -> str:
        if not self._is_trained:
            raise RuntimeError("QuestionLookupBaseline.predict_one() called before train().")

        question = normalize_text(str(row["question"]))
        return self._question_to_answer.get(question, self._default_answer)
