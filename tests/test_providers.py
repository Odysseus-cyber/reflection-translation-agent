import json

import httpx
import pytest

from reflection_translation.llm import ProviderError
from reflection_translation.providers import CompatibleClient, OllamaClient

MESSAGES = [{"role": "user", "content": "Translate: 你好"}]
SCHEMA = {"type": "object", "properties": {"issues": {"type": "array"}}}


def compatible_response(content="Hello", reason="stop", usage=None):
    result = {"choices": [{"message": {"content": content}, "finish_reason": reason}]}
    if usage is not None:
        result["usage"] = usage
    return result


def ollama_response(content="Hello", reason="stop", done=True):
    return {
        "message": {"role": "assistant", "content": content},
        "done": done,
        "done_reason": reason,
        "prompt_eval_count": 12,
        "eval_count": 3,
    }


def adapter(backend, transport):
    client = httpx.Client(transport=transport)
    if backend == "compatible":
        return CompatibleClient(
            base_url="https://example.test/v1", model="test-model", api_key="secret-key", client=client
        ), client
    return OllamaClient(client=client), client


def test_compatible_posts_correct_endpoint_and_preserves_actual_usage():
    def handler(request):
        assert str(request.url) == "https://example.test/custom/v1/chat/completions"
        assert request.headers["Authorization"] == "Bearer test-key"
        assert request.extensions["timeout"]["read"] == 23
        body = json.loads(request.content)
        assert body["messages"] == MESSAGES
        assert body["model"] == "chosen-model"
        assert body["stream"] is False
        assert body["max_tokens"] == 321
        assert "response_format" not in body
        return httpx.Response(200, json=compatible_response(usage={"prompt_tokens": 9, "completion_tokens": 2}))

    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        with CompatibleClient(
            base_url="https://example.test/custom/v1/",
            model="chosen-model",
            api_key="test-key",
            timeout_seconds=23,
            max_output_tokens=321,
            client=http,
        ) as client:
            result = client.complete(MESSAGES, schema=SCHEMA)
            assert result.text == "Hello"
            assert (result.input_tokens, result.output_tokens) == (9, 2)
            assert client.generation_settings == {
                "max_output_tokens": 321, "api_response_format": "none"
            }


@pytest.mark.parametrize("mode", ["none", "json_object", "json_schema"])
def test_compatible_json_mode_only_affects_calls_with_schema(mode):
    seen = []

    def handler(request):
        seen.append(json.loads(request.content))
        assert "authorization" not in request.headers
        return httpx.Response(200, json=compatible_response("{}"))

    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        client = CompatibleClient(
            base_url="http://localhost:8080/v1", model="test", response_format=mode, client=http
        )
        client.complete(MESSAGES, schema=SCHEMA)
        client.complete(MESSAGES)
    assert "response_format" not in seen[1]
    if mode == "none":
        assert "response_format" not in seen[0]
    else:
        assert seen[0]["response_format"]["type"] == mode
    if mode == "json_schema":
        assert seen[0]["response_format"]["json_schema"]["schema"] == SCHEMA
        assert seen[0]["response_format"]["json_schema"]["strict"] is True


def test_ollama_native_schema_options_and_usage():
    seen = []

    def handler(request):
        assert request.url.path == "/api/chat"
        seen.append(json.loads(request.content))
        return httpx.Response(200, json=ollama_response())

    with httpx.Client(transport=httpx.MockTransport(handler)) as http:
        client = OllamaClient(client=http, num_ctx=8192, max_output_tokens=1024)
        result = client.complete(MESSAGES, schema=SCHEMA)
        client.complete(MESSAGES)
        assert client.backend == "ollama"
        assert client.model == "gemma3:1b"
        assert result.input_tokens == 12 and result.output_tokens == 3
        assert client.generation_settings["ollama_num_ctx"] == 8192
    assert seen[0]["format"] == SCHEMA
    assert seen[0]["stream"] is False
    assert seen[0]["options"] == {"temperature": 0.2, "num_predict": 1024, "num_ctx": 8192}
    assert "format" not in seen[1]


