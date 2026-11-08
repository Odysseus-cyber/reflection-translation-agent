"""Chinese Gradio workbench for live translation and a separate fixed example."""

import html
import json
import logging
from collections.abc import Iterator
from pathlib import Path
from queue import Queue
from threading import Thread

import gradio as gr
from pydantic import ValidationError

from .config import create_client
from .examples import load_cases, load_preset
from .llm import ProviderError
from .models import TranslationRequest, TranslationResult
from .reports import diff_html, evidence_summary, review_evidence, rule_checks, write_report
from .workflow import translate

logger = logging.getLogger(__name__)
ARTIFACT_ROOT = Path("artifacts") / "ui"
DIMENSIONS = {
    "accuracy": "准确性",
    "fluency": "流畅性",
    "style": "风格",
    "terminology": "术语一致性",
}
SEVERITIES = {"minor": "轻微", "major": "较大", "critical": "严重"}
STAGES = {"initial": "初译", "review": "审校", "revision": "修订"}
STATUSES = {
    "pending": "等待",
    "running": "进行中",
    "completed": "完成",
    "skipped": "跳过",
    "failed": "失败",
}
REVIEW_HEADERS = ["维度", "程度", "原文片段", "初译片段", "问题说明", "修改建议"]
RUN_STATUSES = {"running": "流程进行中", "completed": "流程完成", "failed": "流程失败"}
REVIEW_CSS = """
<style>
.review-sheet {color:var(--body-text-color);font-size:var(--text-md);}
.review-sheet table {width:100%;table-layout:fixed;border-collapse:collapse;}
.review-sheet th,.review-sheet td {border:1px solid var(--border-color-primary);padding:12px;
  text-align:left;vertical-align:top;overflow-wrap:anywhere;white-space:pre-wrap;}
.review-sheet th {background:var(--background-fill-secondary);font-weight:600;}
.review-sheet th:first-child {width:11%;}
.review-sheet th:nth-child(2) {width:25%;}
.review-sheet th:nth-child(3) {width:14%;}
.review-sheet th:nth-child(4),.review-sheet th:nth-child(5) {width:25%;}
.review-sheet .review-severity {display:block;color:var(--body-text-color-subdued);font-size:0.9em;}
.review-sheet .review-quote {margin:4px 0 10px;padding-left:8px;border-left:2px solid var(--border-color-primary);}
.review-sheet .review-field {font-size:0.9em;color:var(--body-text-color-subdued);}
@media(max-width:900px) {
  .review-sheet table,.review-sheet tbody,.review-sheet tr,.review-sheet td {display:block;width:auto;}
  .review-sheet thead {display:none;}
  .review-sheet tr {margin-bottom:14px;border:1px solid var(--border-color-primary);border-radius:8px;overflow:hidden;}
  .review-sheet td {border:none;border-bottom:1px solid var(--border-color-primary);padding:10px 12px;}
  .review-sheet td:last-child {border-bottom:none;}
  .review-sheet td::before {content:attr(data-label);display:block;font-size:0.85em;
    color:var(--body-text-color-subdued);margin-bottom:4px;}
  .review-sheet td:first-child {background:var(--background-fill-secondary);font-weight:600;}
  .review-sheet .review-severity {display:inline;margin-left:10px;}
  .review-sheet tr.review-empty {display:flex;align-items:center;padding:10px 12px;gap:16px;}
  .review-sheet tr.review-empty td {padding:0;border:0;background:none;}
  .review-sheet tr.review-empty td::before {display:none;}
}
</style>
"""


def parse_request(
    text: str,
    source_lang: str,
    target_lang: str,
    locale: str,
    style: str,
    glossary_json: str,
) -> TranslationRequest:
    """Parse UI values once; the same request validation also protects the CLI."""
    try:
        glossary = json.loads(glossary_json.strip() or "{}")
    except json.JSONDecodeError as exc:
        raise ValueError('术语表必须是 JSON 对象，例如 {"工作区": "workspace"}。') from exc
    if not isinstance(glossary, dict) or any(
        not isinstance(key, str) or not isinstance(value, str) for key, value in glossary.items()
    ):
        raise ValueError("术语表必须是“原文术语：目标译法”的字符串映射。")
    return TranslationRequest(
        text=text,
        source_lang=source_lang or "",
        target_lang=target_lang or "",
        locale=locale or "",
        style=style or "自然、忠实原文",
        glossary=glossary,
    )


