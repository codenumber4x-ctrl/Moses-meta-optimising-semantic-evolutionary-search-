import random

from moses.evolution import Evaluation, Program, ProgramDatabase
from moses.evolution.prompts import build_prompt, extract_code
from toy_problems import GuessNumber


def program(score: float, name: str = "f") -> Program:
    return Program(f"def {name}():\n    return {score}\n", Evaluation(score, f"score {score}"), 0)


def test_demes_keep_only_the_best_programs():
    database = ProgramDatabase(num_demes=1, deme_size=2, rng=random.Random(0))
    for score in (1, 5, 3):
        database.add(program(score, f"f{score}"))
    _, sampled = database.sample(5)
    assert [p.score for p in sampled] == [3, 5]
    assert database.best.score == 5


def test_duplicates_are_detected_ignoring_blank_lines():
    database = ProgramDatabase(rng=random.Random(0))
    database.add(program(1))
    assert "def f():\n\n    return 1   \n" in database
    assert "def g():\n    return 1\n" not in database


def test_sampling_rotates_demes_and_migration_shares_the_best():
    database = ProgramDatabase(num_demes=2, deme_size=4, rng=random.Random(0))
    database.add(program(1, "seed"))
    database.add(program(9, "strong"), deme=0)
    assert [database.sample(1)[0] for _ in range(3)] == [0, 1, 0]
    database.migrate()
    _, deme_one = database.sample(4)  # next deme is 1
    assert max(p.score for p in deme_one) == 9


def test_invalid_programs_are_rejected():
    database = ProgramDatabase()
    try:
        database.add(Program("x", Evaluation.failed("bad"), 1))
    except ValueError:
        return
    raise AssertionError("invalid program was accepted")


def test_prompt_lists_programs_worst_to_best():
    prompt = build_prompt(GuessNumber(), [program(-2.0, "a"), program(-0.5, "b")])
    assert GuessNumber.description in prompt
    assert prompt.index("score -2") < prompt.index("score -0.5")
    assert "`guess`" in prompt


def test_extract_code_takes_the_last_function_block():
    reply = "Idea:\n```python\nx = 1\n```\nFinal:\n```python\ndef guess():\n    return 3\n```\n"
    assert extract_code(reply) == "def guess():\n    return 3"
    assert extract_code("def guess():\n    return 1") == "def guess():\n    return 1"
    assert extract_code("I cannot help with that.") is None
