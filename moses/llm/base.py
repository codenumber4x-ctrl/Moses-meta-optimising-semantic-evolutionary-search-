"""Provider-independent interface for text-generation models."""

from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass


class LLMError(RuntimeError):
    """A model call failed after the provider SDK exhausted its retries."""


@dataclass(frozen=True)
class GenerationConfig:
    """Request settings shared by all providers.

    `temperature` and `reasoning_effort` are only sent when set, because
    some models reject them.
    """

    max_tokens: int = 8192
    temperature: float | None = None
    reasoning_effort: str | None = None  # e.g. "low", "medium", "high"


class LLMClient(ABC):
    """Sends a prompt to a model and returns the reply text."""

    def __init__(self, model: str, config: GenerationConfig | None = None, min_interval: float = 0.0):
        self.model = model
        self.config = config or GenerationConfig()
        self._min_interval = min_interval  # seconds between calls; protects low rate limits
        self._last_call = float("-inf")

    def complete(self, prompt: str, system: str | None = None) -> str:
        """Return the model's reply. Raises LLMError on failure or an empty reply."""
        self._throttle()
        text = self._complete(prompt, system)
        if not text.strip():
            raise LLMError(f"{self.model} returned an empty reply")
        return text

    def _throttle(self) -> None:
        wait = self._last_call + self._min_interval - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.monotonic()

    @abstractmethod
    def _complete(self, prompt: str, system: str | None) -> str:
        """Provider-specific request."""


def resolve_api_key(api_key: str | None, env_var: str) -> str:
    """Use the explicit key if given, otherwise read it from `env_var`."""
    key = api_key or os.environ.get(env_var)
    if not key:
        raise LLMError(f"No API key: pass one explicitly or set {env_var}.")
    return key
