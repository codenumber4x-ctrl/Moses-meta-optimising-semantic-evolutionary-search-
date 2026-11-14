"""The evolutionary loop: sample programs, ask the LLM for a better one, score it, keep the best."""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field

from ..llm import LLMClient, LLMError
from .database import Program, ProgramDatabase
from .evaluator import evaluate
from .problem import Evaluation, Problem
from .prompts import SYSTEM_PROMPT, build_prompt, extract_code

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class EvolutionConfig:
    iterations: int = 10  # one LLM call per iteration
    num_demes: int = 2
    deme_size: int = 6
    programs_per_prompt: int = 3
    migration_interval: int = 5  # iterations between migrations
    max_consecutive_llm_failures: int = 3
    seed: int | None = None  # makes sampling reproducible (LLM replies are not)


@dataclass
class RunResult:
    best: Program
    history: list[Program] = field(default_factory=list)  # every candidate, in order
    llm_failures: int = 0


class Evolver:
    def __init__(self, problem: Problem, llm: LLMClient, config: EvolutionConfig | None = None):
        self.problem = problem
        self.llm = llm
        self.config = config or EvolutionConfig()

    def run(self) -> RunResult:
        cfg = self.config
        database = ProgramDatabase(cfg.num_demes, cfg.deme_size, random.Random(cfg.seed))

        seed = Program(self.problem.seed_program, evaluate(self.problem, self.problem.seed_program), 0)
        if not seed.evaluation.valid:
            raise ValueError(f"Seed program for {self.problem.name} is invalid: {seed.evaluation.feedback}")
        database.add(seed)
        result = RunResult(best=seed, history=[seed])
        log.info("seed score %.4g | %s", seed.score, seed.evaluation.feedback)

        consecutive_failures = 0
        for iteration in range(1, cfg.iterations + 1):
            deme, parents = database.sample(cfg.programs_per_prompt)
            try:
                reply = self.llm.complete(build_prompt(self.problem, parents), SYSTEM_PROMPT)
            except LLMError as exc:
                result.llm_failures += 1
                consecutive_failures += 1
                log.warning("iteration %d: LLM call failed: %s", iteration, exc)
                if consecutive_failures >= cfg.max_consecutive_llm_failures:
                    log.error("stopping after %d consecutive LLM failures", consecutive_failures)
                    break
                continue
            consecutive_failures = 0

            source = extract_code(reply)
            if source is not None and source in database:
                log.info("iteration %d: duplicate program, skipped", iteration)
                continue
            evaluation = evaluate(self.problem, source) if source else Evaluation.failed("no code block in reply")

            program = Program(source or reply, evaluation, iteration)
            result.history.append(program)
            if evaluation.valid:
                database.add(program, deme)
            result.best = database.best
            log.info(
                "iteration %d: deme %d score %.4g (best %.4g) | %s",
                iteration, deme, evaluation.score, result.best.score, evaluation.feedback,
            )

            if iteration % cfg.migration_interval == 0:
                database.migrate()

        return result
