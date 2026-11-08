import os

import pytest

from reflection_translation.config import Settings, create_client, load_settings
from reflection_translation.llm import ProviderError

ENV_NAMES = (
    "API_BASE_URL", "API_MODEL", "API_KEY", "API_RESPONSE_FORMAT", "OLLAMA_BASE_URL",
    "OLLAMA_MODEL", "LLM_TIMEOUT_SECONDS", "MAX_OUTPUT_TOKENS", "OLLAMA_NUM_CTX",
)


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch, tmp_path):
    for name in ENV_NAMES:
        monkeypatch.delenv(name, raising=False)
    monkeypatch.chdir(tmp_path)


def test_defaults_create_local_client_without_network():
    settings = load_settings()
    assert settings == Settings()
    with create_client("ollama", settings=settings) as client:
        assert client.model == "gemma3:1b"
        assert client.base_url == "http://127.0.0.1:11434"
        assert client.timeout_seconds == 120
        assert client.max_output_tokens == 4096
        assert client.num_ctx == 16384


def test_dotenv_is_read_without_mutating_environment_and_env_wins(tmp_path, monkeypatch):
    path = tmp_path / ".env"
    path.write_text(
        "API_BASE_URL=https://example.test/v1\nAPI_MODEL=file-model\nAPI_KEY=file-secret\n"
        "OLLAMA_MODEL=local-model\nLLM_TIMEOUT_SECONDS=45.5\nMAX_OUTPUT_TOKENS=1000\n"
        "OLLAMA_NUM_CTX=8192\nAPI_RESPONSE_FORMAT=json_schema\n", encoding="utf-8",
    )
    monkeypatch.setenv("API_MODEL", "environment-model")
    monkeypatch.setenv("API_KEY", "")
    settings = load_settings()
    assert settings.api_model == "environment-model"
    assert settings.api_key == ""
    assert settings.ollama_model == "local-model"
    assert settings.timeout_seconds == 45.5
    assert settings.max_output_tokens == 1000
    assert settings.ollama_num_ctx == 8192
    assert settings.api_response_format == "json_schema"
    assert "OLLAMA_MODEL" not in os.environ
    assert "file-secret" not in repr(settings)


def test_explicit_env_path_and_no_secret_interpolation(tmp_path):
    path = tmp_path / "custom.env"
    path.write_text('API_KEY="${UNCHANGED}-secret"\n', encoding="utf-8")
    settings = load_settings(path)
    assert settings.api_key == "${UNCHANGED}-secret"
    assert "UNCHANGED" not in repr(settings)


def test_compatible_model_override_and_all_generation_settings():
    settings = Settings(
        api_base_url="https://example.test/v1", api_model="original", api_key="secret",
        api_response_format="json_object", max_output_tokens=1234, timeout_seconds=22,
    )
    with create_client("compatible", "override", settings) as client:
        assert client.model == "override"
        assert client.timeout_seconds == 22
        assert client.generation_settings == {
            "max_output_tokens": 1234, "api_response_format": "json_object"
        }
        assert "secret" not in str(client.generation_settings)
        assert "example.test" not in str(client.generation_settings)


@pytest.mark.parametrize("env_name,value", [
    ("LLM_TIMEOUT_SECONDS", "0"), ("LLM_TIMEOUT_SECONDS", "nan"), ("LLM_TIMEOUT_SECONDS", "inf"),
    ("MAX_OUTPUT_TOKENS", "0"), ("MAX_OUTPUT_TOKENS", "1.5"), ("OLLAMA_NUM_CTX", "-1"),
    ("API_RESPONSE_FORMAT", "unsupported"), ("OLLAMA_MODEL", ""),
])
def test_bad_settings_raise_readable_safe_errors(monkeypatch, env_name, value):
    monkeypatch.setenv(env_name, value)
    with pytest.raises(ProviderError) as caught:
        load_settings()
    assert caught.value.code == "configuration_error"


@pytest.mark.parametrize("settings", [Settings(), Settings(api_base_url="https://example.test/v1")])
def test_compatible_requires_endpoint_and_model(settings):
    with pytest.raises(ProviderError) as caught:
        create_client("compatible", settings=settings)
    assert caught.value.code == "configuration_error"


def test_unknown_backend_rejected():
    with pytest.raises(ProviderError) as caught:
        create_client("unknown", settings=Settings())
    assert caught.value.code == "configuration_error"
