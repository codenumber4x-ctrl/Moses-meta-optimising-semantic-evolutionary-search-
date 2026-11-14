"""LLM provider clients behind one interface: `create_client(provider, ...)`."""

from __future__ import annotations

import os
from dataclasses import dataclass

from .base import GenerationConfig, LLMClient, LLMError, resolve_api_key


@dataclass(frozen=True)
class Provider:
    api_key_env: str
    default_model: str | None
    base_url: str | None = None
    base_url_env: str | None = None


PROVIDERS = {
    "openai": Provider("OPENAI_API_KEY", "gpt-5-mini"),
    "anthropic": Provider("ANTHROPIC_API_KEY", "claude-opus-5-5"),
    "groq": Provider("GROQ_API_KEY", "openai/gpt-oss-120b", base_url="https://api.groq.com/openai/v1"),
    "openai-compatible": Provider("LLM_API_KEY", None, base_url_env="LLM_BASE_URL"),
}


def create_client(
    provider: str,
    model: str | None = None,
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    config: GenerationConfig | None = None,
    min_interval: float = 0.0,
) -> LLMClient:
    """Build a client for `provider`.

    The API key comes from `api_key` or the provider's environment variable
    (see PROVIDERS). `base_url` is required for "openai-compatible"
    (or set LLM_BASE_URL).
    """
    if provider not in PROVIDERS:
        raise LLMError(f"Unknown provider {provider!r}. Choose from: {', '.join(PROVIDERS)}.")
    spec = PROVIDERS[provider]

    model = model or spec.default_model
    if not model:
        raise LLMError(f"Provider {provider!r} needs an explicit model name.")
    key = resolve_api_key(api_key, spec.api_key_env)

    if provider == "anthropic":
        from .anthropic_client import AnthropicClient

        return AnthropicClient(model, key, config, min_interval)

    from .openai_client import OpenAIClient

    url = base_url or spec.base_url or (os.environ.get(spec.base_url_env) if spec.base_url_env else None)
    if provider == "openai-compatible":
        if not url:
            raise LLMError("openai-compatible needs base_url (or set LLM_BASE_URL).")
        return OpenAIClient(model, key, url, config, min_interval, token_limit_param="max_tokens")
    return OpenAIClient(model, key, url, config, min_interval)


__all__ = ["PROVIDERS", "GenerationConfig", "LLMClient", "LLMError", "create_client"]
