import json

import pytest
from pydantic import ValidationError

from reflection_translation.llm import ProviderError
from reflection_translation.models import LLMResponse, ReviewReport, TranslationRequest
from reflection_translation.workflow import parse_review, translate

EMPTY = {"accuracy": [], "fluency": [], "style": [], "terminology": []}
ISSUES = {**EMPTY, "terminology": [{
    "dimension": "terminology", "source_excerpt": "工作区", "translation_excerpt": "work area",
    "explanation": "未采用术语表译法", "suggestion": "改为 workspace", "severity": "minor",
}]}


class FakeClient:
    backend = "test"
    model = "fixture"
    generation_settings = {"temperature": 0.2}

    def __init__(self, outputs):
        self.outputs = iter(outputs)
        self.calls = []

    def complete(self, messages, *, schema=None):
        self.calls.append((messages, schema))
        value = next(self.outputs)
        if isinstance(value, Exception):
            raise value
        return LLMResponse(text=value, input_tokens=20, output_tokens=10)


@pytest.fixture
def sample_request():
    return TranslationRequest(text="打开工作区 {name}。", source_lang="zh", target_lang="en", locale="en-GB", style="产品文案", glossary={"工作区": "workspace"})


def test_full_pipeline_propagates_context_and_uses_review(sample_request):
    client = FakeClient(["Open work area {name}.", json.dumps(ISSUES), "Open workspace {name}."])
    snapshots = []
    result = translate(sample_request, client, snapshots.append)
    assert result.status == "completed"
    assert result.prompt_version == "v1-json"
    assert [s.status for s in result.stages] == ["completed"] * 3
    assert result.revised_translation == "Open workspace {name}."
    for messages, _ in client.calls:
        content = json.loads(messages[1]["content"])
        assert content["source_text"] == sample_request.text
        assert content["glossary"] == sample_request.glossary
        assert content["locale"] == "en-GB"
        assert content["style"] == "产品文案"
    editor_input = json.loads(client.calls[2][0][1]["content"])
    assert editor_input["initial_translation"] == result.initial_translation
    assert editor_input["review"] == ISSUES
    assert client.calls[1][1] == ReviewReport.model_json_schema()
    assert result.stages[0].calls[0].input_tokens == 20
    assert snapshots[0].initial_translation is None  # snapshots never mutate retroactively
    assert snapshots[-1].status == "completed"


def test_empty_review_retains_draft_without_editor_call(sample_request):
    client = FakeClient(["Open workspace {name}.", json.dumps(EMPTY)])
    result = translate(sample_request, client)
    assert len(client.calls) == 2
    assert result.status == "completed"
    assert result.revised_translation == result.initial_translation
    assert result.stages[2].status == "skipped"


def test_review_is_repaired_once_and_all_usage_retained(sample_request):
    client = FakeClient(["Draft", "not json", json.dumps(EMPTY)])
    result = translate(sample_request, client)
    assert result.status == "completed"
    assert len(result.stages[1].calls) == 2
    assert "invalid_review" in result.stages[1].calls[0].error
    assert result.stages[1].calls[1].output_tokens == 10
    assert client.calls[2][0][-2] == {"role": "assistant", "content": "not json"}


def test_invalid_review_twice_preserves_initial_and_stops(sample_request):
    client = FakeClient(["Draft", "{}", "{}"])
    result = translate(sample_request, client)
    assert result.status == "failed"
    assert result.initial_translation == "Draft"
    assert result.revised_translation is None
    assert len(client.calls) == 3
    assert [s.status for s in result.stages] == ["completed", "failed", "skipped"]


@pytest.mark.parametrize("failure_index", [0, 1, 2])
def test_provider_failure_preserves_completed_stages(sample_request, failure_index):
    outputs = ["Draft", json.dumps(ISSUES), "Revised"]
    outputs[failure_index] = ProviderError("timeout", "模型请求超时。")
    result = translate(sample_request, FakeClient(outputs))
    assert result.status == "failed"
    assert result.stages[failure_index].status == "failed"
    assert result.revised_translation is None
    assert (result.initial_translation is not None) == (failure_index > 0)
    assert (result.review is not None) == (failure_index > 1)


def test_truncated_output_is_only_retained_as_incomplete_call(sample_request):
    response = LLMResponse(text="partial", input_tokens=22, output_tokens=4)
    result = translate(sample_request, FakeClient([ProviderError("truncated", "已截断", response)]))
    assert result.initial_translation is None
    assert result.stages[0].calls[0].raw_output == "partial"
    assert result.stages[0].calls[0].output_tokens == 4


def test_empty_output_is_not_success(sample_request):
    assert translate(sample_request, FakeClient([" \n"])).status == "failed"


def test_unknown_provider_exception_does_not_expose_secret(sample_request):
    result = translate(sample_request, FakeClient([RuntimeError("API_KEY=SECRET")]))
    assert "SECRET" not in result.model_dump_json()
    assert result.status == "failed"


def test_parse_fenced_review_and_reject_mismatched_dimension():
    assert not parse_review("```json\n" + json.dumps(EMPTY) + "\n```").issues
    malformed = {**EMPTY, "accuracy": ISSUES["terminology"]}
    with pytest.raises(ValidationError):
        parse_review(json.dumps(malformed))


@pytest.mark.parametrize("text", ["", "   ", "x" * 2001])
def test_request_rejects_empty_or_too_long(text):
    with pytest.raises(ValidationError):
        TranslationRequest(text=text, source_lang="zh", target_lang="en")
