"""Help, the user guide, and "How this is calculated" through the page, on the running server (SPEC, S15, S16;
AC17, AC18)."""

import re
from datetime import date

import pytest
from playwright.sync_api import expect

from test_page import EN, ES, STRINGS, choose_language, count, settle

SECTIONS = ["range", "business", "own", "reversed", "past", "elections", "language", "sources"]
# The worked examples each section shows, by their role in GET /api/guide, in order.
EXAMPLES = {"range": ["total"], "business": ["weekend", "business"], "own": ["own"], "reversed": ["reversed"]}
# The weekday names the page writes beside a date, Monday first: the browser's own (Intl), in each language.
WEEKDAYS = {
    "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    "es": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"],
}
# The dates the app accepts (SPEC, Expectations), written here, not read from the app.
FIRST, LAST = "1950-01-01", "2150-12-31"


def is_guide(key: str) -> bool:
    return key.startswith(("help_", "how_", "example_"))


def fill(template: str, **values) -> str:
    for name, value in values.items():
        template = template.replace("{" + name + "}", str(value))
    assert "{" not in template, template
    return template


def weekday(language: str, day: str) -> str:
    return WEEKDAYS[language][date.fromisoformat(day).weekday()]


def example_text(language: str, example: dict) -> str:
    """The page's sentence for one worked example, from the numbers the API counted."""
    strings = STRINGS[language]
    common = {"known": example["known_answer"], "start": example["start"], "end": example["end"]}
    total, business = example["total"], example["business"]
    role = example["role"]
    if role == "total":
        return fill(strings["example_total"], snc=total["start_not_counted"], bc=total["both_counted"], **common)
    if role == "weekend":
        return fill(
            strings["example_weekend"], start_weekday=weekday(language, example["start"]),
            end_weekday=weekday(language, example["end"]), total_snc=total["start_not_counted"],
            total_bc=total["both_counted"], snc=business["start_not_counted"], bc=business["both_counted"], **common,
        )
    if role == "business":
        mf = example["monday_to_friday"]
        return fill(
            strings["example_business"], calendar=strings[f"calendar_{example['calendar']}"],
            mf_snc=mf["start_not_counted"], mf_bc=mf["both_counted"], excluded=", ".join(example["excluded"]),
            snc=business["start_not_counted"], bc=business["both_counted"], **common,
        )
    if role == "own":
        (day,) = example["own_holidays"]
        return fill(
            strings["example_own"], day=day, weekday=weekday(language, day), snc=business["start_not_counted"],
            bc=business["both_counted"], **common,
        )
    return fill(
        strings["example_reversed"], entered_start=example["entered"]["start"],
        entered_end=example["entered"]["end"], **common,
    )


def examples_by_role(server) -> dict:
    status, body = server.call("GET", "/api/guide")
    assert status == 200, body
    return {e["role"]: e for e in body["examples"]}


def section(page, name: str):
    return page.locator(f"#help #guide-{name}")


@pytest.mark.parametrize("language", ["en", "es"])
def test_s15_help_has_one_section_per_feature_with_its_examples(server, open_page, language):
    strings = STRINGS[language]
    page = open_page(server.url)
    choose_language(page, language)
    settle(page, lambda: page.click("#help-toggle"))
    examples = examples_by_role(server)
    expect(page.locator("#help .guide-intro")).to_have_text(strings["help_intro"])
    titles = [strings[f"help_{s}_title"] for s in SECTIONS]
    expect(page.locator("#help .guide-section h2")).to_have_text(titles)
    contents = page.locator("#help .guide-contents a")
    expect(contents).to_have_text(titles)
    assert contents.evaluate_all("as => as.map(a => a.getAttribute('href'))") == [f"#guide-{s}" for s in SECTIONS]
    for s in SECTIONS:
        expect(section(page, s).locator(".guide-text")).to_have_text(strings[f"help_{s}"].split("\n\n"))
        shown = [example_text(language, examples[role]) for role in EXAMPLES.get(s, [])]
        if s == "range":
            shown.insert(0, fill(strings["help_range_dates"], first=FIRST, last=LAST))
        if shown:
            expect(section(page, s).locator(".guide-example")).to_have_text(shown)
        else:
            expect(section(page, s).locator(".guide-example")).to_have_count(0)


@pytest.mark.parametrize("language", ["en", "es"])
def test_s16_each_result_shows_its_formula_and_a_worked_example(server, open_page, language):
    strings = STRINGS[language]
    page = open_page(server.url)
    choose_language(page, language)
    count(page, "2026-10-26", "2026-10-30")
    examples = examples_by_role(server)
    for panel, role in (("how-total", "total"), ("how-business", "business")):
        settle(page, lambda p=panel: page.click(f"#{p}-toggle"))
        expect(page.locator(f"#{panel} .how-text")).to_have_text(strings[panel.replace("-", "_")])
        expect(page.locator(f"#{panel} .how-example")).to_be_visible()
        expect(page.locator(f"#{panel} .how-example")).to_have_text(example_text(language, examples[role]))


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
    expect(page.locator("#help .guide-section h2").first).to_have_text(ES["help_range_title"])
    expect(section(page, "range").locator(".guide-text").first).to_have_text(ES["help_range"].split("\n\n")[0])
    expect(section(page, "business").locator(".guide-example").first).to_contain_text(WEEKDAYS["es"][4])  # viernes


