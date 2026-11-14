# tests

## Summary
Tests for the framework. Most run offline. A scripted stand-in replaces the LLM, so the search logic is checked deterministically without network calls. One file talks to real APIs.

| File | Checks |
|---|---|
| `toy_problems.py` | Small problems used by the tests: `GuessNumber`, `Slugify` |
| `test_evaluator.py` | Candidates run isolated: syntax errors, missing functions, timeouts, exceptions and printing are all handled |
| `test_database_and_prompts.py` | Deme size limits, duplicate detection, deme rotation, migration, prompt contents, code extraction |
| `test_engine.py` | The full loop with a scripted LLM: keeps the best program, skips duplicates, survives and stops on LLM failures |
| `test_problems.py` | Every bundled problem has a valid seed program, and a known-good solution scores higher |
| `test_llm_clients.py` | Provider setup: keys from the environment, required settings, error messages |
| `test_llm_smoke.py` | **Live:** asks each provider that has a key set one short question |

## Running
```bash
pytest -m "not live"   # offline, no API key needed
pytest -m live -s      # live smoke test; -s prints the replies
```
- **Which providers run:** the live test runs for every provider whose key variable is set (`GROQ_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) and skips the rest.
- **Cost:** one small request per provider, which is safe on free-tier keys.
- **Choosing a model:** override it with `<PROVIDER>_MODEL`, for example `GROQ_MODEL=llama-3.1-8b-instant`.
