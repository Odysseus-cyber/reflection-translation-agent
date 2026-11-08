"""HTTP model adapters with safe errors and injectable transports."""

from typing import Literal, Self
from urllib.parse import urlsplit

import httpx

from .llm import ProviderError
from .models import LLMResponse

ResponseFormat = Literal["none", "json_object", "json_schema"]


def validate_base_url(value: str) -> str:
    """Accept an HTTP API root; keep credentials in the dedicated key field."""
    value = value.strip().rstrip("/")
    try:
        parsed = urlsplit(value)
        valid = (
            parsed.scheme in {"http", "https"}
            and bool(parsed.hostname)
            and not parsed.username
            and not parsed.password
            and not parsed.query
            and not parsed.fragment
            and not any(char.isspace() for char in value)
        )
        # Accessing port also validates its syntax and range.
        parsed.port
    except ValueError:
        valid = False
    if not valid:
        raise ProviderError(
            "configuration_error", "API 地址须为 HTTP(S) 地址，且不包含账号、密码、查询参数或片段。"
        )
    return value


def _token_count(value: object) -> int | None:
    # Missing or malformed provider accounting is unknown, never an invented zero.
    return value if type(value) is int and value >= 0 else None


class _HTTPClient:
    """Own internally created HTTP clients; leave injected clients caller-owned."""

    backend: str

    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        timeout_seconds: float = 120,
        max_output_tokens: int = 4096,
        client: httpx.Client | None = None,
    ) -> None:
        self.base_url = validate_base_url(base_url)
        if not model.strip():
            raise ProviderError("configuration_error", "请配置模型名称。")
        if timeout_seconds <= 0 or max_output_tokens <= 0:
            raise ProviderError("configuration_error", "超时时间和输出 token 上限必须大于零。")
        self.model = model.strip()
        self.timeout_seconds = timeout_seconds
        self.max_output_tokens = max_output_tokens
        self._owns_client = client is None
        self._client = client if client is not None else httpx.Client()
        self._closed = False

    def close(self) -> None:
        if self._owns_client:
            self._client.close()
        self._closed = True

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _post(self, endpoint: str, payload: dict, headers: dict | None = None) -> dict:
        if self._closed or self._client.is_closed:
            raise ProviderError("client_closed", "模型客户端已关闭，请重新创建客户端。")
        try:
            response = self._client.post(
                f"{self.base_url}{endpoint}",
                json=payload,
                headers=headers,
                timeout=self.timeout_seconds,
                follow_redirects=False,
            )
        except httpx.TimeoutException:
            raise ProviderError("timeout", "模型请求超时，请检查服务或增加超时时间。") from None
        except httpx.ConnectError:
            raise ProviderError("connection_error", "无法连接模型服务，请检查服务是否启动及 API 地址。") from None
        except httpx.RequestError:
            raise ProviderError("request_error", "模型请求失败，请检查网络及服务配置。") from None

        status = response.status_code
        if status in {401, 403}:
            raise ProviderError("authentication_error", "模型服务拒绝访问，请检查 API 密钥及模型权限。")
        if status == 404:
            raise ProviderError("not_found", "模型服务未找到端点或模型，请检查 API 地址及模型名称。")
        if status == 429:
            raise ProviderError("rate_limit", "模型服务达到请求或配额限制，请稍后重试。")
        if status >= 500:
            raise ProviderError("server_error", f"模型服务暂时不可用（HTTP {status}）。")
        if not 200 <= status < 300:
            raise ProviderError("http_error", f"模型服务拒绝请求（HTTP {status}），请检查配置。")
        try:
            data = response.json()
        except (ValueError, UnicodeError):
            raise ProviderError("invalid_response", "模型服务未返回有效的 JSON 响应。") from None
        if not isinstance(data, dict):
            raise ProviderError("invalid_response", "模型服务返回的响应结构不符合接口约定。")
        if "error" in data:
            raise ProviderError("server_error", "模型服务返回错误，请检查模型是否可用。")
        return data


