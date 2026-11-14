"""Builds the LLM prompt and extracts the program from its reply."""

from __future__ import annotations

import re

from .database import Program
from .problem import Problem

SYSTEM_PROMPT = (
    "You improve Python programs inside an evolutionary search. "
    "Each program is scored automatically; your goal is a higher score. "
    "Reply with exactly one ```python code block containing the complete program."
)

_CODE_BLOCK = re.compile(r"```(?:python|py)?[ \t]*\n(.*?)```", re.DOTALL)


def build_prompt(problem: Problem, programs: list[Program]) -> str:
    """Describe the task and show previous programs, worst to best, with scores and feedback."""
    attempts = "\n\n".join(
        f"### Program {i} (score {p.score:.4g})\n"
        f"Feedback: {p.evaluation.feedback or 'none'}\n"
        f"```python\n{p.source.strip()}\n```"
        for i, p in enumerate(programs, start=1)
    )
    return (
        f"## Task\n{problem.description.strip()}\n\n"
        f"## Rules\n"
        f"- Define `{problem.entry_point}` with the same signature as below.\n"
        f"- Use only the Python standard library. Do not read files, use the network, or print.\n"
        f"- It must finish within {problem.timeout:g} seconds for all test inputs together.\n\n"
        f"## Previous programs (worst to best)\n{attempts}\n\n"
        f"## Your turn\n"
        f"Write an improved program that should score higher than Program {len(programs)}. "
        f"Learn from the feedback; try a different approach if scores have stalled. "
        f"Return the complete program in one ```python block."
    )


def extract_code(reply: str) -> str | None:
    """Return the last code block that defines a function, or None."""
    blocks = [b for b in _CODE_BLOCK.findall(reply) if "def " in b]
    if blocks:
        return blocks[-1].strip()
    return reply.strip() if reply.lstrip().startswith(("def ", "import ", "from ")) else None
