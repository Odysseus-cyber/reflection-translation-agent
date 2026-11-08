"""Read per-project settings without mutating the process environment."""

import math
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import dotenv_values

from .llm import ProviderError
from .providers import CompatibleClient, OllamaClient, ResponseFormat, validate_base_url


@dataclass(frozen=True)
class Settings:
    api_base_url: str = ""
    api_model: str = ""
    api_key: str = field(default="", repr=False)
    api_response_format: ResponseFormat = "none"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "gemma3:1b"
    timeout_seconds: float = 120
    max_output_tokens: int = 4096
    ollama_num_ctx: int = 16384

    def __post_init__(self) -> None:
        if not math.isfinite(self.timeout_seconds) or self.timeout_seconds <= 0:
            raise ProviderError("configuration_error", "LLM_TIMEOUT_SECONDS 必须为大于零的有限数值。")
        if self.max_output_tokens <= 0 or self.ollama_num_ctx <= 0:
            raise ProviderError("configuration_error", "MAX_OUTPUT_TOKENS 和 OLLAMA_NUM_CTX 必须大于零。")
        if self.api_response_format not in {"none", "json_object", "json_schema"}:
            raise ProviderError("configuration_error", "API_RESPONSE_FORMAT 应为 none、json_object 或 json_schema。")
        validate_base_url(self.ollama_base_url)
        if self.api_base_url:
            validate_base_url(self.api_base_url)
        if not self.ollama_model.strip():
            raise ProviderError("configuration_error", "请配置 OLLAMA_MODEL。")


def load_settings(env_file: str | Path | None = None) -> Settings:
    """Read .env in the working directory, then override with environment values.

    A caller can supply an explicit file path. No ancestor .env files are searched.
    Blank environment values deliberately override values from the file.
    """
    path = Path(env_file) if env_file is not None else Path.cwd() / ".env"
    try:
        values = {**dotenv_values(path, interpolate=False), **os.environ}
    except (OSError, UnicodeError):
        raise ProviderError("configuration_error", "无法读取配置文件，请检查路径、权限和 UTF-8 编码。") from None

    def read(name: str, default: str) -> str:
        value = values.get(name)
        return default if value is None else value.strip()

    try:
        timeout = float(read("LLM_TIMEOUT_SECONDS", "120"))
        max_output_tokens = int(read("MAX_OUTPUT_TOKENS", "4096"))
        num_ctx = int(read("OLLAMA_NUM_CTX", "16384"))
    except ValueError:
        raise ProviderError(
            "configuration_error", "LLM_TIMEOUT_SECONDS 须为数字，MAX_OUTPUT_TOKENS 和 OLLAMA_NUM_CTX 须为整数。"
        ) from None

    return Settings(
        api_base_url=read("API_BASE_URL", ""),
        api_model=read("API_MODEL", ""),
        api_key=read("API_KEY", ""),
        api_response_format=read("API_RESPONSE_FORMAT", "none"),
        ollama_base_url=read("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
        ollama_model=read("OLLAMA_MODEL", "gemma3:1b"),
        timeout_seconds=timeout,
        max_output_tokens=max_output_tokens,
        ollama_num_ctx=num_ctx,
    )


def create_client(
    backend: str, model: str | None = None, settings: Settings | None = None
) -> CompatibleClient | OllamaClient:
    """Build the requested backend without making a network request."""
    if backend not in {"compatible", "ollama"}:
        raise ProviderError("configuration_error", "backend 应为 compatible 或 ollama。")
    settings = settings if settings is not None else load_settings()
    if backend == "ollama":
        return OllamaClient(
            base_url=settings.ollama_base_url,
            model=model if model is not None else settings.ollama_model,
            timeout_seconds=settings.timeout_seconds,
            max_output_tokens=settings.max_output_tokens,
            num_ctx=settings.ollama_num_ctx,
        )
    if not settings.api_base_url:
        raise ProviderError("configuration_error", "请在 .env 中设置 API_BASE_URL。")
    selected_model = model if model is not None else settings.api_model
    if not selected_model.strip():
        raise ProviderError("configuration_error", "请在 .env 中设置 API_MODEL，或指定模型参数。")
    return CompatibleClient(
        base_url=settings.api_base_url,
        model=selected_model,
        api_key=settings.api_key,
        response_format=settings.api_response_format,
        timeout_seconds=settings.timeout_seconds,
        max_output_tokens=settings.max_output_tokens,
    )