class CompatibleClient(_HTTPClient):
    """A /chat/completions adapter; base_url includes any provider /v1 prefix."""

    backend = "compatible"

    def __init__(
        self,
        *,
        base_url: str,
        model: str,
        api_key: str = "",
        response_format: ResponseFormat = "none",
        timeout_seconds: float = 120,
        max_output_tokens: int = 4096,
        client: httpx.Client | None = None,
    ) -> None:
        if response_format not in {"none", "json_object", "json_schema"}:
            raise ProviderError("configuration_error", "API_RESPONSE_FORMAT 应为 none、json_object 或 json_schema。")
        if "\r" in api_key or "\n" in api_key:
            raise ProviderError("configuration_error", "API 密钥不能包含换行。")
        super().__init__(
            base_url=base_url,
            model=model,
            timeout_seconds=timeout_seconds,
            max_output_tokens=max_output_tokens,
            client=client,
        )
        self._api_key = api_key
        self.response_format = response_format
        self.generation_settings = {
            "max_output_tokens": max_output_tokens,
            "api_response_format": response_format,
        }

    def complete(self, messages: list[dict[str, str]], *, schema: dict | None = None) -> LLMResponse:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "max_tokens": self.max_output_tokens,
        }
        # Normal translation stages remain text even when review formatting is enabled.
        if schema is not None and self.response_format == "json_object":
            payload["response_format"] = {"type": "json_object"}
        elif schema is not None and self.response_format == "json_schema":
            payload["response_format"] = {
                "type": "json_schema",
                "json_schema": {"name": "translation_review", "strict": True, "schema": schema},
            }
        headers = {"Authorization": f"Bearer {self._api_key}"} if self._api_key else None
        data = self._post("/chat/completions", payload, headers)
        choices = data.get("choices")
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
            raise ProviderError("invalid_response", "模型服务响应缺少有效的 choices。")
        choice = choices[0]
        message = choice.get("message")
        if not isinstance(message, dict):
            raise ProviderError("invalid_response", "模型服务响应缺少有效的 message。")
        content = message.get("content")
        if content is not None and not isinstance(content, str):
            raise ProviderError("invalid_response", "模型服务返回了非文本内容。")
        usage = data.get("usage")
        usage = usage if isinstance(usage, dict) else {}
        result = LLMResponse(
            text=content or "",
            input_tokens=_token_count(usage.get("prompt_tokens")),
            output_tokens=_token_count(usage.get("completion_tokens")),
        )
        if choice.get("finish_reason") == "length":
            raise ProviderError("truncated", "模型输出达到长度上限，未得到完整结果。", result)
        if choice.get("finish_reason") == "content_filter" or message.get("refusal"):
            raise ProviderError("refused", "模型服务未完成该内容的生成。", result)
        if not result.text.strip():
            raise ProviderError("empty_response", "模型服务返回了空文本。", result)
        return result


class OllamaClient(_HTTPClient):
    """Native Ollama /api/chat with JSON schema output for the review stage."""

    backend = "ollama"

    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:11434",
        model: str = "gemma3:1b",
        timeout_seconds: float = 120,
        max_output_tokens: int = 4096,
        num_ctx: int = 16384,
        client: httpx.Client | None = None,
    ) -> None:
        if num_ctx <= 0:
            raise ProviderError("configuration_error", "OLLAMA_NUM_CTX 必须大于零。")
        super().__init__(
            base_url=base_url,
            model=model,
            timeout_seconds=timeout_seconds,
            max_output_tokens=max_output_tokens,
            client=client,
        )
        self.num_ctx = num_ctx
        self.generation_settings = {
            "temperature": 0.2,
            "max_output_tokens": max_output_tokens,
            "ollama_num_ctx": num_ctx,
        }

    def complete(self, messages: list[dict[str, str]], *, schema: dict | None = None) -> LLMResponse:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "num_predict": self.max_output_tokens,
                "num_ctx": self.num_ctx,
            },
        }
        if schema is not None:
            payload["format"] = schema
        data = self._post("/api/chat", payload)
        message = data.get("message")
        if not isinstance(message, dict) or not isinstance(message.get("content"), str):
            raise ProviderError("invalid_response", "Ollama 返回的响应缺少有效文本。")
        result = LLMResponse(
            text=message["content"],
            input_tokens=_token_count(data.get("prompt_eval_count")),
            output_tokens=_token_count(data.get("eval_count")),
        )
        if data.get("done_reason") == "length" or data.get("done") is False:
            raise ProviderError("truncated", "Ollama 未生成完整结果，请检查输出长度上限。", result)
        if data.get("done") is not True:
            raise ProviderError("invalid_response", "Ollama 响应缺少完成标记。", result)
        if not result.text.strip():
            raise ProviderError("empty_response", "Ollama 返回了空文本。", result)
        return result
