import json

import pytest

from reflection_translation import evaluation
from reflection_translation.examples import load_cases, load_preset
from reflection_translation.models import CallRecord, TranslationRequest
from reflection_translation.reports import (
    diff_html,
    report_markdown,
    review_evidence,
    rule_checks,
    write_report,
)


def test_checks_ignore_terms_absent_from_source_and_count_duplicate_placeholders():
    result = load_preset()
    result.request = TranslationRequest(
        text="你好 {name} {name}，工作区。",
        source_lang="中文",
        target_lang="English",
        glossary={"工作区": "workspace", "不存在": "absent"},
    )
    result.initial_translation = "Hi {name}, workspace."
    result.revised_translation = "Hi {name} {name}, workspace."
    checks = rule_checks(result)
    assert checks["initial"]["terminology"]["applicable"] == 1
    assert checks["initial"]["terminology"]["matched"] == 1
    assert checks["initial"]["placeholders"]["missing"] == {"{name}": 1}
    assert checks["revised"]["placeholders"]["preserved"]


def test_new_placeholder_is_reported_and_cannot_pass():
    result = load_preset()
    result.revised_translation += " {new}"
    checks = rule_checks(result)["revised"]["placeholders"]
    assert checks["extra"] == {"{new}": 1}
    assert not checks["preserved"]


def test_placeholder_patterns_do_not_count_nested_tokens_twice():
    result = load_preset()
    result.request.text = "{{name}} ${x} %(value)s %d {error_code}"
    result.initial_translation = result.request.text
    counts = rule_checks(result)["initial"]["placeholders"]["expected"]
    assert len(counts) == 5
    assert all(count == 1 for count in counts.values())


def test_partial_results_are_not_empty_successes():
    result = load_preset()
    result.initial_translation = result.revised_translation = None
    assert rule_checks(result)["initial"] is None
    assert rule_checks(result)["revised"] is None
    assert "完成初译" in diff_html(result)


def test_diff_escapes_html_for_equal_deleted_and_inserted_content():
    result = load_preset()
    result.initial_translation = '<script>alert("old")</script> & text'
    result.revised_translation = '<script>alert("new")</script> & changed'
    rendered = diff_html(result)
    assert "<script>" not in rendered
    assert "&lt;script&gt;" in rendered
    assert "&amp;" in rendered
    assert "<ins " in rendered and "<del " in rendered


def test_diff_preserves_english_words_chinese_characters_and_line_breaks():
    result = load_preset()
    result.initial_translation = "Your work area.\n这里旧文。"
    result.revised_translation = "Your workspace.\n这里新文。"
    rendered = diff_html(result)
    assert ">work area</del>" in rendered
    assert ">workspace</ins>" in rendered
    assert ">旧</del>" in rendered and ">新</ins>" in rendered
    assert "\n这里" in rendered


def test_export_preserves_request_review_metadata_and_unknown_usage(tmp_path):
    result = load_preset()
    result.mode = "live"
    result.generation_settings = {"temperature": 0.2}
    result.stages[0].calls = [
        CallRecord(attempt=1, elapsed_seconds=0.1, input_tokens=0, output_tokens=None)
    ]
    json_path, md_path = write_report(result, tmp_path)
    exported = json.loads(json_path.read_text())
    assert exported["request"] == result.request.model_dump()
    assert exported["review"] == result.review.model_dump()
    assert exported["generation_settings"] == {"temperature": 0.2}
    assert exported["stages"][0]["calls"][0]["output_tokens"] is None
    assert "0.100 | 0 | 未提供" in md_path.read_text()
    assert "api_key" not in json_path.read_text().lower()


def test_preset_report_never_presents_authored_time_as_a_measurement():
    markdown = report_markdown(load_preset())
    assert "手工编写，非模型实测" in markdown
    assert "时间为示例编写标签" in markdown
    assert "未测量" in markdown


def test_evaluation_keeps_failures_and_separate_blind_mapping(monkeypatch, tmp_path):
    def fake_translate(request, client, on_progress=None):
        result = load_preset()
        result.request = request
        result.mode = "live"
        if request.text == load_cases()[1]["request"]["text"]:
            result.status = "failed"
            result.revised_translation = None
            result.error = "review failed"
        return result

    monkeypatch.setattr(evaluation, "translate", fake_translate)
    client = type("Client", (), {"backend": "test", "model": "test-model"})()
    summary = evaluation.evaluate_cases(load_cases()[:2], client, tmp_path)
    assert (summary["total"], summary["completed"], summary["failed"]) == (2, 1, 1)
    from pathlib import Path

    mapping = json.loads(Path(summary["blind_mapping"]).read_text())
    assert len(mapping) == 1
    assert {mapping[0]["A"], mapping[0]["B"]} == {"initial_translation", "revised_translation"}
    manual = Path(summary["manual_review"]).read_text()
    assert "initial_translation" not in manual
    assert "修订更好／相当／初译更好" in manual
    assert Path(summary["cases"][1]["json_path"]).is_file()


def test_evaluation_rejects_path_ids_before_any_model_call(tmp_path):
    case = load_cases()[0]
    case["id"] = "../outside"
    with pytest.raises(ValueError):
        evaluation.evaluate_cases([case], object(), tmp_path)
    assert not list(tmp_path.iterdir())


def test_evidence_checks_real_substrings_without_changing_findings_or_result(tmp_path):
    result = load_preset()
    result.review.style[0].source_excerpt = "原文不存在的概述"
    result.review.style[0].translation_excerpt = "When you connect again"
    before = result.model_dump(mode="json")
    evidence = review_evidence(result)
    assert evidence[0]["source_excerpt_found"] is False
    assert evidence[0]["translation_excerpt_found"] is True
    assert evidence[0]["source_excerpt_status"] == "not_found"
    json_path, markdown_path = write_report(result, tmp_path)
    payload = json.loads(json_path.read_text())
    assert payload["rule_checks"]["review_evidence"]["issues"] == evidence
    assert "原文片段：未找到；初译片段：已找到" in markdown_path.read_text()
    assert result.model_dump(mode="json") == before
    assert payload["status"] == "completed"


def test_empty_citations_are_not_mismatches_and_unavailable_draft_is_distinct():
    result = load_preset()
    result.review.style[0].source_excerpt = " \n"
    result.review.style[0].translation_excerpt = ""
    item = review_evidence(result)[0]
    assert item["source_excerpt_found"] is None
    assert item["translation_excerpt_found"] is None
    assert item["source_excerpt_status"] == item["translation_excerpt_status"] == "not_provided"
    result.review.style[0].translation_excerpt = "nonempty"
    result.initial_translation = None
    item = review_evidence(result)[0]
    assert item["translation_excerpt_found"] is None
    assert item["translation_excerpt_status"] == "unavailable"


def test_evidence_distinguishes_pending_review_from_empty_review():
    result = load_preset()
    result.review.style = result.review.terminology = []
    assert review_evidence(result) == []
    result.review = None
    assert review_evidence(result) is None


def test_report_labels_workflow_completion_and_records_prompt_version():
    result = load_preset()
    result.mode = "live"
    result.prompt_version = "v1-json"
    report = report_markdown(result)
    assert "状态：流程完成（completed）" in report
    assert "提示词：v1-json" in report
    result.prompt_version = None
    assert "提示词：未记录" in report_markdown(result)
    result.mode = "preset"
    assert "提示词：" not in report_markdown(result)
