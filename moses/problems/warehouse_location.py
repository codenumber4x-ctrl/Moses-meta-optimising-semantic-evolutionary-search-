"""Function optimisation: place warehouses to minimise average delivery distance."""

from __future__ import annotations

import math
import random

from ..evolution import CaseResult, Evaluation, Problem


class WarehouseLocation(Problem):
    name = "warehouse_location"
    entry_point = "place_warehouses"
    timeout = 10.0
    description = """\
A retailer delivers to towns on a map (coordinates in km) and will build k warehouses.
Write `place_warehouses(towns, k)` where `towns` is a list of [x, y, population].
Return a list of exactly k [x, y] warehouse positions; they may be anywhere on the map.
Every town is supplied by its nearest warehouse. Minimise the average straight-line
delivery distance per person (weighted by population).
Score = minus that distance in km, averaged over three different regions."""
    seed_program = """\
def place_warehouses(towns, k):
    # Build warehouses in the k most populous towns.
    largest = sorted(towns, key=lambda town: town[2], reverse=True)[:k]
    return [[x, y] for x, y, _ in largest]
"""

    def __init__(self) -> None:
        self._cases = [(_make_region(seed), k) for seed, k in ((1, 3), (2, 4), (3, 5))]

    def cases(self) -> list[tuple]:
        return self._cases

    def score(self, results: list[CaseResult]) -> Evaluation:
        distances = []
        for (towns, k), result in zip(self._cases, results):
            if result.error:
                return Evaluation.failed(result.error)
            sites = _as_sites(result.output, k)
            if sites is None:
                return Evaluation.failed(f"expected a list of {k} [x, y] pairs, got {str(result.output)[:80]}")
            distances.append(_mean_distance(towns, sites))

        mean = sum(distances) / len(distances)
        per_region = ", ".join(f"{d:.2f}" for d in distances)
        return Evaluation(-mean, f"average distance per person {mean:.2f} km (regions: {per_region})")


def _make_region(seed: int, num_towns: int = 40) -> list[list[float]]:
    """Towns clustered around a few cities, so good placements are not obvious."""
    rng = random.Random(seed)
    cities = [(rng.uniform(15, 85), rng.uniform(15, 85)) for _ in range(5)]
    towns = []
    for _ in range(num_towns):
        cx, cy = rng.choice(cities)
        towns.append([round(rng.gauss(cx, 10), 2), round(rng.gauss(cy, 10), 2), rng.randint(500, 50_000)])
    return towns


def _as_sites(output: object, k: int) -> list[tuple[float, float]] | None:
    if not isinstance(output, list) or len(output) != k:
        return None
    sites = []
    for site in output:
        if not (isinstance(site, list) and len(site) == 2 and all(isinstance(v, (int, float)) for v in site)):
            return None
        if not all(math.isfinite(v) for v in site):
            return None
        sites.append((float(site[0]), float(site[1])))
    return sites


def _mean_distance(towns: list[list[float]], sites: list[tuple[float, float]]) -> float:
    total_people = sum(pop for _, _, pop in towns)
    weighted = sum(pop * min(math.dist((x, y), site) for site in sites) for x, y, pop in towns)
    return weighted / total_people