@pytest.mark.parametrize("language", ["en", "es"])
def test_ac17_each_part_of_the_guide_holds_at_most_150_words(server, open_page, language):
    """Each section of Help, and each "How this is calculated", as shown with its examples: no more elaborate than the
    feature it explains (SPEC, S15, AC17)."""
    page = open_page(server.url)
    choose_language(page, language)
    count(page, "2026-10-26", "2026-10-30")
    for toggle in ("#help-toggle", "#how-total-toggle", "#how-business-toggle"):
        settle(page, lambda t=toggle: page.click(t))
    parts = page.locator("#help .guide-section, .how").evaluate_all(
        "els => els.map(e => [e.id, e.innerText.split(/\\s+/).filter(Boolean).length])"
    )
    assert len(parts) == len(SECTIONS) + 2, parts
    long = [p for p in parts if p[1] > 150]
    assert not long, (language, long)
    assert all(p[1] > 0 for p in parts), parts


def test_ac18_the_guide_writes_no_digit_of_its_own():
    """The guide's strings hold no digit: each figure in Help and "How this is calculated" is filled in from the API's
    count, which tests/test_guide.py checks against the known answers; a figure typed into the text could drift from
    the code."""
    for language in ("en", "es"):
        typed = {k: v for k, v in STRINGS[language].items() if is_guide(k) and re.search(r"\d", v)}
        assert not typed, (language, typed)


@pytest.mark.parametrize(
    "language,without,only",
    [("en", "without your own holidays", "as your only own holiday"),
     ("es", "sin sus días festivos propios", "como único día festivo propio")],
)
def test_s16_each_worked_example_says_which_own_holidays_it_counts(server, open_page, language, without, only):
    """The words are written here, not read from strings.json, so removing them from the page's text fails. Every
    example leaves out the user's own holidays, except K10's, which counts one day and says so."""
    page = open_page(server.url)
    choose_language(page, language)
    count(page, "2026-10-26", "2026-10-30")
    for toggle in ("#help-toggle", "#how-total-toggle", "#how-business-toggle"):
        settle(page, lambda t=toggle: page.click(t))
    shown = page.locator("#help .guide-example, .how-example").all_text_contents()
    dates = fill(STRINGS[language]["help_range_dates"], first=FIRST, last=LAST)
    examples = [text for text in shown if text != dates]
    assert len(examples) == 7, shown  # five in Help, two under the result
    own = [text for text in examples if "K10" in text]
    assert len(own) == 1 and only in own[0] and without not in own[0], own
    assert all(without in text for text in examples if text not in own), examples


def test_s16_a_failed_request_for_the_examples_shows_no_earlier_example(server, open_page):
    """After a failed GET /api/guide, Help and both "How this is calculated" panels show their texts alone and the
    error says the server did not answer; no example from an earlier opening stands in for one this opening could
    not count."""
    toggles = ("#help-toggle", "#how-total-toggle", "#how-business-toggle")
    page = open_page(server.url)
    count(page, "2026-10-26", "2026-10-30")
    for toggle in toggles:  # open, so the examples are counted and shown
        settle(page, lambda t=toggle: page.click(t))
    expect(section(page, "range").locator(".guide-example").nth(1)).to_contain_text("K1")
    expect(page.locator("#how-business .how-example")).to_contain_text("K9a")
    for toggle in toggles:  # close
        page.click(toggle)
    page.route("**/api/guide", lambda route: route.abort())
    settle(page, lambda: page.click("#help-toggle"))
    expect(page.locator("#help .guide-text")).to_have_text(
        [text for s in SECTIONS for text in EN[f"help_{s}"].split("\n\n")]
    )
    expect(page.locator("#help .guide-example")).to_have_count(0)
    expect(page.locator("#how-total .how-text")).to_have_text(EN["how_total"])
    expect(page.locator("#how-total .how-example")).to_be_hidden()
    expect(page.locator("#how-business .how-example")).to_be_hidden()
    expect(page.locator("#error")).to_have_text(EN["error_network"])


@pytest.mark.parametrize("width", [1280, 375])
def test_the_guide_is_in_view_when_the_page_opens(server, open_page, width):
    """Help is a visible control at the top of the page, not below the fold (the owner, 2026-11-15)."""
    page = open_page(server.url)
    page.set_viewport_size({"width": width, "height": 700})
    toggle = page.locator("#help-toggle")
    expect(toggle).to_be_in_viewport()
    expect(toggle).to_have_text(EN["help_title"])


def test_the_guide_has_every_section_in_both_languages():
    keys = ["help_title", "help_intro", "help_contents", "help_range_dates"]
    keys += [f"help_{s}" for s in SECTIONS] + [f"help_{s}_title" for s in SECTIONS]
    for key in keys:
        assert EN.get(key) and ES.get(key), key