def review_rows(result: TranslationResult) -> list[list[str]]:
    """Keep all four dimensions visible, including dimensions with no findings."""
    if result.review is None:
        return []
    rows = []
    for dimension, label in DIMENSIONS.items():
        issues = getattr(result.review, dimension)
        if not issues:
            rows.append([label, "—", "—", "—", "审校未报告问题", "—"])
        for issue in issues:
            rows.append(
                [
                    label,
                    SEVERITIES[issue.severity],
                    issue.source_excerpt,
                    issue.translation_excerpt,
                    issue.explanation,
                    issue.suggestion,
                ]
            )
    return rows


def review_html(result: TranslationResult) -> str:
    """A wrapped table on desktop and full-detail cards on narrow screens."""
    if result.review is None:
        return '<p class="review-pending">审校完成后显示四维意见。</p>'
    evidence = {
        (finding["dimension"], finding["issue_index"]): finding
        for finding in review_evidence(result) or []
    }
    headers = ["维度／程度", "引用片段", "引用核对", "问题说明", "修改建议"]
    cells = []
    for dimension, label in DIMENSIONS.items():
        issues = getattr(result.review, dimension)
        if not issues:
            cells.append(
                '<tr class="review-empty"><td>' + html.escape(label)
                + '</td><td colspan="4">审校未报告问题</td></tr>'
            )
        for index, issue in enumerate(issues, start=1):
            source = html.escape(issue.source_excerpt) if issue.source_excerpt.strip() else "未提供"
            initial = (
                html.escape(issue.translation_excerpt)
                if issue.translation_excerpt.strip()
                else "未提供"
            )
            values = [
                html.escape(label)
                + '<span class="review-severity">'
                + html.escape(SEVERITIES[issue.severity])
                + "</span>",
                '<span class="review-field">原文</span><div class="review-quote">'
                + source
                + '</div><span class="review-field">初译</span><div class="review-quote">'
                + initial
                + "</div>",
                html.escape(evidence_summary(evidence[dimension, index])),
                html.escape(issue.explanation),
                html.escape(issue.suggestion),
            ]
            cells.append(
                "<tr>"
                + "".join(
                    f'<td data-label="{html.escape(title, quote=True)}">{value}</td>'
                    for title, value in zip(headers, values, strict=True)
                )
                + "</tr>"
            )
    heading = "".join(f'<th scope="col">{html.escape(title)}</th>' for title in headers)
    return (
        REVIEW_CSS
        + '<div class="review-sheet"><table aria-label="四维审校意见"><thead><tr>'
        + heading
        + "</tr></thead><tbody>"
        + "".join(cells)
        + "</tbody></table></div>"
    )


def status_text(result: TranslationResult) -> str:
    if result.mode == "preset":
        timing = "手工固定流程示例 · 无真实模型调用耗时"
    else:
        elapsed = sum(call.elapsed_seconds for stage in result.stages for call in stage.calls)
        timing = f"真实运行 · 已记录模型调用耗时 {elapsed:.2f} 秒"
    lines = [
        f"{RUN_STATUSES[result.status]} · {timing}",
        f"模型：{result.backend} / {result.model}",
        *([f"提示词：{result.prompt_version or '未记录'}"] if result.mode != "preset" else []),
        " → ".join(f"{STAGES[s.name]}：{STATUSES[s.status]}" for s in result.stages),
    ]
    if result.review is not None:
        lines.append(f"审校报告 {len(result.review.issues)} 个问题；四维问题清单不是质量评分。")
    for stage in result.stages:
        if stage.note:
            lines.append(f"{STAGES[stage.name]}：{stage.note}")
    if result.error:
        lines.append(f"错误：{result.error}")
    return "\n".join(lines)


def _report_paths(result: TranslationResult) -> tuple[str, str]:
    paths = write_report(result, ARTIFACT_ROOT / result.run_id)
    return str(paths[0]), str(paths[1])


def render_result(result: TranslationResult, *, export: bool = False) -> tuple:
    json_path, markdown_path = _report_paths(result) if export else (None, None)
    return (
        result.initial_translation or "",
        review_html(result),
        result.revised_translation or "",
        diff_html(result) if result.revised_translation is not None else "",
        status_text(result),
        rule_checks(result) if result.initial_translation is not None else {},
        json_path,
        markdown_path,
    )


def iter_translation(
    request: TranslationRequest, backend: str, model: str | None = None
) -> Iterator[TranslationResult]:
    """Bridge synchronous model calls to Gradio updates without sharing mutable state.

    The worker owns and closes its client even if the UI consumer disconnects. Errors
    cross the queue and are re-raised, so a failed call cannot look like completion.
    """
    events: Queue[tuple[str, object]] = Queue()

    def progress(result: TranslationResult) -> None:
        events.put(("progress", result.model_copy(deep=True)))

    def worker() -> None:
        client = None
        failure = None
        try:
            client = create_client(backend, model=model)
            result = translate(request, client, on_progress=progress)
            events.put(("result", result.model_copy(deep=True)))
        except Exception as exc:
            failure = exc
        finally:
            try:
                if client is not None and callable(getattr(client, "close", None)):
                    client.close()
            except Exception as exc:
                if failure is None:
                    failure = exc
            finally:
                if failure is not None:
                    events.put(("error", failure))
                events.put(("done", None))

    Thread(target=worker, name="translation-ui-worker", daemon=True).start()
    final_result = None
    while True:
        event, value = events.get()
        if event == "progress":
            yield value
        elif event == "result":
            final_result = value
        elif event == "error":
            raise value
        elif event == "done":
            if final_result is not None:
                yield final_result
            return


