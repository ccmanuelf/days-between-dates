"""Help and "How this is calculated" through the page, on the running server (SPEC, S15, S16; AC17, AC18)."""

import re

import pytest
from playwright.sync_api import expect

from test_page import EN, ES, STRINGS, choose_language, count, settle

SECTIONS = ["range", "business", "own", "reversed", "past", "elections", "language", "demo", "sources"]
WITH_EXAMPLE = {"range": "total", "business": "business", "reversed": "reversed"}


def is_guide(key: str) -> bool:
    return key.startswith(("help_", "how_", "example_"))


def fill(template: str, **values) -> str:
    for name, value in values.items():
        template = template.replace("{" + name + "}", str(value))
    assert "{" not in template, template
    return template


def example_text(strings: dict, example: dict) -> str:
    """The page's sentence for one worked example, from the numbers the API counted."""
    common = {"known": example["known_answer"], "start": example["start"], "end": example["end"]}
    if example["role"] == "total":
        total = example["total"]
        return fill(strings["example_total"], snc=total["start_not_counted"], bc=total["both_counted"], **common)
    if example["role"] == "business":
        mf, business = example["monday_to_friday"], example["business"]
        return fill(
            strings["example_business"], calendar=strings[f"calendar_{example['calendar']}"],
            mf_snc=mf["start_not_counted"], mf_bc=mf["both_counted"], excluded=", ".join(example["excluded"]),
            snc=business["start_not_counted"], bc=business["both_counted"], **common,
        )
    return fill(
        strings["example_reversed"], entered_start=example["entered"]["start"],
        entered_end=example["entered"]["end"], **common,
    )


def examples_by_role(server) -> dict:
    status, body = server.call("GET", "/api/guide")
    assert status == 200, body
    return {e["role"]: e for e in body["examples"]}


@pytest.mark.parametrize("language", ["en", "es"])
def test_s15_help_has_one_section_per_feature_with_its_examples(server, open_page, language):
    strings = STRINGS[language]
    page = open_page(server.url)
    choose_language(page, language)
    settle(page, lambda: page.click("#help-toggle"))
    examples = examples_by_role(server)
    expect(page.locator("#help dt")).to_have_text([strings[f"help_{s}_title"] for s in SECTIONS])
    texts = [
        f"{strings[f'help_{s}']} {example_text(strings, examples[WITH_EXAMPLE[s]])}" if s in WITH_EXAMPLE
        else strings[f"help_{s}"]
        for s in SECTIONS
    ]
    expect(page.locator("#help dd")).to_have_text(texts)


@pytest.mark.parametrize("language", ["en", "es"])
def test_s16_each_result_shows_its_formula_and_a_worked_example(server, open_page, language):
    strings = STRINGS[language]
    page = open_page(server.url)
    choose_language(page, language)
    count(page, "2026-10-26", "2026-10-30")
    examples = examples_by_role(server)
    settle(page, lambda: page.click("#how-total-toggle"))
    expect(page.locator("#how-total .how-text")).to_have_text(
        f"{strings['how_total']} {example_text(strings, examples['total'])}"
    )
    settle(page, lambda: page.click("#how-business-toggle"))
    expect(page.locator("#how-business .how-text")).to_have_text(
        f"{strings['how_business']} {example_text(strings, examples['business'])}"
    )


def test_s16_the_examples_are_counted_each_time_a_panel_opens(server, open_page):
    page = open_page(server.url)
    asked = []
    page.on("request", lambda r: asked.append(r.url) if "/api/guide" in r.url else None)
    settle(page, lambda: page.click("#help-toggle"))
    page.click("#help-toggle")  # closes: no request
    settle(page, lambda: page.click("#help-toggle"))
    assert len(asked) == 2, asked


def test_s16_a_language_switch_rewrites_the_open_guide(server, open_page):
    page = open_page(server.url)
    settle(page, lambda: page.click("#help-toggle"))
    choose_language(page, "es")
    expect(page.locator("#help dt").first).to_have_text(ES["help_range_title"])
    expect(page.locator("#help dd").first).to_contain_text(ES["help_range"])


def test_ac17_the_guide_is_shorter_than_the_rest_of_the_page_in_each_language():
    for language in ("en", "es"):
        strings = STRINGS[language]
        guide = sum(len(v) for k, v in strings.items() if is_guide(k))
        rest = sum(len(v) for k, v in strings.items() if not is_guide(k))
        assert 0 < guide < rest, (language, guide, rest)


def test_ac18_the_guide_writes_no_digit_of_its_own():
    """The guide's strings hold no digit: each figure in Help and "How this is calculated" is filled in from the API's
    count, which tests/test_guide.py checks against the known answers; a figure typed into the text could drift from
    the code."""
    for language in ("en", "es"):
        typed = {k: v for k, v in STRINGS[language].items() if is_guide(k) and re.search(r"\d", v)}
        assert not typed, (language, typed)


@pytest.mark.parametrize(
    "language,words", [("en", "without your own holidays"), ("es", "sin sus días festivos propios")]
)
def test_s16_each_worked_example_says_it_leaves_out_your_own_holidays(server, open_page, language, words):
    """The words are written here, not read from strings.json, so removing them from the page's text fails."""
    page = open_page(server.url)
    choose_language(page, language)
    count(page, "2026-10-26", "2026-10-30")
    for toggle in ("#help-toggle", "#how-total-toggle", "#how-business-toggle"):
        settle(page, lambda t=toggle: page.click(t))
    shown = [page.locator("#help dd").nth(SECTIONS.index(s)).text_content() for s in WITH_EXAMPLE]
    shown += [page.locator(f"#{panel} .how-text").text_content() for panel in ("how-total", "how-business")]
    assert len(shown) == 5
    assert all(words in text for text in shown), shown


def test_s16_a_failed_request_for_the_examples_shows_no_earlier_example(server, open_page):
    """After a failed GET /api/guide, Help and both "How this is calculated" panels show their texts alone and the
    error says the server did not answer; no example from an earlier opening stands in for one this opening could
    not count."""
    toggles = ("#help-toggle", "#how-total-toggle", "#how-business-toggle")
    page = open_page(server.url)
    count(page, "2026-10-26", "2026-10-30")
    for toggle in toggles:  # open, so the examples are counted and shown
        settle(page, lambda t=toggle: page.click(t))
    expect(page.locator("#help dd").first).to_contain_text("K1")
    expect(page.locator("#how-business .how-text")).to_contain_text("K9a")
    for toggle in toggles:  # close
        page.click(toggle)
    page.route("**/api/guide", lambda route: route.abort())
    settle(page, lambda: page.click("#help-toggle"))
    expect(page.locator("#help dd")).to_have_text([EN[f"help_{s}"] for s in SECTIONS])
    expect(page.locator("#how-total .how-text")).to_have_text(EN["how_total"])
    expect(page.locator("#how-business .how-text")).to_have_text(EN["how_business"])
    expect(page.locator("#error")).to_have_text(EN["error_network"])


def test_the_guide_has_every_section_in_both_languages():
    for key in [f"help_{s}" for s in SECTIONS] + [f"help_{s}_title" for s in SECTIONS]:
        assert EN.get(key) and ES.get(key), key
