# moses/evolution

## Summary
The search engine. It keeps a population of scored Python programs, asks an LLM for improved versions, scores each new program, and keeps the best. It knows nothing about any specific task: problems plug in through the `Problem` class.

## Modules
| File | Role |
|---|---|
| `problem.py` | `Problem`: what a task provides. `Evaluation`: a score (higher is better) plus feedback text |
| `evaluator.py`, `_runner.py` | Runs a candidate in a separate `python -I` process with a time limit, then scores its outputs |
| `database.py` | Program population split into demes. Keeps the best programs per deme, drops duplicates, migrates the best between demes |
| `prompts.py` | Builds the prompt (task, rules, previous programs worst to best with scores and feedback) and pulls the code out of the reply |
| `engine.py` | `Evolver`: the main loop and `EvolutionConfig` |

## One iteration
1. Pick the next deme. Sample a fit parent plus a few other programs from it.
2. Build a prompt from them and ask the LLM for a better program.
3. Extract the code and skip it if it duplicates a known program.
4. Run and score the program. Valid programs join the deme, keeping only the best `deme_size`.
5. Every `migration_interval` iterations, copy each deme's best program to the next deme.

The run stops after `iterations` LLM calls, or after `max_consecutive_llm_failures` failed calls in a row.

## Defining a problem
```python
from moses.evolution import CaseResult, Evaluation, Problem

class MyProblem(Problem):
    name = "my_problem"
    entry_point = "solve"                          # function the program must define
    description = "Plain-language objective shown to the LLM."
    seed_program = "def solve(x):\n    return x\n" # simple, working start
    timeout = 10.0                                 # seconds for all cases together

    def cases(self):                               # JSON-serialisable argument tuples
        return [(1,), (2,)]

    def score(self, results: list[CaseResult]) -> Evaluation:
        ...                                        # higher is better; use Evaluation.failed(...) for invalid output
```
Candidate programs may use only the Python standard library.
