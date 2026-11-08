from collections import Counter

from reflection_translation.examples import load_cases, load_locale_pair, load_preset
from reflection_translation.models import TranslationRequest


def test_twelve_original_cases_cover_four_directions_and_three_domains():
    cases = load_cases()
    assert len(cases) == len({case["id"] for case in cases}) == 12
    requests = [TranslationRequest.model_validate(case["request"]) for case in cases]
    assert set(Counter((req.source_lang, req.target_lang) for req in requests).values()) == {3}
    assert len({(req.source_lang, req.target_lang) for req in requests}) == 4
    assert Counter(case["category"] for case in cases) == {
        "产品文案": 4,
        "商务沟通": 4,
        "技术说明": 4,
    }


def test_locale_pair_only_changes_locale_and_id():
    left, right = load_locale_pair()
    assert left["request"]["locale"] == "en-US"
    assert right["request"]["locale"] == "en-GB"
    assert {k: v for k, v in left["request"].items() if k != "locale"} == {
        k: v for k, v in right["request"].items() if k != "locale"
    }


def test_preset_has_no_measured_calls_or_tokens():
    preset = load_preset()
    assert preset.mode == "preset"
    assert all(not stage.calls for stage in preset.stages)
    assert preset.review.terminology
    assert "workspace" in preset.revised_translation
    assert load_preset() == preset
