"""Every bundled problem has a working seed, and better programs get better scores."""

import pytest

from moses.evolution import evaluate
from moses.problems import PROBLEM_NAMES, get_problem

# Hand-written good solutions: each must beat its problem's seed.
GOOD_SOLUTIONS = {
    "warehouse_location": """
import math

def place_warehouses(towns, k):
    sites = [[x, y] for x, y, _ in sorted(towns, key=lambda t: -t[2])[:k]]
    for _ in range(50):  # weighted k-means
        groups = [[] for _ in sites]
        for town in towns:
            nearest = min(range(k), key=lambda i: math.dist(town[:2], sites[i]))
            groups[nearest].append(town)
        for i, group in enumerate(groups):
            if group:
                total = sum(t[2] for t in group)
                sites[i] = [sum(t[0] * t[2] for t in group) / total, sum(t[1] * t[2] for t in group) / total]
    return sites
""",
    "price_parser": r"""
import re

def parse_price(text):
    numbers = re.findall(r"(\d[\d.,]*)\s*([kKmM])?(?![a-zA-Z])", text)
    if not numbers:
        return 0.0 if "free" in text.lower() else None
    number, suffix = numbers[-1]
    number = number.rstrip(".,")
    decimal = re.search(r"[.,](\d{1,2})$", number)
    whole, fraction = (number[: decimal.start()], decimal.group(1)) if decimal else (number, "0")
    value = float(re.sub(r"[.,]", "", whole) + "." + fraction)
    return value * {"k": 1e3, "m": 1e6}.get(suffix.lower(), 1)
""",
    "delivery_route": """
import math

def plan_route(depot, stops):
    remaining, position, order = set(range(len(stops))), depot, []
    while remaining:
        nearest = min(remaining, key=lambda i: math.dist(position, stops[i]))
        remaining.remove(nearest)
        order.append(nearest)
        position = stops[nearest]
    return order
""",
}


@pytest.mark.parametrize("name", PROBLEM_NAMES)
def test_seed_is_valid_and_improvable(name):
    problem = get_problem(name)
    seed = evaluate(problem, problem.seed_program)
    good = evaluate(problem, GOOD_SOLUTIONS[name])
    assert seed.valid, seed.feedback
    assert good.score > seed.score, good.feedback


def test_price_parser_reference_solves_every_case():
    evaluation = evaluate(get_problem("price_parser"), GOOD_SOLUTIONS["price_parser"])
    assert evaluation.score == 100.0, evaluation.feedback


def test_wrong_output_shape_is_invalid():
    problem = get_problem("delivery_route")
    evaluation = evaluate(problem, "def plan_route(depot, stops):\n    return [0, 0]\n")
    assert not evaluation.valid


def test_unknown_problem():
    with pytest.raises(KeyError):
        get_problem("nope")
