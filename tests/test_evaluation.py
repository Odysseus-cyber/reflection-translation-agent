import json
from pathlib import Path

import pytest

from reflection_translation import evaluation
from reflection_translation.examples import load_cases
from reflection_translation.models import TranslationResult


class Client:
    backend = "test"
    model = "fixture"


def completed_result(request, client):
    return TranslationResult(
        request=request,
        backend=client.backend,
        model=client.model,
        status="completed",
        initial_translation="First translation.",
        revised_translation="Revised translation.",
    )


def test_interrupted_batch_preserves_finished_case_and_summary(monkeypatch, tmp_path):
    cases = load_cases()[:3]
    calls = 0

    def interrupt_second(request, client, on_progress=None):
        nonlocal calls
        calls += 1
        if calls == 2:
            # The first result is durable before the next potentially slow call.
            checkpoint = json.loads(next(tmp_path.rglob("summary.json")).read_text())
            assert checkpoint["total"] == 1
            assert checkpoint["active_case"] == cases[1]["id"]
            raise KeyboardInterrupt
        return completed_result(request, client)

    monkeypatch.setattr(evaluation, "translate", interrupt_second)
    with pytest.raises(KeyboardInterrupt):
        evaluation.evaluate_cases(cases, Client(), tmp_path)
    summary = json.loads(next(tmp_path.rglob("summary.json")).read_text())
    assert (summary["status"], summary["planned"], summary["total"]) == ("interrupted", 3, 1)
    assert summary["active_case"] == cases[1]["id"]
    assert Path(summary["cases"][0]["json_path"]).is_file()
    result = json.loads(Path(summary["cases"][0]["checkpoint_path"]).read_text())
    assert result["revised_translation"] == "Revised translation."
    assert len(json.loads(Path(summary["blind_mapping"]).read_text())) == 1
    assert calls == 2


def test_report_failure_keeps_current_result_and_stops_new_calls(monkeypatch, tmp_path):
    cases = load_cases()[:3]
    original_write_report = evaluation.write_report
    calls = []

    def translate(request, client, on_progress=None):
        calls.append(request.text)
        return completed_result(request, client)

    def fail_second_report(result, directory):
        if directory.name == cases[1]["id"]:
            raise PermissionError("private-error-detail")
        return original_write_report(result, directory)

    monkeypatch.setattr(evaluation, "translate", translate)
    monkeypatch.setattr(evaluation, "write_report", fail_second_report)
    summary = evaluation.evaluate_cases(cases, Client(), tmp_path)
    assert summary["status"] == "failed"
    assert (summary["total"], summary["completed"], summary["failed"], summary["export_failed"]) == (2, 2, 0, 1)
    assert len(calls) == 2
    assert "private-error-detail" not in json.dumps(summary)
    assert Path(summary["cases"][0]["markdown_path"]).is_file()
    current = summary["cases"][1]
    assert current["export_status"] == "failed"
    assert current["markdown_path"] is None
    assert json.loads(Path(current["checkpoint_path"]).read_text())["status"] == "completed"
    assert json.loads(Path(summary["summary_json"]).read_text()) == summary
    assert len(json.loads(Path(summary["blind_mapping"]).read_text())) == 2


def test_interrupt_during_review_preserves_the_completed_draft(monkeypatch, tmp_path):
    def interrupt_after_initial(request, client, on_progress):
        result = TranslationResult(request=request, backend=client.backend, model=client.model)
        result.initial_translation = "Completed draft before interruption."
        result.stages[0].status = "completed"
        result.stages[1].status = "running"
        on_progress(result)
        raise KeyboardInterrupt

    monkeypatch.setattr(evaluation, "translate", interrupt_after_initial)
    with pytest.raises(KeyboardInterrupt):
        evaluation.evaluate_cases(load_cases()[:1], Client(), tmp_path)
    summary = json.loads(next(tmp_path.rglob("summary.json")).read_text())
    assert summary["status"] == "interrupted"
    assert (summary["total"], summary["completed"], summary["failed"]) == (1, 0, 0)
    row = summary["cases"][0]
    assert row["status"] == "running"
    assert row["export_status"] == "pending"
    checkpoint = json.loads(Path(row["checkpoint_path"]).read_text())
    assert checkpoint["initial_translation"] == "Completed draft before interruption."
    assert checkpoint["revised_translation"] is None
    assert [stage["status"] for stage in checkpoint["stages"]] == ["completed", "running", "pending"]
    assert json.loads(Path(summary["blind_mapping"]).read_text()) == []


def test_unexpected_failure_is_not_silenced_and_preserves_summary(monkeypatch, tmp_path):
    calls = 0

    def fail_second(request, client, on_progress=None):
        nonlocal calls
        calls += 1
        if calls == 2:
            on_progress(TranslationResult(request=request, backend=client.backend, model=client.model))
            raise RuntimeError("private-transport-configuration")
        return completed_result(request, client)

    monkeypatch.setattr(evaluation, "translate", fail_second)
    with pytest.raises(RuntimeError):
        evaluation.evaluate_cases(load_cases()[:2], Client(), tmp_path)
    summary = json.loads(next(tmp_path.rglob("summary.json")).read_text())
    assert summary["status"] == "failed"
    assert summary["completed"] == 1
    assert summary["export_failed"] == 0
    assert summary["cases"][1]["status"] == "running"
    assert "private-transport" not in summary["error"]


def test_atomic_summary_write_does_not_destroy_previous_checkpoint(monkeypatch, tmp_path):
    target = tmp_path / "summary.json"
    target.write_text('{"total": 1}', encoding="utf-8")
    original_write_text = Path.write_text

    def interrupted_write(path, text, *args, **kwargs):
        if path.name == ".summary.json.tmp":
            original_write_text(path, "partial", *args, **kwargs)
            raise OSError("disk full")
        return original_write_text(path, text, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", interrupted_write)
    with pytest.raises(OSError):
        evaluation._atomic_write(target, '{"total": 2}')
    assert json.loads(target.read_text()) == {"total": 1}


def test_interrupt_is_not_replaced_by_checkpoint_io_failure(monkeypatch, tmp_path):
    interrupted = False
    original_atomic_write = evaluation._atomic_write

    def interrupt(request, client, on_progress=None):
        nonlocal interrupted
        interrupted = True
        raise KeyboardInterrupt

    def fail_after_interrupt(path, text):
        if interrupted:
            raise OSError("storage disconnected")
        original_atomic_write(path, text)

    monkeypatch.setattr(evaluation, "translate", interrupt)
    monkeypatch.setattr(evaluation, "_atomic_write", fail_after_interrupt)
    with pytest.raises(KeyboardInterrupt):
        evaluation.evaluate_cases(load_cases()[:1], Client(), tmp_path)
    # The last complete JSON remains readable even though the disk failed afterward.
    summary = json.loads(next(tmp_path.rglob("summary.json")).read_text())
    assert summary["active_case"] == load_cases()[0]["id"]
    assert summary["total"] == 0
