"""UI behavior tests use injected clients and never call a model service."""

from threading import Event

import gradio as gr
import pytest
from pydantic import ValidationError

from reflection_translation import ui
from reflection_translation.examples import load_preset
from reflection_translation.llm import ProviderError
from reflection_translation.models import ReviewReport, TranslationRequest, TranslationResult


@pytest.fixture
def request_data():
    return TranslationRequest(text="你好", source_lang="中文", target_lang="English")


def test_request_validation_covers_glossary_and_short_text_limit():
    request = ui.parse_request(
        "工作区", "中文", "English", "en-GB", "专业", '{"工作区":"workspace"}'
    )
    assert request.glossary == {"工作区": "workspace"}
    assert request.locale == "en-GB"
    for invalid in ["not json", "[]", '{"工作区": 123}']:
        with pytest.raises(ValueError, match="术语表"):
            ui.parse_request("原文", "中文", "English", "", "", invalid)
    with pytest.raises(ValidationError):
        ui.parse_request("文" * 2001, "中文", "English", "", "", "")


def test_progress_snapshots_are_independent_and_client_is_closed(monkeypatch, request_data):
    closed = Event()

    class Client:
        def close(self):
            closed.set()

    def translate(request, client, on_progress):
        result = TranslationResult(request=request, backend="ollama", model="test")
        result.initial_translation = "Hello"
        on_progress(result)
        result.revised_translation = "Hi"
        result.status = "completed"
        return result

    monkeypatch.setattr(ui, "create_client", lambda backend, model=None: Client())
    monkeypatch.setattr(ui, "translate", translate)
    snapshots = list(ui.iter_translation(request_data, "ollama"))
    assert len(snapshots) == 2
    assert snapshots[0].status == "running"
    assert snapshots[0].revised_translation is None
    assert snapshots[1].revised_translation == "Hi"
    assert closed.is_set()


def test_worker_error_is_propagated_after_client_cleanup(monkeypatch, request_data):
    closed = Event()

    class Client:
        def close(self):
            closed.set()

    def translate(request, client, on_progress):
        result = TranslationResult(request=request, backend="ollama", model="test")
        result.initial_translation = "Hello"
        on_progress(result)
        raise RuntimeError("审校失败")

    monkeypatch.setattr(ui, "create_client", lambda backend, model=None: Client())
    monkeypatch.setattr(ui, "translate", translate)
    iterator = ui.iter_translation(request_data, "ollama")
    assert next(iterator).initial_translation == "Hello"
    with pytest.raises(RuntimeError, match="审校失败"):
        next(iterator)
    assert closed.is_set()


def test_disconnected_consumer_does_not_skip_client_cleanup(monkeypatch, request_data):
    closed = Event()
    proceed = Event()

    class Client:
        def close(self):
            closed.set()

    def translate(request, client, on_progress):
        result = TranslationResult(request=request, backend="ollama", model="test")
        on_progress(result)
        assert proceed.wait(timeout=2)
        return result

    monkeypatch.setattr(ui, "create_client", lambda backend, model=None: Client())
    monkeypatch.setattr(ui, "translate", translate)
    iterator = ui.iter_translation(request_data, "ollama")
    next(iterator)
    iterator.close()
    proceed.set()
    assert closed.wait(timeout=2)


def test_empty_review_shows_each_dimension_without_claiming_a_quality_score(request_data):
    result = TranslationResult(request=request_data, backend="ollama", model="test")
    result.review = ReviewReport(accuracy=[], fluency=[], style=[], terminology=[])
    rows = ui.review_rows(result)
    assert [row[0] for row in rows] == ["准确性", "流畅性", "风格", "术语一致性"]
    assert all(row[4] == "审校未报告问题" for row in rows)
    assert "不是质量评分" in ui.status_text(result)


def test_preset_status_does_not_claim_real_model_timing(request_data):
    result = TranslationResult(
        request=request_data, backend="preset", model="manual", mode="preset"
    )
    assert "手工固定流程示例" in ui.status_text(result)
    assert "无真实模型调用耗时" in ui.status_text(result)
    assert "真实运行" not in ui.status_text(result)


def test_live_validation_clears_previous_outputs_and_reports_error(monkeypatch):
    def no_client(*args, **kwargs):
        pytest.fail("Invalid input must not create a model client")

    monkeypatch.setattr(ui, "create_client", no_client)
    iterator = ui.run_live("文" * 2001, "中文", "English", "", "", "{}", "ollama", "")
    assert next(iterator)[:4] == ("", "", "", "")
    invalid = next(iterator)
    assert "2000" in invalid[4]
    assert invalid[-2:] == (None, None)
    with pytest.raises(gr.Error):
        next(iterator)


def test_live_error_keeps_the_completed_draft(monkeypatch, request_data):
    def failing_iterator(request, backend, model):
        result = TranslationResult(request=request, backend=backend, model="test")
        result.initial_translation = "Hello"
        result.stages[0].status = "completed"
        result.stages[1].status = "running"
        yield result
        raise ProviderError("unavailable", "审校接口暂不可用")

    monkeypatch.setattr(ui, "iter_translation", failing_iterator)
    monkeypatch.setattr(ui, "rule_checks", lambda result: {})
    iterator = ui.run_live(request_data.text, "中文", "English", "", "", "{}", "ollama", "")
    next(iterator)
    assert next(iterator)[0] == "Hello"
    failed = next(iterator)
    assert failed[0] == "Hello"
    assert "审校：失败" in failed[4]
    with pytest.raises(gr.Error, match="审校接口暂不可用"):
        next(iterator)