@pytest.mark.parametrize("backend", ["compatible", "ollama"])
@pytest.mark.parametrize(
    ("status", "code"),
    [(401, "authentication_error"), (403, "authentication_error"), (404, "not_found"),
     (429, "rate_limit"), (503, "server_error"), (400, "http_error"), (302, "http_error")],
)
def test_http_errors_are_safe_and_redirects_are_not_followed(backend, status, code):
    def handler(request):
        return httpx.Response(
            status, text="secret-key https://example.test?secret=query-token private response body",
            headers={"Location": "https://should-not-follow.test"},
        )

    client, http = adapter(backend, httpx.MockTransport(handler))
    with http, pytest.raises(ProviderError) as caught:
        client.complete(MESSAGES)
    assert caught.value.code == code
    assert "secret" not in str(caught.value)
    assert "example.test" not in str(caught.value)
    assert "private response" not in str(caught.value)


@pytest.mark.parametrize("backend", ["compatible", "ollama"])
@pytest.mark.parametrize(
    ("exception", "code"),
    [(httpx.ReadTimeout, "timeout"), (httpx.ConnectError, "connection_error"),
     (httpx.RemoteProtocolError, "request_error")],
)
def test_transport_failures_are_safe(backend, exception, code):
    def handler(request):
        raise exception("private secret-key query?token=do-not-print", request=request)

    client, http = adapter(backend, httpx.MockTransport(handler))
    with http, pytest.raises(ProviderError) as caught:
        client.complete(MESSAGES)
    assert caught.value.code == code
    assert "secret" not in str(caught.value)
    assert caught.value.__suppress_context__ is True


@pytest.mark.parametrize("backend", ["compatible", "ollama"])
def test_truncation_keeps_partial_text_and_billable_usage(backend):
    body = (compatible_response("partial", "length", {"prompt_tokens": 12, "completion_tokens": 3})
            if backend == "compatible" else ollama_response("partial", "length"))
    client, http = adapter(backend, httpx.MockTransport(lambda _: httpx.Response(200, json=body)))
    with http, pytest.raises(ProviderError) as caught:
        client.complete(MESSAGES)
    assert caught.value.code == "truncated"
    assert caught.value.response.text == "partial"
    assert caught.value.response.input_tokens == 12
    assert caught.value.response.output_tokens == 3


@pytest.mark.parametrize("backend", ["compatible", "ollama"])
def test_empty_output_is_not_success(backend):
    body = compatible_response(" \n") if backend == "compatible" else ollama_response(" \n")
    client, http = adapter(backend, httpx.MockTransport(lambda _: httpx.Response(200, json=body)))
    with http, pytest.raises(ProviderError) as caught:
        client.complete(MESSAGES)
    assert caught.value.code == "empty_response"


@pytest.mark.parametrize("backend", ["compatible", "ollama"])
@pytest.mark.parametrize("body", ["not-json private payload", "[]", "{}"])
def test_invalid_response_is_a_safe_provider_error(backend, body):
    client, http = adapter(backend, httpx.MockTransport(lambda _: httpx.Response(200, text=body)))
    with http, pytest.raises(ProviderError) as caught:
        client.complete(MESSAGES)
    assert caught.value.code == "invalid_response"
    assert "private" not in str(caught.value)


def test_missing_or_invalid_usage_remains_unknown():
    body = compatible_response(usage={"prompt_tokens": True, "completion_tokens": -3})
    client, http = adapter("compatible", httpx.MockTransport(lambda _: httpx.Response(200, json=body)))
    with http:
        result = client.complete(MESSAGES)
    assert result.input_tokens is None and result.output_tokens is None


def test_ollama_incomplete_response_keeps_usage():
    body = ollama_response("half", done=False)
    client, http = adapter("ollama", httpx.MockTransport(lambda _: httpx.Response(200, json=body)))
    with http, pytest.raises(ProviderError) as caught:
        client.complete(MESSAGES)
    assert caught.value.code == "truncated"
    assert caught.value.response.output_tokens == 3


def test_context_manager_closes_owned_client_but_not_injected_transport():
    with OllamaClient() as owned:
        assert not owned._client.is_closed
    assert owned._client.is_closed
    with httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(200, json=ollama_response()))) as http:
        with OllamaClient(client=http) as injected:
            assert injected.complete(MESSAGES).text == "Hello"
        assert not http.is_closed
        with pytest.raises(ProviderError, match="已关闭"):
            injected.complete(MESSAGES)


@pytest.mark.parametrize("url", [
    "https://example.test?key=secret", "https://user:secret@example.test/v1",
    "ftp://example.test", "https://example.test/#secret", "http://example.test:invalid",
])
def test_invalid_base_urls_are_rejected_without_echoing_credentials(url):
    with pytest.raises(ProviderError) as caught:
        CompatibleClient(base_url=url, model="test")
    assert caught.value.code == "configuration_error"
    assert "secret" not in str(caught.value)
