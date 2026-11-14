"""Client for the Anthropic Messages API."""

from __future__ import annotations

import anthropic

from .base import GenerationConfig, LLMClient, LLMError


class AnthropicClient(LLMClient):
    """`temperature` is not sent: current Claude models reject sampling parameters."""

    def __init__(
        self,
        model: str,
        api_key: str,
        config: GenerationConfig | None = None,
        min_interval: float = 0.0,
        max_retries: int = 5,
        timeout: float = 600.0,
    ):
        super().__init__(model, config, min_interval)
        # The SDK retries rate limits (honouring Retry-After), timeouts and 5xx errors.
        self._client = anthropic.Anthropic(api_key=api_key, max_retries=max_retries, timeout=timeout)

    def _complete(self, prompt: str, system: str | None) -> str:
        params = {}
        if system:
            params["system"] = system
        if self.config.reasoning_effort is not None:
            params["output_config"] = {"effort": self.config.reasoning_effort}

        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=self.config.max_tokens,
                messages=[{"role": "user", "content": prompt}],
                **params,
            )
        except anthropic.APIError as exc:
            raise LLMError(f"{type(exc).__name__}: {exc}") from exc

        if response.stop_reason == "refusal":
            raise LLMError(f"{self.model} declined the request")
        return "".join(block.text for block in response.content if block.type == "text")
