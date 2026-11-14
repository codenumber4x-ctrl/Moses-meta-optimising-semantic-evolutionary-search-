"""The evaluator runs candidate code in a child process and never lets it crash the search."""

from moses.evolution import evaluate
from toy_problems import GuessNumber, Slugify


def test_valid_program_is_scored():
    evaluation = evaluate(GuessNumber(), "def guess():\n    return 3.5\n")
    assert evaluation.valid
    assert abs(evaluation.score + 0.2) < 1e-9


def test_syntax_error_is_reported():
    evaluation = evaluate(GuessNumber(), "def guess(:\n")
    assert not evaluation.valid
    assert "SyntaxError" in evaluation.feedback


def test_missing_entry_point_is_reported():
    evaluation = evaluate(GuessNumber(), "def other():\n    return 1\n")
    assert not evaluation.valid
    assert "guess" in evaluation.feedback


def test_infinite_loop_times_out():
    problem = GuessNumber()
    problem.timeout = 1.0
    evaluation = evaluate(problem, "def guess():\n    while True:\n        pass\n")
    assert not evaluation.valid
    assert "timed out" in evaluation.feedback


def test_exception_in_one_case_reaches_the_scorer():
    source = "def slugify(title):\n    if '!' in title:\n        raise ValueError('bang')\n    return title\n"
    evaluation = evaluate(Slugify(), source)
    assert evaluation.valid
    assert evaluation.score == 0


def test_printing_does_not_corrupt_results():
    evaluation = evaluate(GuessNumber(), "print('noise')\ndef guess():\n    print('more')\n    return 3.7\n")
    assert evaluation.score == 0


def test_unserialisable_output_is_an_error():
    evaluation = evaluate(GuessNumber(), "def guess():\n    return object()\n")
    assert not evaluation.valid
