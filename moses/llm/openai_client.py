"""Client for the OpenAI Chat Completions API and servers that implement it (Groq, vLLM, Ollama, ...)."""

from __future__ import annotations

import openai

from .base import GenerationConfig, LLMClient, LLMError


class OpenAIClient(LLMClient):
    def __init__(
        self,
        model: str,
        api_key: str,
        base_url: str | None = None,
        config: GenerationConfig | None = None,
        min_interval: float = 0.0,
        token_limit_param: str = "max_completion_tokens",
        max_retries: int = 5,
        timeout: float = 300.0,
    ):
        super().__init__(model, config, min_interval)
        # Older OpenAI-compatible servers only understand "max_tokens".
        self._token_limit_param = token_limit_param
        # The SDK retries rate limits (honouring Retry-After), timeouts and 5xx errors.
        self._client = openai.OpenAI(api_key=api_key, base_url=base_url, max_retries=max_retries, timeout=timeout)

    def _complete(self, prompt: str, system: str | None) -> str:
        messages = [{"role": "system", "content": system}] if system else []
        messages.append({"role": "user", "content": prompt})

        params = {self._token_limit_param: self.config.max_tokens}
        if self.config.temperature is not None:
            params["temperature"] = self.config.temperature
        if self.config.reasoning_effort is not None:
            params["reasoning_effort"] = self.config.reasoning_effort

        try:
            response = self._client.chat.completions.create(model=self.model, messages=messages, **params)
        except openai.APIError as exc:
            raise LLMError(f"{type(exc).__name__}: {exc}") from exc
        return response.choices[0].message.content or ""
