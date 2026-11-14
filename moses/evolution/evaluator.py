"""Scores candidate programs by running them in a separate Python process.

This isolates crashes, infinite loops and stray output from the search, but it
is not a security sandbox: run untrusted model output inside a container or VM.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from .problem import CaseResult, Evaluation, Problem

_RUNNER = Path(__file__).with_name("_runner.py")


def evaluate(problem: Problem, source: str) -> Evaluation:
    """Run `source` on the problem's cases and score it."""
    request = json.dumps({"source": source, "entry_point": problem.entry_point, "cases": problem.cases()})
    try:
        completed = subprocess.run(
            [sys.executable, "-I", str(_RUNNER)],
            input=request,
            capture_output=True,
            text=True,
            timeout=problem.timeout,
        )
    except subprocess.TimeoutExpired:
        return Evaluation.failed(f"timed out after {problem.timeout:g}s")

    try:
        reply = json.loads(completed.stdout)
    except json.JSONDecodeError:
        stderr = completed.stderr.strip().splitlines()
        return Evaluation.failed(f"program crashed: {stderr[-1] if stderr else 'no output'}")

    if "error" in reply:
        return Evaluation.failed(reply["error"])
    return problem.score([CaseResult(r.get("output"), r.get("error")) for r in reply["results"]])
