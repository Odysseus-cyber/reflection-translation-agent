import json

import pytest

from reflection_translation.cli import main
from reflection_translation.llm import ProviderError
from reflection_translation.models import LLMResponse


class FakeClient:
    backend = "test"
    model = "fixture"
    closed = False

    def __init__(self):
        self.outputs = iter(["Hello", json.dumps({k: [] for k in ("accuracy", "fluency", "style", "terminology")})])

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.closed = True

    def complete(self, messages, *, schema=None):
        return LLMResponse(text=next(self.outputs))


def test_cli_exports_real_result_and_closes_client(monkeypatch, tmp_path, capsys):
    client = FakeClient()
    monkeypatch.setattr("reflection_translation.config.create_client", lambda *args: client)
    code = main(["translate", "--text", "你好", "--source", "zh", "--target", "en", "--output", str(tmp_path)])
    assert code == 0
    assert client.closed
    assert "Hello" in capsys.readouterr().out
    report = json.loads(next(tmp_path.rglob("*.json")).read_text())
    assert report["mode"] == "live"
    assert report["status"] == "completed"


def test_cli_configuration_error_is_actionable_without_traceback(monkeypatch, capsys):
    def unavailable(*_):
        raise ProviderError("configuration_error", "请设置 API_BASE_URL。")
    monkeypatch.setattr("reflection_translation.config.create_client", unavailable)
    assert main(["translate", "--text", "你好", "--source", "zh", "--target", "en"]) == 2
    error = capsys.readouterr().err
    assert "API_BASE_URL" in error
    assert "Traceback" not in error


def test_cli_rejects_long_text_before_client_creation(monkeypatch, capsys):
    def forbidden(*_):
        raise AssertionError("client should not be created")
    monkeypatch.setattr("reflection_translation.config.create_client", forbidden)
    assert main(["translate", "--text", "x" * 2001, "--source", "zh", "--target", "en"]) == 2
    assert "text" in capsys.readouterr().err


def test_cli_unknown_case_fails_without_model_call(monkeypatch, capsys):
    def forbidden(*_):
        raise AssertionError("client should not be created")
    monkeypatch.setattr("reflection_translation.config.create_client", forbidden)
    assert main(["evaluate", "--case", "unknown"]) == 2
    assert "未知案例" in capsys.readouterr().err


def test_export_failure_does_not_hide_completed_translation(monkeypatch, capsys):
    monkeypatch.setattr("reflection_translation.config.create_client", lambda *args: FakeClient())
    def failed_export(*_):
        raise PermissionError("no write permission")
    monkeypatch.setattr("reflection_translation.reports.write_report", failed_export)
    assert main(["translate", "--text", "你好", "--source", "zh", "--target", "en"]) == 2
    output = capsys.readouterr()
    assert "Hello" in output.out
    assert "报告导出失败" in output.err


@pytest.mark.parametrize("command", ["translate", "evaluate"])
def test_unusable_output_fails_before_creating_client(monkeypatch, tmp_path, capsys, command):
    output = tmp_path / "existing-file"
    output.write_text("keep me")

    def forbidden(*_):
        pytest.fail("An unusable output directory must fail before client creation")

    monkeypatch.setattr("reflection_translation.config.create_client", forbidden)
    args = [command, "--output", str(output)]
    if command == "translate":
        args.extend(["--text", "你好", "--source", "zh", "--target", "en"])
    assert main(args) == 2
    assert "输出目录无法写入" in capsys.readouterr().err
    assert output.read_text() == "keep me"


@pytest.mark.parametrize("error_type", [OSError, ValueError, RuntimeError])
def test_library_errors_do_not_echo_configuration(monkeypatch, tmp_path, capsys, error_type):
    def unsafe_failure(*_):
        raise error_type("private-api-key-in-exception")

    monkeypatch.setattr("reflection_translation.config.create_client", unsafe_failure)
    assert main([
        "translate", "--text", "你好", "--source", "zh", "--target", "en",
        "--output", str(tmp_path),
    ]) == 2
    output = capsys.readouterr()
    assert "private-api-key" not in output.out + output.err
    assert "Traceback" not in output.err


def test_evaluation_interrupt_closes_client_and_returns_130(monkeypatch, tmp_path, capsys):
    client = FakeClient()

    def interrupted(*_, **kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr("reflection_translation.config.create_client", lambda *args: client)
    monkeypatch.setattr("reflection_translation.evaluation.translate", interrupted)
    assert main(["evaluate", "--output", str(tmp_path)]) == 130
    assert client.closed
    assert "评估已中断" in capsys.readouterr().err
    summary = json.loads(next(tmp_path.rglob("summary.json")).read_text())
    assert summary["status"] == "interrupted"


def test_evaluation_export_failure_returns_2_with_recovery_summary(monkeypatch, tmp_path, capsys):
    client = FakeClient()

    def failed_export(*_):
        raise OSError("private-filesystem-detail")

    monkeypatch.setattr("reflection_translation.config.create_client", lambda *args: client)
    monkeypatch.setattr("reflection_translation.evaluation.write_report", failed_export)
    assert main(["evaluate", "--output", str(tmp_path)]) == 2
    assert client.closed
    output = capsys.readouterr()
    summary = json.loads(output.out)
    assert summary["status"] == "failed"
    assert summary["export_failed"] == 1
    assert summary["cases"][0]["checkpoint_path"]
    assert "private-filesystem-detail" not in output.out + output.err
