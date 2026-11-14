# moses/problems

## Summary
Ready-made, practical problems for the search. Each one is a `Problem` subclass with a plain-language objective, a deliberately weak starting program, and an automatic score.

| Problem | Kind | The program must… | Score |
|---|---|---|---|
| `warehouse_location` | Function optimisation | Place `k` warehouses among towns to minimise the average delivery distance per person | Minus the average distance (km) |
| `price_parser` | Code fragment for a task | Read a price out of text such as `"1.234,56 €"` or `"2.5k"` | % of test texts parsed correctly (some are hidden) |
| `delivery_route` | Heuristic design | Order a van's stops to minimise total driving distance | Minus the average route length (km) |

All test data is generated from fixed seeds, so scores are comparable between runs.

## Adding a problem
1. Create a module here that subclasses `Problem`. See `moses/evolution/README.md` for the fields.
2. Add the class to `_PROBLEM_TYPES` in `__init__.py`.
3. Add a known-good solution to `tests/test_problems.py`. The test checks that it beats the seed program.