def test_unexpected_error_does_not_expose_exception_content(monkeypatch, caplog):
    def failing_iterator(*args):
        raise RuntimeError("private-key-in-library-error")
        yield

    monkeypatch.setattr(ui, "iter_translation", failing_iterator)
    iterator = ui.run_live("你好", "中文", "English", "", "", "{}", "ollama", "")
    next(iterator)
    failed = next(iterator)
    assert "private-key" not in failed[4]
    assert "界面运行失败" in failed[4]
    with pytest.raises(gr.Error) as error:
        next(iterator)
    assert "private-key" not in str(error.value)
    assert "private-key" not in caplog.text


def test_build_app_does_not_create_clients_or_write_reports(monkeypatch):
    def unexpected(*args, **kwargs):
        pytest.fail("Building the interface must not call models or export files")

    monkeypatch.setattr(ui, "create_client", unexpected)
    monkeypatch.setattr(ui, "write_report", unexpected)
    app = ui.build_app()
    assert isinstance(app, gr.Blocks)
    components = app.get_config_file()["components"]
    tabs = [
        component["props"]["label"] for component in components if component["type"] == "tabitem"
    ]
    assert tabs == ["真实模型运行", "预置流程示例"]
    assert not any(component["props"].get("type") == "password" for component in components)
    app.close()


def test_review_html_shows_all_details_escapes_model_content_and_reflows():
    result = load_preset()
    issue = result.review.style[0]
    issue.source_excerpt = '<script>alert("source")</script>'
    issue.translation_excerpt = '<img src=x onerror="bad">'
    issue.explanation = '<b>reason & "quote"</b>'
    issue.suggestion = '<a href="javascript:bad">suggestion</a>'
    rendered = ui.review_html(result)
    assert "<script>" not in rendered and "<img " not in rendered
    assert '<a href="javascript:' not in rendered
    assert "&lt;script&gt;" in rendered and "&lt;img " in rendered
    assert "reason &amp; &quot;quote&quot;" in rendered
    assert "suggestion&lt;/a&gt;" in rendered
    assert "原文片段：未找到；初译片段：未找到" in rendered
    assert "@media(max-width:900px)" in rendered
    assert 'data-label="修改建议"' in rendered
    assert all(label in rendered for label in ["准确性", "流畅性", "风格", "术语一致性"])
    assert "var(--body-text-color)" in rendered


def test_empty_review_still_has_all_four_dimensions_in_html(request_data):
    result = TranslationResult(request=request_data, backend="ollama", model="test")
    result.review = ReviewReport(accuracy=[], fluency=[], style=[], terminology=[])
    rendered = ui.review_html(result)
    assert rendered.count("审校未报告问题") == 4
    assert all(label in rendered for label in ui.DIMENSIONS.values())


@pytest.mark.parametrize("workflow_status", ["completed", "failed"])
def test_export_failure_preserves_model_results_and_workflow_status(
    monkeypatch, workflow_status, caplog
):
    result = load_preset()
    result.mode = "live"
    result.status = workflow_status
    result.prompt_version = "v1-json"
    if workflow_status == "failed":
        result.stages[1].status = "failed"
        result.stages[1].note = "审校生成截断"
        result.stages[2].status = "skipped"
        result.revised_translation = None
        result.error = "review / truncated"
    before = result.model_dump()

    def failed_export(*args):
        raise PermissionError("private-export-path-and-secret")

    monkeypatch.setattr(ui, "iter_translation", lambda *args: iter([result]))
    monkeypatch.setattr(ui, "write_report", failed_export)
    iterator = ui.run_live(result.request.text, "中文", "English", "", "", "{}", "ollama", "")
    next(iterator)  # Clear the previous display.
    completed_view = next(iterator)
    final_view = next(iterator)
    assert final_view[:4] == completed_view[:4]
    assert final_view[-2:] == (None, None)
    assert final_view[4].startswith(ui.RUN_STATUSES[workflow_status])
    assert "报告导出失败" in final_view[4]
    assert "提示词：v1-json" in final_view[4]
    if workflow_status == "failed":
        assert "审校：失败" in final_view[4]
        assert "review / truncated" in final_view[4]
    with pytest.raises(gr.Error, match="报告导出失败"):
        next(iterator)
    assert result.model_dump() == before
    assert "private-export-path" not in final_view[4] + caplog.text


def test_successful_export_adds_downloads_without_repeating_model_calls(monkeypatch, tmp_path):
    result = load_preset()
    result.mode = "live"
    monkeypatch.setattr(ui, "iter_translation", lambda *args: iter([result]))
    monkeypatch.setattr(ui, "ARTIFACT_ROOT", tmp_path)
    views = list(ui.run_live(result.request.text, "中文", "English", "", "", "{}", "ollama", ""))
    assert views[-1][4].startswith("流程完成")
    assert views[-1][0] == result.initial_translation
    assert views[-1][2] == result.revised_translation
    assert all(path is not None for path in views[-1][-2:])
