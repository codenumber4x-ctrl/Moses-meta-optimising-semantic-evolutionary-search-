# MOSES: LLM-guided evolutionary search

## Summary
A step toward MOSES (Meta-Optimizing Semantic Evolutionary Search) for OpenCog Hyperon. It is an evolutionary search over Python programs in the style of FunSearch and AlphaEvolve. Instead of random mutation and crossover, an LLM proposes each new candidate. It sees the objective, the best programs found so far, their scores and their evaluation feedback.

Every candidate is run and scored automatically. Good ones are kept in a population split into demes (sub-populations), and the loop repeats. Any task that can be written as "a Python function plus a scoring rule" fits the framework.

```
sample parents from a deme → build prompt → LLM writes a new program → run and score it → keep it if good → repeat
```

## Layout
| Path | What it is |
|---|---|
| `moses/llm/` | One interface for OpenAI, Anthropic, Groq and any OpenAI-compatible server |
| `moses/evolution/` | The search: problem definition, evaluator, program database, prompts, main loop |
| `moses/problems/` | Ready-made practical problems |
| `tests/` | Offline unit tests, toy problems, and a live LLM smoke test |

## Quick start
Requires Python 3.10 or later.

```bash
pip install -r requirements.txt
export GROQ_API_KEY=your-key   # or OPENAI_API_KEY / ANTHROPIC_API_KEY
```

On Windows PowerShell:
```powershell
pip install -r requirements.txt
$env:GROQ_API_KEY = "your-key"   # current window only; or OPENAI_API_KEY / ANTHROPIC_API_KEY
setx GROQ_API_KEY "your-key"     # optional: keep it for new windows (reopen PowerShell after)
```
If no key is set, the commands below prompt you to type it in.

```bash
python -m moses problems                                   # list problems
python -m moses ask "What is the capital of France?"       # check the LLM connection
python -m moses run delivery_route --iterations 5          # evolve a solution
python -m moses run price_parser --provider anthropic --output best.py
```

Useful options:
- `--provider`: `groq` (the default), `openai`, `anthropic` or `openai-compatible`
- `--model`
- `--reasoning-effort low|medium|high`
- `--min-interval SECONDS` (pause between LLM calls)
- `--iterations N` (one LLM call each)

Free-tier API keys have low per-minute limits. Use few iterations, `--reasoning-effort low` and `--min-interval 10`.

## Tests
```bash
pytest -m "not live"   # offline, no API key needed
pytest -m live -s      # one short question per provider with a key set
```

## Safety
Candidate programs are model-written code. They run in a separate Python process with a time limit, which is not a security sandbox. For anything beyond experiments, run the search inside a container or VM.
