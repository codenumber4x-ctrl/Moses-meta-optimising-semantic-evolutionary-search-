"""The evolutionary loop, driven by a scripted stand-in for the LLM (no network)."""

import pytest

from moses.evolution import EvolutionConfig, Evolver
from moses.llm import LLMClient, LLMError
from toy_problems import GuessNumber


class ScriptedLLM(LLMClient):
    """Returns pre-written replies in order; an Exception in the script is raised instead."""

    def __init__(self, replies):
        super().__init__("scripted")
        self.replies = list(replies)
        self.prompts = []

    def _complete(self, prompt, system):
        self.prompts.append(prompt)
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply


def answer(value: float) -> str:
    return f"```python\ndef guess():\n    return {value}\n```"


def test_search_keeps_the_best_program():
    llm = ScriptedLLM([answer(1), answer(3), "no code here", answer(2)])
    result = Evolver(GuessNumber(), llm, EvolutionConfig(iterations=4, seed=0)).run()

    assert "return 3" in result.best.source
    assert len(result.history) == 5  # seed + 4 candidates
    assert not result.history[3].evaluation.valid  # the reply without code
    assert "score" in llm.prompts[-1] and "Previous programs" in llm.prompts[-1]


def test_duplicates_are_not_re_evaluated():
    llm = ScriptedLLM([answer(1), answer(1)])
    result = Evolver(GuessNumber(), llm, EvolutionConfig(iterations=2, seed=0)).run()
    assert len(result.history) == 2  # seed + first answer only


def test_llm_failures_are_counted_and_stop_the_run_when_persistent():
    llm = ScriptedLLM([LLMError("rate limited"), answer(3), LLMError("a"), LLMError("b"), LLMError("c"), answer(3.7)])
    result = Evolver(GuessNumber(), llm, EvolutionConfig(iterations=6, max_consecutive_llm_failures=3)).run()
    assert result.llm_failures == 4
    assert result.best.score == pytest.approx(-0.7)  # stopped before the final, perfect answer
    assert llm.replies == [answer(3.7)]