def _friendly_validation_error(exc: ValidationError) -> str:
    labels = {
        "text": "原文",
        "source_lang": "源语言",
        "target_lang": "目标语言",
        "glossary": "术语表",
    }
    parts = []
    for error in exc.errors():
        field = str(error["loc"][0])
        if field == "text" and error["type"] == "string_too_long":
            parts.append("原文最多 2000 字符；本版本只处理短文本。")
        else:
            parts.append(f"{labels.get(field, field)}：{error['msg']}")
    return "\n".join(parts)


def run_live(
    text: str,
    source_lang: str,
    target_lang: str,
    locale: str,
    style: str,
    glossary_json: str,
    backend: str,
    model: str,
) -> Iterator[tuple]:
    """Gradio handler; clear an earlier run before validation or network activity."""
    yield "", "", "", "", "正在检查配置……", {}, None, None
    try:
        request = parse_request(text, source_lang, target_lang, locale, style, glossary_json)
    except ValidationError as exc:
        message = _friendly_validation_error(exc)
        yield "", "", "", "", f"输入有误：{message}", {}, None, None
        raise gr.Error(message) from exc
    except ValueError as exc:
        yield "", "", "", "", f"输入有误：{exc}", {}, None, None
        raise gr.Error(str(exc)) from exc

    latest = None
    last_view = ("", "", "", "", "正在运行……", {}, None, None)
    try:
        for latest in iter_translation(request, backend, (model or "").strip() or None):
            # Export once after worker cleanup, rather than for every progress snapshot.
            last_view = render_result(latest)
            yield last_view
    except Exception as exc:
        logger.error("Translation UI run failed (%s)", type(exc).__name__)
        message = str(exc) if isinstance(exc, ProviderError) else "界面运行失败，请检查服务。"
        if latest is not None:
            failed = latest.model_copy(deep=True)
            if failed.status == "running":
                failed.status = "failed"
                failed.error = message
                for stage in failed.stages:
                    if stage.status == "running":
                        stage.status = "failed"
            # Avoid rerunning a renderer that may itself have caused this failure.
            view = list(last_view)
            view[0] = failed.initial_translation or ""
            view[2] = failed.revised_translation or ""
            view[4] = status_text(failed) + f"\n界面运行中断：{message}"
            view[-2:] = [None, None]
            yield tuple(view)
        else:
            yield "", "", "", "", f"启动失败：{message}", {}, None, None
        raise gr.Error(message) from None

    # Export is a separate UI action: a filesystem failure cannot rewrite model status.
    if latest is not None:
        try:
            paths = _report_paths(latest)
        except Exception as exc:
            logger.error("Translation report export failed (%s)", type(exc).__name__)
            message = "报告导出失败：请检查输出目录权限或磁盘空间；本次译文仍可复制。"
            view = list(last_view)
            view[4] = status_text(latest) + "\n" + message
            view[-2:] = [None, None]
            yield tuple(view)
            raise gr.Error(message) from None
        view = list(last_view)
        view[-2:] = paths
        yield tuple(view)


def character_count(text: str) -> str:
    count = len(text or "")
    return f"{count} / 2000 字符" + (" · 已超限，请缩短原文。" if count > 2000 else "")


def _output_components(result: TranslationResult | None = None) -> list:
    values = render_result(result) if result else ("", "", "", "", "等待运行", {}, None, None)
    status = gr.Textbox(label="运行状态", value=values[4], lines=4, interactive=False)
    with gr.Row():
        initial = gr.Textbox(label="① 初译", value=values[0], lines=8, interactive=False)
        revision = gr.Textbox(label="③ 修订译文", value=values[2], lines=8, interactive=False)
    gr.Markdown("### ② 四维审校\n逐条查看理由与建议。引用核对仅检查片段是否出现在原文或初译中。")
    review = gr.HTML(value=values[1], label="问题与修改建议")
    gr.Markdown("### 修改对照\n删除与新增以不同颜色标记；修改数量不代表质量提升。")
    diff = gr.HTML(value=values[3], label="初译与修订差异")
    with gr.Accordion("规则检查：术语与占位符", open=False):
        gr.Markdown("这些检查提供具体线索，不等同于语义质量评估。")
        checks = gr.JSON(value=values[5], label="规则检查结果")
    with gr.Row():
        json_file = gr.File(label="下载完整 JSON", interactive=False)
        markdown_file = gr.File(label="下载 Markdown 报告", interactive=False)
    return [initial, review, revision, diff, status, checks, json_file, markdown_file]


