"""Small, fast problems for testing the framework without real workloads."""

from moses.evolution import CaseResult, Evaluation, Problem


class GuessNumber(Problem):
    """Return a number as close as possible to a hidden target."""

    name = "guess_number"
    entry_point = "guess"
    description = "Write `guess()` returning a number. Score = minus its distance from a hidden target."
    seed_program = "def guess():\n    return 0\n"
    timeout = 5.0
    target = 3.7

    def cases(self) -> list[tuple]:
        return [()]

    def score(self, results: list[CaseResult]) -> Evaluation:
        (result,) = results
        if result.error:
            return Evaluation.failed(result.error)
        if not isinstance(result.output, (int, float)):
            return Evaluation.failed("guess() must return a number")
        distance = abs(result.output - self.target)
        return Evaluation(-distance, f"off by {distance:.3f}")


class Slugify(Problem):
    """Turn titles into URL slugs; scored by the share of examples handled."""

    name = "slugify"
    entry_point = "slugify"
    description = "Write `slugify(title)`: lowercase, words joined by '-', punctuation removed."
    seed_program = "def slugify(title):\n    return title.lower()\n"
    timeout = 5.0
    examples = [("Hello World", "hello-world"), ("Python 3.12!", "python-312"), ("  a  b ", "a-b")]

    def cases(self) -> list[tuple]:
        return [(title,) for title, _ in self.examples]

    def score(self, results: list[CaseResult]) -> Evaluation:
        passed = sum(r.output == expected for r, (_, expected) in zip(results, self.examples))
        return Evaluation(passed / len(self.examples), f"{passed}/{len(self.examples)} correct")
