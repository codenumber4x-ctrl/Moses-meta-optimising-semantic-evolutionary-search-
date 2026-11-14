"""Command line: list problems, ask a model a question, or run an evolutionary search."""

from __future__ import annotations

import argparse
import getpass
import logging
import os
import sys
from pathlib import Path

from .evolution import EvolutionConfig, Evolver
from .llm import PROVIDERS, GenerationConfig, LLMClient, LLMError, create_client
from .problems import PROBLEM_NAMES, get_problem


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")

    if args.command == "problems":
        for name in PROBLEM_NAMES:
            print(f"{name}: {get_problem(name).description.splitlines()[0]}")
        return 0

    try:
        llm = _make_client(args)
        if args.command == "ask":
            print(llm.complete(args.question))
            return 0
        return _run(args, llm)
    except LLMError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def _run(args: argparse.Namespace, llm: LLMClient) -> int:
    problem = get_problem(args.problem)
    config = EvolutionConfig(iterations=args.iterations, num_demes=args.demes, seed=args.seed)
    result = Evolver(problem, llm, config).run()

    best = result.best
    print(f"\nBest score {best.score:.4g} (iteration {best.iteration}): {best.evaluation.feedback}")
    print(f"Candidates evaluated: {len(result.history) - 1}, LLM failures: {result.llm_failures}\n")
    print(best.source)
    if args.output:
        Path(args.output).write_text(best.source + "\n")
        print(f"\nSaved to {args.output}")
    return 0


def _make_client(args: argparse.Namespace) -> LLMClient:
    """Use --api-key or the provider's environment variable; otherwise prompt for the key."""
    env_var = PROVIDERS[args.provider].api_key_env
    api_key = args.api_key or os.environ.get(env_var)
    if not api_key and sys.stdin.isatty():
        api_key = getpass.getpass(f"{env_var} not set. Enter API key: ").strip() or None
    config = GenerationConfig(args.max_tokens, args.temperature, args.reasoning_effort)
    return create_client(
        args.provider, args.model, api_key=api_key, base_url=args.base_url,
        config=config, min_interval=args.min_interval,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m moses", description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("problems", help="list the available problems")

    llm = argparse.ArgumentParser(add_help=False)
    llm.add_argument("--provider", choices=PROVIDERS, default="groq")
    llm.add_argument("--model", help="model name (default: the provider's default)")
    llm.add_argument("--api-key", help="API key (default: the provider's environment variable)")
    llm.add_argument("--base-url", help="server URL, for openai-compatible providers")
    llm.add_argument("--max-tokens", type=int, default=8192)
    llm.add_argument("--temperature", type=float)
    llm.add_argument("--reasoning-effort", help="e.g. low, medium, high (reasoning models only)")
    llm.add_argument("--min-interval", type=float, default=0.0, help="seconds between LLM calls (for low rate limits)")

    ask = commands.add_parser("ask", parents=[llm], help="send one question to the model")
    ask.add_argument("question")

    run = commands.add_parser("run", parents=[llm], help="evolve a solution to a problem")
    run.add_argument("problem", choices=PROBLEM_NAMES)
    run.add_argument("--iterations", type=int, default=10, help="LLM calls to make")
    run.add_argument("--demes", type=int, default=2, help="independent sub-populations")
    run.add_argument("--seed", type=int, help="random seed for parent sampling")
    run.add_argument("--output", help="file to save the best program to")
    return parser
