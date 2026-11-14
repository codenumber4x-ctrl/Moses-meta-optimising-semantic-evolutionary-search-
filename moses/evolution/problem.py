"""What a problem must provide to be searched."""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Evaluation:
    """Result of scoring one program. Higher scores are better."""

    score: float
    feedback: str = ""  # short, human-readable; shown to the LLM in later prompts

    @property
    def valid(self) -> bool:
        return math.isfinite(self.score)

    @classmethod
    def failed(cls, reason: str) -> Evaluation:
        return cls(-math.inf, reason)


@dataclass(frozen=True)
class CaseResult:
    """Output (or error message) of the candidate function for one input."""

    output: Any = None
    error: str | None = None


class Problem(ABC):
    """A task solved by writing one Python function.

    The candidate program defines `entry_point`. It is called once per
    argument tuple from `cases()` in a separate process, and `score()`
    turns the results into an Evaluation.
    """

    name: str
    description: str  # the objective, in plain language, for the LLM
    entry_point: str  # name of the function the program must define
    seed_program: str  # a simple, working starting point
    timeout: float = 10.0  # seconds allowed for all cases together

    @abstractmethod
    def cases(self) -> list[tuple]:
        """Argument tuples for the entry point. Must be JSON-serialisable."""

    @abstractmethod
    def score(self, results: list[CaseResult]) -> Evaluation:
        """Score the results, which are in the same order as `cases()`."""
