"""Code fragment: a function that reads prices out of free text."""

from __future__ import annotations

from ..evolution import CaseResult, Evaluation, Problem

# (text, expected price, shown in feedback?). Hidden cases check the program generalises.
_CASES = [
    ("$19.99", 19.99, True),
    ("Price: 1,299 USD", 1299.0, True),
    ("€3,50", 3.5, True),
    ("Call for price", None, True),
    ("FREE", 0.0, True),
    ("2.5k", 2500.0, True),
    ("1.234,56 €", 1234.56, False),
    ("USD 45", 45.0, False),
    ("Now only £7.00!", 7.0, False),
    ("Was $30, now $25", 25.0, False),
    ("12.5M", 12_500_000.0, False),
    ("Sold out", None, False),
    ("Price: 0.99", 0.99, False),
    ("Total: 1,000,000.00 USD", 1_000_000.0, False),
    ("9,99€", 9.99, False),
    ("free shipping", 0.0, False),
]


class PriceParser(Problem):
    name = "price_parser"
    entry_point = "parse_price"
    timeout = 5.0
    description = """\
Write `parse_price(text)` that returns the price in a short product text as a float, or None.
Rules:
- A price is a number with optional thousands separators and an optional decimal part.
  Both "." and "," are used: a separator followed by 1-2 final digits is the decimal point,
  one followed by 3 digits separates thousands ("1,299" = 1299, "3,50" = 3.5, "1.234,56" = 1234.56).
- A "k" or "M" suffix (any case) multiplies by 1,000 or 1,000,000 ("2.5k" = 2500).
- Currency symbols and codes ($, €, £, USD, ...) can appear before or after the number.
- If there are several numbers, return the last one.
- If there is no number but the text contains "free" (any case), return 0.0; otherwise return None.
Score = percentage of test texts parsed correctly; some test texts are hidden."""
    seed_program = """\
def parse_price(text):
    try:
        return float(text.replace("$", "").replace(",", "").strip())
    except ValueError:
        return None
"""

    def cases(self) -> list[tuple]:
        return [(text,) for text, _, _ in _CASES]

    def score(self, results: list[CaseResult]) -> Evaluation:
        failures, hidden_failures = [], 0
        for (text, expected, shown), result in zip(_CASES, results):
            if _matches(result.output, expected) and not result.error:
                continue
            if shown:
                got = result.error or repr(result.output)
                failures.append(f"{text!r} -> expected {expected!r}, got {got}")
            else:
                hidden_failures += 1

        passed = len(_CASES) - len(failures) - hidden_failures
        feedback = f"{passed}/{len(_CASES)} correct"
        if failures:
            feedback += "; failed: " + "; ".join(failures[:3])
        if hidden_failures:
            feedback += f"; {hidden_failures} hidden case(s) failed"
        return Evaluation(100.0 * passed / len(_CASES), feedback)


def _matches(output: object, expected: float | None) -> bool:
    if expected is None or output is None:
        return output is expected
    return isinstance(output, (int, float)) and abs(output - expected) < 1e-6
