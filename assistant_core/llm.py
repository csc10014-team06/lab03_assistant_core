
"""LLM interfaces and offline/demo implementations."""

from __future__ import annotations

import logging
import random
import time
from collections.abc import Callable
from typing import Protocol, runtime_checkable


class LLMError(Exception):
    """Raised when an LLM implementation cannot complete a prompt."""


@runtime_checkable
class LLMClient(Protocol):
    """Common interface used by the assistant service."""

    def complete(self, prompt: str) -> str:
        """Return a completion or raise LLMError."""
        ...


class FakeLLM:
    """Deterministic, offline LLM substitute for tests."""

    def __init__(self, response: str = "fake response") -> None:
        self.response = response
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        """Record the prompt and return a configured response."""
        self.prompts.append(prompt)
        return self.response


class DemoLLM:
    """Offline demo implementation matching the monolith's reply format."""

    def __init__(
        self,
        *,
        rng: Callable[[], float] = random.random,
        sleep_fn: Callable[[float], object] = time.sleep,
        timeout_probability: float = 0.1,
        delay_seconds: float = 0.2,
        logger: logging.Logger | None = None,
    ) -> None:
        if not 0.0 <= timeout_probability <= 1.0:
            raise ValueError(
                "timeout_probability must be between 0 and 1"
            )
        if delay_seconds < 0:
            raise ValueError("delay_seconds must not be negative")

        self._rng = rng
        self._sleep = sleep_fn
        self._timeout_probability = timeout_probability
        self._delay_seconds = delay_seconds
        self._logger = logger or logging.getLogger(__name__)

    def complete(self, prompt: str) -> str:
        """Simulate a completion or raise LLMError on timeout."""
        self._logger.debug("LLM prompt: %.60s", prompt)
        self._sleep(self._delay_seconds)

        if self._rng() < self._timeout_probability:
            raise LLMError("LLM timeout")

        return "Here is what I found: " + prompt[-120:]
