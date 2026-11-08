"""Small injectable model interface; no client is created at import time."""

from typing import Protocol

from .models import LLMResponse


class ProviderError(Exception):
    """Safe-to-display failure, optionally retaining an incomplete model response."""

    def __init__(self, code: str, message: str, response: LLMResponse | None = None):
        super().__init__(message)
        self.code = code
        self.response = response


class LLMClient(Protocol):
    backend: str
    model: str

    def complete(self, messages: list[dict[str, str]], *, schema: dict | None = None) -> LLMResponse: ...
