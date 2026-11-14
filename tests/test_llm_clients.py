"""Client construction and configuration checks (no network)."""

import pytest

from moses.llm import PROVIDERS, LLMError, create_client
from moses.llm.anthropic_client import AnthropicClient
from moses.llm.openai_client import OpenAIClient


@pytest.fixture(autouse=True)
def no_keys(monkeypatch):
    for spec in PROVIDERS.values():
        monkeypatch.delenv(spec.api_key_env, raising=False)
    monkeypatch.delenv("LLM_BASE_URL", raising=False)


def test_missing_key_names_the_environment_variable():
    with pytest.raises(LLMError, match="GROQ_API_KEY"):
        create_client("groq")


def test_key_from_environment(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    assert isinstance(create_client("openai"), OpenAIClient)


def test_explicit_key_and_provider_types():
    assert isinstance(create_client("anthropic", api_key="k"), AnthropicClient)
    groq = create_client("groq", api_key="k")
    assert isinstance(groq, OpenAIClient)
    assert groq.model == PROVIDERS["groq"].default_model


def test_openai_compatible_needs_url_and_model():
    with pytest.raises(LLMError, match="model"):
        create_client("openai-compatible", api_key="k")
    with pytest.raises(LLMError, match="base_url"):
        create_client("openai-compatible", "local-model", api_key="k")
    client = create_client("openai-compatible", "local-model", api_key="k", base_url="http://localhost:8000/v1")
    assert client.model == "local-model"


def test_unknown_provider():
    with pytest.raises(LLMError, match="Unknown provider"):
        create_client("nope", api_key="k")
