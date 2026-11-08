"""Portable reports and narrow, explainable string checks."""

import html
import json
import re
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

from .models import TranslationResult

DIMENSIONS = {
    "accuracy": "准确性",
    "fluency": "流畅性",
    "style": "风格",
    "terminology": "术语一致性",
}
PLACEHOLDER = re.compile(
    r"\{\{\s*[\w.]+\s*\}\}|\$\{[\w.]+\}|\{[\w.]+\}|%\([\w.]+\)[sdif]|(?<!%)%[sdif]"
)
EVIDENCE_LABELS = {
    "found": "已找到",
    "not_found": "未找到",
    "not_provided": "未提供",
    "unavailable": "未核对",
}


def _excerpt_check(excerpt: str, text: str | None) -> tuple[bool | None, str]:
    if not excerpt.strip():
        return None, "not_provided"
    if text is None:
        return None, "unavailable"
    found = excerpt in text
    return found, "found" if found else "not_found"


def review_evidence(result: TranslationResult) -> list[dict] | None:
    """Check cited substrings without editing findings or changing workflow status."""
    if result.review is None:
        return None
    findings = []
    for dimension in DIMENSIONS:
        for index, issue in enumerate(getattr(result.review, dimension), start=1):
            source_found, source_status = _excerpt_check(issue.source_excerpt, result.request.text)
            translation_found, translation_status = _excerpt_check(
                issue.translation_excerpt, result.initial_translation
            )
            findings.append(
                {
                    "dimension": dimension,
                    "issue_index": index,
                    "source_excerpt_found": source_found,
                    "translation_excerpt_found": translation_found,
                    "source_excerpt_status": source_status,
                    "translation_excerpt_status": translation_status,
                }
            )
    return findings


def evidence_summary(finding: dict) -> str:
    return (
        f"原文片段：{EVIDENCE_LABELS[finding['source_excerpt_status']]}；"
        f"初译片段：{EVIDENCE_LABELS[finding['translation_excerpt_status']]}"
    )


def _text_checks(result: TranslationResult, text: str | None) -> dict | None:
    if text is None:
        return None
    terms = [
        {
            "source": source,
            "target": target,
            "matched": target in text,
            "target_occurrences": text.count(target),
        }
        for source, target in result.request.glossary.items()
        if source in result.request.text
    ]
    expected = Counter(PLACEHOLDER.findall(result.request.text))
    found = Counter(PLACEHOLDER.findall(text))
    return {
        "terminology": {
            "applicable": len(terms),
            "matched": sum(t["matched"] for t in terms),
            "terms": terms,
        },
        "placeholders": {
            "expected": dict(expected),
            "found": dict(found),
            "missing": dict(expected - found),
            "extra": dict(found - expected),
            "preserved": expected == found,
        },
    }


def rule_checks(result: TranslationResult) -> dict:
    return {
        "method": "术语按区分大小写的字面子串匹配，仅检查原文出现的术语；占位符按原样及出现次数比较。规则结果不是整体翻译质量评分。",
        "initial": _text_checks(result, result.initial_translation),
        "revised": _text_checks(result, result.revised_translation),
        "review_evidence": {
            "method": "按原样核对审校引用是否为原文或初译的子串；空片段记为未提供。此结果仅供定位引用，不验证建议是否正确，也不改变审校意见。",
            "issues": review_evidence(result),
        },
    }


def _diff_tokens(text: str) -> list[str]:
    tokens = []
    # CJK characters remain individually comparable; other scripts keep whole words.
    for part in re.split(r"([\u3400-\u9fff\u3040-\u30ff])", text):
        if not part:
            continue
        tokens.extend(re.findall(r"\w+(?:['’]\w+)*|\s+|[^\w\s]", part))
    return tokens


def diff_html(result: TranslationResult) -> str:
    if result.initial_translation is None or result.revised_translation is None:
        return '<p class="diff-empty">完成初译与修订后显示修改对照。</p>'
    before = _diff_tokens(result.initial_translation)
    after = _diff_tokens(result.revised_translation)
    pieces = []
    for tag, a, b, c, d in SequenceMatcher(None, before, after, autojunk=False).get_opcodes():
        old, new = html.escape("".join(before[a:b])), html.escape("".join(after[c:d]))
        if tag == "equal":
            pieces.append(old)
        if tag in {"replace", "delete"}:
            pieces.append(f'<del style="background:#fee2e2;color:#991b1b">{old}</del>')
        if tag in {"replace", "insert"}:
            pieces.append(f'<ins style="background:#dcfce7;color:#166534">{new}</ins>')
    return '<div style="white-space:pre-wrap;line-height:1.8">' + "".join(pieces) + "</div>"


