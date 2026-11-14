"""Ready-made problems. Add a new one by subclassing `Problem` and listing it here."""

from __future__ import annotations

from ..evolution import Problem
from .delivery_route import DeliveryRoute
from .price_parser import PriceParser
from .warehouse_location import WarehouseLocation

_PROBLEM_TYPES = (WarehouseLocation, PriceParser, DeliveryRoute)
PROBLEM_NAMES = [cls.name for cls in _PROBLEM_TYPES]


def get_problem(name: str) -> Problem:
    for cls in _PROBLEM_TYPES:
        if cls.name == name:
            return cls()
    raise KeyError(f"Unknown problem {name!r}. Available: {', '.join(PROBLEM_NAMES)}")


__all__ = ["PROBLEM_NAMES", "get_problem"]
