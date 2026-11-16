"""The User Guide and "How this is calculated" through the page, on the running server (SPEC, S15, S16, AC17). The
guide is static help: its worked examples are written in its text, and tests/test_guide.py counts each one again."""

import pytest
from playwright.sync_api import expect

from test_page import EN, ES, STRINGS, choose_language, count

SECTIONS = ["range", "business", "own", "reversed", "past", "elections", "language", "sources"]
# The worked examples each section shows, by their key, in order; the first of "range" names the dates accepted.
EXAMPLES = {
    "range": ["help_range_dates", "example_total"],
    "business": ["example_weekend", "example_business"],
    "own": ["example_own"],
    "reversed": ["example_reversed"],
}


def section(page, name: str):
    return page.locator(f"#help-body #guide-{name}")


def open_guide(page) -> None:
    page.click("[data-tab=guide]")
    expect(page.locator("#help-body")).to_be_visible()


@pytest.mark.parametrize("language", ["en", "es"])
def test_s15_the_guide_has_one_section_per_feature_with_its_examples(server, open_page, language):
    strings = STRINGS[language]
    page = open_page(server.url)
    choose_language(page, language)
    open_guide(page)
    expect(page.locator("#help-body .guide-intro")).to_have_text(strings["help_intro"])
    titles = [strings[f"help_{s}_title"] for s in SECTIONS]
    expect(page.locator("#help-body .guide-section h2")).to_have_text(titles)
    contents = page.locator("#help-body .guide-contents a")
    expect(contents).to_have_text(titles)
    assert contents.evaluate_all("as => as.map(a => a.getAttribute('href'))") == [f"#guide-{s}" for s in SECTIONS]
    for s in SECTIONS:
        expect(section(page, s).locator(".guide-text")).to_have_text(strings[f"help_{s}"].split("\n\n"))
        examples = section(page, s).locator(".guide-example")
        if s in EXAMPLES:
            expect(examples).to_have_text([strings[key] for key in EXAMPLES[s]])
        else:
            expect(examples).to_have_count(0)


@pytest.mark.parametrize("language", ["en", "es"])
def test_s16_each_result_shows_its_formula_and_a_worked_example(server, open_page, language):
    strings = STRINGS[language]
    page = open_page(server.url)
    choose_language(page, language)
    count(page, "2026-10-26", "2026-10-30")
    for panel, example in (("how-total", "example_total"), ("how-business", "example_business")):
        page.click(f"#{panel}-toggle")
        expect(page.locator(f"#{panel} .how-text")).to_have_text(strings[panel.replace("-", "_")])
        expect(page.locator(f"#{panel} .how-example")).to_be_visible()
        expect(page.locator(f"#{panel} .how-example")).to_have_text(strings[example])


def test_s15_a_language_switch_rewrites_the_open_guide(server, open_page):
    page = open_page(server.url)
    open_guide(page)
    choose_language(page, "es")
    expect(page.locator("#help-body .guide-section h2").first).to_have_text(ES["help_range_title"])
    expect(section(page, "business").locator(".guide-example").first).to_have_text(ES["example_weekend"])


@pytest.mark.parametrize("language", ["en", "es"])
def test_ac17_each_feature_is_explained_in_at_most_150_words(server, open_page, language):
    """Each section of the guide, and each "How this is calculated" formula, as shown, worked examples not counted:
    no more elaborate than the feature it explains (SPEC, S15, AC17; the app template's User Guide rule)."""
    page = open_page(server.url)
    choose_language(page, language)
    count(page, "2026-10-26", "2026-10-30")
    words = "els => els.map(e => [e.id, [...e.querySelectorAll('.guide-text, .how-text')]" \
            ".map(p => p.textContent.split(/\\s+/).filter(Boolean).length).reduce((a, b) => a + b, 0)])"
    parts = page.locator(".how").evaluate_all(words)  # under the result, on the count tab
    open_guide(page)
    parts += page.locator("#help-body .guide-section").evaluate_all(words)
    assert len(parts) == len(SECTIONS) + 2, parts
    long = [p for p in parts if p[1] > 150]
    assert not long, (language, long)
    assert all(p[1] > 0 for p in parts), parts


@pytest.mark.parametrize(
    "language,without,only",
    [("en", "without your own holidays", "as your only own holiday"),
     ("es", "sin sus días festivos propios", "como único día festivo propio")],
)
def test_s16_each_worked_example_says_which_own_holidays_it_counts(server, open_page, language, without, only):
    """The words are written here, not read from the locale files, so removing them from the page's text fails. Every
    example leaves out the user's own holidays, except K10's, which counts one day and says so."""
    page = open_page(server.url)
    choose_language(page, language)
    count(page, "2026-10-26", "2026-10-30")
    page.click("#how-total-toggle")
    page.click("#how-business-toggle")
    shown = page.locator(".how-example").all_text_contents()
    open_guide(page)
    shown += page.locator("#help-body .guide-example").all_text_contents()
    examples = [text.strip() for text in shown if text.strip() != STRINGS[language]["help_range_dates"]]
    assert len(examples) == 7, shown  # five in the guide, two under the result
    own = [text for text in examples if "K10" in text]
    assert len(own) == 1 and only in own[0] and without not in own[0], own
    assert all(without in text for text in examples if text not in own), examples


@pytest.mark.parametrize("width", [1280, 375])
def test_the_guide_is_in_view_when_the_page_opens(server, open_page, width):
    """The guide is a visible control at the top of the page, not below the fold (the owner, 2026-11-15)."""
    page = open_page(server.url)
    page.set_viewport_size({"width": width, "height": 700})
    tab = page.locator("[data-tab=guide]")
    expect(tab).to_be_in_viewport()
    expect(tab).to_have_text(EN["help_title"])


def test_the_guide_has_every_section_in_both_languages():
    keys = ["help_title", "help_intro", "help_contents", "help_range_dates"]
    keys += [f"help_{s}" for s in SECTIONS] + [f"help_{s}_title" for s in SECTIONS]
    for key in keys:
        assert EN.get(key) and ES.get(key), key
