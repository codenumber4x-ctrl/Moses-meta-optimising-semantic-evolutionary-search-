"""Population of scored programs, split into demes (sub-populations).

Each deme evolves on its own so several lines of solutions are explored at
once; the best programs periodically migrate to the next deme.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .problem import Evaluation


@dataclass(frozen=True)
class Program:
    source: str
    evaluation: Evaluation
    iteration: int  # 0 for the seed

    @property
    def score(self) -> float:
        return self.evaluation.score


class ProgramDatabase:
    def __init__(self, num_demes: int = 2, deme_size: int = 6, rng: random.Random | None = None):
        if num_demes < 1 or deme_size < 1:
            raise ValueError("num_demes and deme_size must be at least 1")
        self._demes: list[list[Program]] = [[] for _ in range(num_demes)]
        self._deme_size = deme_size
        self._seen: set[str] = set()
        self._next_deme = 0
        self._rng = rng or random.Random()

    def __contains__(self, source: str) -> bool:
        return _normalise(source) in self._seen

    @property
    def best(self) -> Program:
        return max((p for deme in self._demes for p in deme), key=lambda p: p.score)

    def add(self, program: Program, deme: int | None = None) -> None:
        """Add a valid program to one deme, or to every deme when `deme` is None."""
        if not program.evaluation.valid:
            raise ValueError("only valid programs are stored")
        self._seen.add(_normalise(program.source))
        for index in range(len(self._demes)) if deme is None else [deme]:
            self._insert(index, program)

    def sample(self, count: int) -> tuple[int, list[Program]]:
        """Pick the next deme (round robin) and up to `count` of its programs.

        The first pick is a tournament winner (fit but not always the best);
        the rest are random distinct members. Returned worst to best.
        """
        deme_index = self._next_deme
        self._next_deme = (self._next_deme + 1) % len(self._demes)
        deme = self._demes[deme_index]

        parent = max(self._rng.sample(deme, min(2, len(deme))), key=lambda p: p.score)
        others = [p for p in deme if p is not parent]
        chosen = [parent, *self._rng.sample(others, min(count - 1, len(others)))]
        return deme_index, sorted(chosen, key=lambda p: p.score)

    def migrate(self) -> None:
        """Copy each deme's best program into the next deme (ring topology)."""
        bests = [max(deme, key=lambda p: p.score) for deme in self._demes]
        for index, program in enumerate(bests):
            self._insert((index + 1) % len(self._demes), program)

    def _insert(self, index: int, program: Program) -> None:
        deme = self._demes[index]
        if any(p.source == program.source for p in deme):
            return
        deme.append(program)
        deme.sort(key=lambda p: p.score, reverse=True)
        del deme[self._deme_size :]


def _normalise(source: str) -> str:
    """Treat programs that differ only in blank lines or trailing spaces as duplicates."""
    return "\n".join(line.rstrip() for line in source.strip().splitlines() if line.strip())
