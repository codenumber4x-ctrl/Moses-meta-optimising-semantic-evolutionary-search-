"""Live smoke test: one short question per provider whose API key is set.

Each test makes a single small request, so it is safe on free-tier keys.
Override the model with <PROVIDER>_MODEL, e.g. GROQ_MODEL=llama-3.1-8b-instant.
"""

import os

import pytest

from moses.llm import PROVIDERS, GenerationConfig, create_client

pytestmark = pytest.mark.live


@pytest.mark.parametrize("provider", ["groq", "openai", "anthropic"])
def test_model_answers_a_simple_question(provider):
    spec = PROVIDERS[provider]
    if not os.environ.get(spec.api_key_env):
        pytest.skip(f"{spec.api_key_env} is not set")

    model = os.environ.get(f"{provider.upper()}_MODEL")
    client = create_client(provider, model, config=GenerationConfig(max_tokens=1024))
    reply = client.complete("What is the capital of France? Answer with one word.")

    print(f"\n[{provider} / {client.model}] {reply}")
    assert "paris" in reply.lower()
