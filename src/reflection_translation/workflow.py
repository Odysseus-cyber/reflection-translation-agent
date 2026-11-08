"""One pass of translation, structured review and evidence-guided revision."""

import json
import time
from collections.abc import Callable

from pydantic import ValidationError

from .llm import LLMClient, ProviderError
from .models import (
    CallRecord,
    LLMResponse,
    ReviewReport,
    StageRecord,
    TranslationRequest,
    TranslationResult,
)
from .prompts import PROMPT_VERSION, messages_for


def parse_review(text: str) -> ReviewReport:
    """Allow a single Markdown JSON fence, but never silently extract fragments."""
    value = text.strip()
    if value.startswith("```") and value.endswith("```"):
        lines = value.splitlines()
        if lines[0].strip().lower() in ("```json", "```") and lines[-1].strip() == "```":
            value = "\n".join(lines[1:-1])
    return ReviewReport.model_validate(json.loads(value))


def translate(
    request: TranslationRequest,
    client: LLMClient,
    on_progress: Callable[[TranslationResult], None] | None = None,
) -> TranslationResult:
    """Return completed or partial failed results; no fixture fallback exists here."""
    result = TranslationResult(
        request=request,
        backend=client.backend,
        model=client.model,
        prompt_version=PROMPT_VERSION,
        generation_settings=getattr(client, "generation_settings", {}),
    )

    def emit():
        if on_progress:
            on_progress(result.model_copy(deep=True))

    def invoke(stage: StageRecord, messages: list[dict[str, str]], schema=None) -> LLMResponse:
        stage.status = "running"
        emit()
        start = time.perf_counter()
        response = None
        error = None
        try:
            response = client.complete(messages, schema=schema)
            if not response.text.strip():
                raise ProviderError("empty_output", "模型返回了空输出。", response)
            return response
        except ProviderError as exc:
            response = exc.response
            error = f"{exc.code}: {exc}"
            raise
        except Exception as exc:
            # Provider implementation bugs still leave a useful partial result; no secrets in repr.
            error = "internal_error: 模型客户端发生内部错误。"
            raise ProviderError("internal_error", "模型客户端发生内部错误。") from exc
        finally:
            stage.calls.append(CallRecord(
                attempt=len(stage.calls) + 1,
                elapsed_seconds=round(time.perf_counter() - start, 6),
                input_tokens=response.input_tokens if response else None,
                output_tokens=response.output_tokens if response else None,
                raw_output=response.text if response else None,
                error=error,
            ))

    active = result.stages[0]
    try:
        initial = invoke(active, messages_for("initial", request))
        result.initial_translation = initial.text.strip()
        active.status = "completed"
        emit()

        active = result.stages[1]
        messages = messages_for("review", request, result.initial_translation)
        for attempt in range(2):
            response = invoke(active, messages, ReviewReport.model_json_schema())
            try:
                result.review = parse_review(response.text)
                break
            except (ValidationError, ValueError) as exc:
                active.calls[-1].error = "invalid_review: 审校结果未通过结构校验。"
                if attempt == 1:
                    raise ProviderError("invalid_review", "审校 JSON 经一次纠正后仍无效。") from exc
                active.note = "首次审校格式无效，正在纠正一次。"
                details = "不是合法的 JSON 对象。"
                if isinstance(exc, ValidationError):
                    details = json.dumps(
                        [{"field": e["loc"], "reason": e["msg"]} for e in exc.errors()],
                        ensure_ascii=False,
                    )
                messages = messages + [
                    {"role": "assistant", "content": response.text},
                    {"role": "user", "content": "请纠正上次输出的结构，仅返回符合指定 Schema 的 JSON。错误：" + details},
                ]
        active.status = "completed"
        active.note = "结构已纠正。" if len(active.calls) == 2 else ""
        emit()

        active = result.stages[2]
        if not result.review.issues:
            result.revised_translation = result.initial_translation
            active.status = "skipped"
            active.note = "审校未发现问题，无需修订；保留初译。"
        else:
            revised = invoke(active, messages_for("revision", request, result.initial_translation, result.review))
            result.revised_translation = revised.text.strip()
            active.status = "completed"
        result.status = "completed"
    except ProviderError as exc:
        active.status = "failed"
        active.note = str(exc)
        result.status = "failed"
        result.error = f"{active.name} / {exc.code}: {exc}"
        for stage in result.stages:
            if stage.status == "pending":
                stage.status = "skipped"
                stage.note = "前序阶段失败，未执行。"
    emit()
    return result
