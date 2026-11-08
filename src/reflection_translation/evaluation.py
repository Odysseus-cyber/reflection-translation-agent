"""Paired draft/revision records, with recoverable per-case progress."""

import json
import random
import re
from pathlib import Path
from uuid import uuid4

from .models import TranslationRequest
from .reports import _cell, _fence, rule_checks, write_report
from .workflow import translate


def _atomic_write(path: Path, text: str) -> None:
    """Replace a checkpoint only after its complete contents have been written."""
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def evaluate_cases(cases: list[dict], client, output_dir: Path) -> dict:
    """Checkpoint each result; preserve interrupts and stop after an export failure.

    A summary's case status describes translation; export_status describes report
    availability. Checkpoint JSON retains a result even if report rendering fails.
    """
    identifiers = [case["id"] for case in cases]
    if len(set(identifiers)) != len(identifiers):
        raise ValueError("评估案例 ID 不得重复")
    if any(not re.fullmatch(r"[a-z0-9][a-z0-9-]*", identifier) for identifier in identifiers):
        raise ValueError("案例 ID 仅允许小写字母、数字与连字符")
    requests = [TranslationRequest.model_validate(case["request"]) for case in cases]
    evaluation_id = f"evaluation-{uuid4()}"
    directory = Path(output_dir).resolve() / evaluation_id
    directory.mkdir(parents=True, exist_ok=True)
    randomizer = random.Random(evaluation_id)
    rows, mapping = [], []
    manual = [
        "# 人工 A/B 对照评审",
        "",
        "先评审本文件，再打开 blind-mapping.json 揭盲。A/B 顺序按案例随机分配；两份译文来自同一次运行。",
        "",
        "分别检查准确性、流畅性、目标风格和术语一致性；每维填写 A 更好／相当／B 更好，并引用具体片段。",
        "",
        "不要把规则命中数当作整体质量分。此文件没有预填质量结论。",
        "",
    ]
    summary = {
        "evaluation_id": evaluation_id,
        "output_dir": str(directory),
        "backend": client.backend,
        "model": client.model,
        "status": "running",
        "planned": len(cases),
        "total": 0,
        "completed": 0,
        "failed": 0,
        "export_failed": 0,
        "active_case": None,
        "error": None,
        "cases": rows,
        "summary_json": str(directory / "summary.json"),
        "summary_markdown": str(directory / "summary.md"),
        "manual_review": str(directory / "manual-review.md"),
        "blind_mapping": str(directory / "blind-mapping.json"),
    }

    def save_summary() -> None:
        summary["total"] = len(rows)
        summary["completed"] = sum(row["status"] == "completed" for row in rows)
        summary["failed"] = sum(row["status"] == "failed" for row in rows)
        summary["export_failed"] = sum(row["export_status"] == "failed" for row in rows)
        _atomic_write(
            Path(summary["summary_json"]),
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        )

    def save_documents() -> None:
        lines = [
            "# 配对翻译运行记录",
            "",
            f"后端：{client.backend}；模型：{client.model}",
            "",
            f"批次状态：{summary['status']}；计划 {summary['planned']} 例，已记录 {summary['total']} 例，"
            f"流程完成 {summary['completed']} 例，失败 {summary['failed']} 例，导出失败 {summary['export_failed']} 例。",
            "",
            "以上只表示执行状态，不表示译文质量提升。术语、占位符检查见逐例报告；人工质量结论需填写 manual-review.md 后揭盲。",
            "",
            "| 案例 | 场景 | 流程状态 | 导出状态 | 记录 |",
            "| --- | --- | --- | --- | --- |",
        ]
        for row in rows:
            link = "未写入"
            if row["markdown_path"]:
                link = f"[报告]({row['id']}/report.md)"
            elif row["checkpoint_path"]:
                link = f"[原始结果]({row['id']}/checkpoint.json)"
            lines.append(
                f"| {row['id']} | {_cell(row['category'])} | {row['status']} | {row['export_status']} | {link} |"
            )
        if summary["error"]:
            lines.extend(["", summary["error"]])
        _atomic_write(Path(summary["summary_markdown"]), "\n".join(lines) + "\n")
        _atomic_write(Path(summary["manual_review"]), "\n".join(manual))
        _atomic_write(
            Path(summary["blind_mapping"]),
            json.dumps(mapping, ensure_ascii=False, indent=2) + "\n",
        )

    def save_state() -> None:
        # The JSON checkpoint remains useful even if a later presentation export fails.
        save_summary()
        save_documents()

    def save_terminal_state() -> None:
        # If the disk is no longer writable, retain earlier atomic checkpoints and
        # return/raise the original outcome; do not replace an interrupt with I/O errors.
        try:
            save_state()
        except OSError:
            pass

    row = None
    try:
        save_state()
        for case, request in zip(cases, requests, strict=True):
            row = None
            summary["active_case"] = case["id"]
            save_summary()
            case_directory = directory / case["id"]
            checkpoint_path = case_directory / "checkpoint.json"

            def checkpoint_progress(snapshot) -> None:
                nonlocal row
                case_directory.mkdir(parents=True, exist_ok=True)
                _atomic_write(checkpoint_path, snapshot.model_dump_json(indent=2) + "\n")
                if row is None:
                    row = {
                        "id": case["id"],
                        "category": case["category"],
                        "run_id": snapshot.run_id,
                        "export_status": "pending",
                        "checkpoint_path": str(checkpoint_path),
                        "json_path": None,
                        "markdown_path": None,
                    }
                    rows.append(row)
                row.update(
                    status=snapshot.status,
                    error=snapshot.error,
                    rule_checks=rule_checks(snapshot),
                )
                # Completed stages survive an interrupt during the next model call.
                save_summary()

            result = translate(request, client, on_progress=checkpoint_progress)
            checkpoint_progress(result)

            if (
                result.status == "completed"
                and result.initial_translation is not None
                and result.revised_translation is not None
            ):
                labels = ["initial_translation", "revised_translation"]
                randomizer.shuffle(labels)
                mapping.append({"id": case["id"], "A": labels[0], "B": labels[1]})
                manual.extend([
                    f"## {case['id']} · {case['category']}", "",
                    "### 输入与要求", "",
                    _fence(json.dumps(request.model_dump(), ensure_ascii=False, indent=2)), "",
                    "### 译文 A", "", _fence(getattr(result, labels[0])), "",
                    "### 译文 B", "", _fence(getattr(result, labels[1])), "",
                    "| 维度 | A 更好／相当／B 更好 | 片段与理由 |",
                    "| --- | --- | --- |",
                    "| 准确性 | | |", "| 流畅性 | | |", "| 风格 | | |", "| 术语一致性 | | |", "",
                    "整体偏好：________；理由：________", "",
                    "揭盲后结论（修订更好／相当／初译更好）：________", "",
                ])
            json_path, markdown_path = write_report(result, case_directory)
            row.update(
                export_status="completed",
                json_path=str(json_path),
                markdown_path=str(markdown_path),
            )
            summary["active_case"] = None
            save_state()
        summary["status"] = "completed"
        save_state()
    except KeyboardInterrupt:
        summary["status"] = "interrupted"
        summary["error"] = "评估已中断；已写入的逐例记录可继续查看，尚未完成的案例需重新运行。"
        save_terminal_state()
        raise
    except OSError:
        if row is not None and row["export_status"] == "pending":
            row["export_status"] = "failed"
        summary["status"] = "failed"
        summary["error"] = "评估报告导出失败，已停止后续案例；请检查输出目录和磁盘空间。"
        save_terminal_state()
    except Exception:
        summary["status"] = "failed"
        summary["error"] = "评估执行失败；已写入的逐例记录和汇总已保留。"
        save_terminal_state()
        raise
    return summary