def build_app() -> gr.Blocks:
    """Construct the UI without connecting to a provider or starting a server."""
    cases = load_cases()
    case_map = {case["id"]: case for case in cases}
    preset = load_preset()

    def load_case(case_id: str | None) -> tuple:
        if case_id not in case_map:
            return (gr.skip(),) * 6
        request = TranslationRequest.model_validate(case_map[case_id]["request"])
        return (
            request.text,
            request.source_lang,
            request.target_lang,
            request.locale,
            request.style,
            json.dumps(request.glossary, ensure_ascii=False, indent=2),
        )

    with gr.Blocks(title="反思式多语言翻译工作台", analytics_enabled=False) as app:
        gr.Markdown(
            "# 反思式多语言翻译工作台\n"
            "**初译 → 四维审校 → 修订** · 为短文本配置语言、地区表达和术语，查看每一步。"
        )
        with gr.Tab("真实模型运行"):
            gr.Markdown("使用兼容 API 或本地 Ollama。模型凭据从本地配置读取。")
            with gr.Row():
                backend = gr.Dropdown(
                    choices=[("兼容 API", "compatible"), ("本地 Ollama", "ollama")],
                    value="ollama",
                    label="模型后端",
                )
                model = gr.Textbox(label="模型名（可选覆盖）", placeholder="留空使用本地配置")
            case_choice = gr.Dropdown(
                choices=[(f"{case['id']} · {case['category']}", case["id"]) for case in cases],
                value=None,
                label="载入案例原文（也可直接输入自己的文本）",
            )
            with gr.Row():
                source = gr.Dropdown(
                    choices=["中文", "English", "日本語"],
                    value="中文",
                    allow_custom_value=True,
                    label="源语言",
                )
                target = gr.Dropdown(
                    choices=["中文", "English", "日本語"],
                    value="English",
                    allow_custom_value=True,
                    label="目标语言",
                )
                locale = gr.Dropdown(
                    choices=["", "en-US", "en-GB", "zh-CN", "zh-TW", "ja-JP"],
                    value="en-US",
                    allow_custom_value=True,
                    label="目标地区／本地化要求",
                )
            text = gr.Textbox(
                label="待翻译原文",
                lines=7,
                placeholder="输入邮件、产品文案或技术短文本，最多 2000 字符。",
            )
            length = gr.Markdown("0 / 2000 字符")
            with gr.Row():
                style = gr.Dropdown(
                    choices=[
                        "自然、忠实原文",
                        "简洁专业的商务表达",
                        "准确清晰的技术文档",
                        "自然、有吸引力的产品文案",
                    ],
                    value="自然、忠实原文",
                    allow_custom_value=True,
                    label="表达风格（可自定义）",
                )
                glossary = gr.Textbox(
                    label="术语表（JSON，可留空）",
                    value="{}",
                    lines=3,
                    placeholder='{"工作区": "workspace"}',
                )
            run = gr.Button("开始初译 → 审校 → 修订", variant="primary")
            outputs = _output_components()
            case_choice.change(
                load_case,
                inputs=case_choice,
                outputs=[text, source, target, locale, style, glossary],
            )
            text.change(character_count, inputs=text, outputs=length, show_progress="hidden")
            run.click(
                run_live,
                inputs=[text, source, target, locale, style, glossary, backend, model],
                outputs=outputs,
                concurrency_limit=1,
                trigger_mode="once",
            )
        with gr.Tab("预置流程示例"):
            gr.Markdown(
                "## 手工固定流程示例\n"
                "以下内容用于解释界面与三阶段机制，**不是一次真实模型运行，也不是质量评测结果**。"
                "示例输入不可修改；处理新文本请切换到“真实模型运行”。"
            )
            gr.Textbox(label="固定原文", value=preset.request.text, interactive=False, lines=4)
            gr.JSON(value=preset.request.model_dump(exclude={"text"}), label="固定配置")
            preset_outputs = _output_components(preset)
            export = gr.Button("导出这份固定示例")
            export.click(lambda: _report_paths(preset), outputs=preset_outputs[-2:])
        gr.Markdown(
            "基于 Andrew Ng 的开源 Translation Agent 流程扩展 · 一次审校与修订 · 中英为主，兼顾日语"
        )
    return app.queue()
