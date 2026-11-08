"""Hand-authored input cases and an explicitly non-measured walkthrough."""

import json
from importlib.resources import files

from .models import TranslationResult


def _read(name: str):
    return json.loads(files("reflection_translation").joinpath("data", name).read_text("utf-8"))


def load_cases() -> list[dict]:
    """Return 12 original inputs, not a scored benchmark or reference translations."""
    return _read("cases.json")


def load_locale_pair() -> list[dict]:
    return _read("locale_pair.json")


def load_preset() -> TranslationResult:
    """A fixed teaching example. Its timestamp labels the authored fixture only."""
    return TranslationResult.model_validate(_read("preset.json"))
