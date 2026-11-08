"""Shared contracts used by the workflow, providers, CLI and UI."""

from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

Dimension = Literal["accuracy", "fluency", "style", "terminology"]
StageName = Literal["initial", "review", "revision"]


class TranslationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str = Field(min_length=1, max_length=2000)
    source_lang: str = Field(min_length=1, max_length=80)
    target_lang: str = Field(min_length=1, max_length=80)
    locale: str = Field(default="", max_length=120)
    style: str = Field(default="自然、忠实原文", max_length=500)
    glossary: dict[str, str] = Field(default_factory=dict)

    @field_validator("text", "source_lang", "target_lang")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("输入不能为空或仅包含空白")
        return value

    @field_validator("glossary")
    @classmethod
    def nonempty_terms(cls, value: dict[str, str]) -> dict[str, str]:
        if len(value) > 100:
            raise ValueError("术语表最多 100 项")
        if any(not k.strip() or not v.strip() for k, v in value.items()):
            raise ValueError("术语及译法均不能为空")
        return value


class ReviewIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    dimension: Dimension
    source_excerpt: str
    translation_excerpt: str
    explanation: str = Field(min_length=1)
    suggestion: str = Field(min_length=1)
    severity: Literal["minor", "major", "critical"]


class ReviewReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accuracy: list[ReviewIssue]
    fluency: list[ReviewIssue]
    style: list[ReviewIssue]
    terminology: list[ReviewIssue]

    @field_validator("accuracy", "fluency", "style", "terminology")
    @classmethod
    def matching_dimension(cls, issues: list[ReviewIssue], info):
        if any(issue.dimension != info.field_name for issue in issues):
            raise ValueError("问题维度必须与所在分组一致")
        return issues

    @property
    def issues(self) -> list[ReviewIssue]:
        return self.accuracy + self.fluency + self.style + self.terminology


class LLMResponse(BaseModel):
    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None


class CallRecord(BaseModel):
    attempt: int
    elapsed_seconds: float
    input_tokens: int | None = None
    output_tokens: int | None = None
    raw_output: str | None = None
    error: str | None = None


class StageRecord(BaseModel):
    name: StageName
    status: Literal["pending", "running", "completed", "skipped", "failed"] = "pending"
    calls: list[CallRecord] = Field(default_factory=list)
    note: str = ""


class TranslationResult(BaseModel):
    run_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    mode: Literal["live", "preset"] = "live"
    request: TranslationRequest
    backend: str
    model: str
    # Older records and hand-authored examples have no prompt version.
    prompt_version: str | None = None
    generation_settings: dict[str, str | int | float | bool] = Field(default_factory=dict)
    status: Literal["running", "completed", "failed"] = "running"
    initial_translation: str | None = None
    review: ReviewReport | None = None
    revised_translation: str | None = None
    stages: list[StageRecord] = Field(default_factory=lambda: [
        StageRecord(name="initial"), StageRecord(name="review"), StageRecord(name="revision")
    ])
    error: str | None = None
