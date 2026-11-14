"""Heuristic design: plan the order of a delivery van's stops."""

from __future__ import annotations

import math
import random

from ..evolution import CaseResult, Evaluation, Problem


class DeliveryRoute(Problem):
    name = "delivery_route"
    entry_point = "plan_route"
    timeout = 10.0
    description = """\
A delivery van leaves the depot, visits every stop once, and returns to the depot.
Write `plan_route(depot, stops)` where `depot` is [x, y] and `stops` is a list of [x, y]
(coordinates in km). Return the visiting order as a list of stop indices, each exactly once.
Minimise the total straight-line driving distance.
Score = minus the average route length over five days with 25-60 stops each."""
    seed_program = """\
def plan_route(depot, stops):
    # Visit stops in the order they were booked.
    return list(range(len(stops)))
"""

    def __init__(self) -> None:
        self._cases = [_make_day(seed) for seed in range(5)]
        self._baseline = sum(_route_length(d, s, _nearest_neighbour(d, s)) for d, s in self._cases) / len(self._cases)

    def cases(self) -> list[tuple]:
        return self._cases

    def score(self, results: list[CaseResult]) -> Evaluation:
        lengths = []
        for (depot, stops), result in zip(self._cases, results):
            if result.error:
                return Evaluation.failed(result.error)
            order = result.output
            if not isinstance(order, list) or sorted(order) != list(range(len(stops))):
                return Evaluation.failed(f"route must list each of the {len(stops)} stop indices exactly once")
            lengths.append(_route_length(depot, stops, order))

        mean = sum(lengths) / len(lengths)
        change = 100.0 * (self._baseline - mean) / self._baseline
        return Evaluation(
            -mean,
            f"average route {mean:.1f} km ({change:+.1f}% vs. nearest-neighbour baseline {self._baseline:.1f} km)",
        )


def _make_day(seed: int) -> tuple[list[float], list[list[float]]]:
    rng = random.Random(seed)
    stops = [[round(rng.uniform(0, 100), 2), round(rng.uniform(0, 100), 2)] for _ in range(rng.randint(25, 60))]
    return [50.0, 50.0], stops


def _route_length(depot: list[float], stops: list[list[float]], order: list[int]) -> float:
    path = [depot, *(stops[i] for i in order), depot]
    return sum(math.dist(a, b) for a, b in zip(path, path[1:]))


def _nearest_neighbour(depot: list[float], stops: list[list[float]]) -> list[int]:
    remaining, position, order = set(range(len(stops))), depot, []
    while remaining:
        nearest = min(remaining, key=lambda i: math.dist(position, stops[i]))
        remaining.remove(nearest)
        order.append(nearest)
        position = stops[nearest]
    return order