def _fence(text: str) -> str:
    longest = max((len(m.group()) for m in re.finditer(r"`+", text)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}\n{text}\n{fence}"


def _cell(value) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def report_markdown(result: TranslationResult) -> str:
    mode = (
        "预置流程示例：手工编写，非模型实测，时间为示例编写标签"
        if result.mode == "preset"
        else "真实模型调用"
    )
    status_label = {"completed": "流程完成", "running": "流程进行中", "failed": "流程失败"}
    lines = [
        "# 翻译运行报告",
        "",
        f"- 模式：{mode}",
        f"- 运行 ID：{result.run_id}",
        f"- 时间：{result.created_at.isoformat()}",
        f"- 后端：{result.backend}",
        f"- 模型：{result.model}",
        f"- 状态：{status_label[result.status]}（{result.status}）",
        *([f"- 提示词：{result.prompt_version or '未记录'}"] if result.mode != "preset" else []),
        "",
        "## 请求与生成配置",
        "",
        _fence(
            json.dumps(
                {
                    "request": result.request.model_dump(),
                    "generation_settings": result.generation_settings,
                },
                ensure_ascii=False,
                indent=2,
            )
        ),
        "",
        "## 初译",
        "",
        _fence(result.initial_translation or "（未生成）"),
        "",
        "## 四维审校",
        "",
    ]
    evidence = {
        (finding["dimension"], finding["issue_index"]): finding
        for finding in review_evidence(result) or []
    }
    if result.review is None:
        lines.append("（未完成）")
    else:
        for key, title in DIMENSIONS.items():
            lines.extend([f"### {title}", ""])
            issues = getattr(result.review, key)
            if not issues:
                lines.extend(["未报告问题。", ""])
                continue
            lines.extend(
                [
                    "| 严重程度 | 原文片段 | 初译片段 | 引用核对 | 原因 | 修改建议 |",
                    "| --- | --- | --- | --- | --- | --- |",
                ]
            )
            for index, issue in enumerate(issues, start=1):
                lines.append(
                    "| "
                    + " | ".join(
                        _cell(value)
                        for value in [
                            issue.severity,
                            issue.source_excerpt,
                            issue.translation_excerpt,
                            evidence_summary(evidence[key, index]),
                            issue.explanation,
                            issue.suggestion,
                        ]
                    )
                    + " |"
                )
            lines.append("")
    lines.extend(
        [
            "",
            "## 修订",
            "",
            _fence(result.revised_translation or "（未生成）"),
            "",
            "## 规则检查",
            "",
            _fence(json.dumps(rule_checks(result), ensure_ascii=False, indent=2)),
            "",
            "## 阶段记录",
            "",
            "| 阶段 | 状态 | 调用次数 | 实测耗时（秒） | 输入 tokens | 输出 tokens | 备注 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for stage in result.stages:
        calls = stage.calls

        # Unknown usage stays unknown even when another attempt has a known value.
        def usage(field):
            values = [getattr(c, field) for c in calls]
            return (
                sum(values) if values and all(value is not None for value in values) else "未提供"
            )

        elapsed = f"{sum(c.elapsed_seconds for c in calls):.3f}" if calls else "未测量"
        lines.append(
            "| "
            + " | ".join(
                map(
                    _cell,
                    [
                        stage.name,
                        stage.status,
                        len(calls),
                        elapsed,
                        usage("input_tokens"),
                        usage("output_tokens"),
                        stage.note,
                    ],
                )
            )
            + " |"
        )
    if result.error:
        lines.extend(["", "## 错误", "", _fence(result.error)])
    lines.extend(["", "完整逐次调用记录与原始输出见同名 JSON 文件。", ""])
    return "\n".join(lines)


def write_report(result: TranslationResult, output_dir: Path) -> tuple[Path, Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path, md_path = output_dir / "result.json", output_dir / "report.md"
    payload = result.model_dump(mode="json")
    payload["rule_checks"] = rule_checks(result)
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(report_markdown(result), encoding="utf-8")
    return json_path, md_path
