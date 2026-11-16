"""Dark mode and accessibility through the page, on the running server (SPEC, S13, S14; AC15, AC16; the visual
standard's rules 1, 2, 6 and 10)."""

import pytest
from playwright.sync_api import expect

from conftest import PAGE_PROBE
from test_page import EN, ES, STRINGS, add_holiday, choose_calendar, choose_language, count, settle

# Every visible text on the page with its color and the color behind it, each field's text and each empty field's
# placeholder against the field's own background; the background is the first one up the tree that is not fully
# transparent, or the page's canvas. A color is read by painting it on a canvas, so any form the browser reports
# (rgb(), oklab(), color(srgb ...)) is read the same way; rgb() values come back unchanged.
CONTRAST = """
() => {
  const ctx = document.createElement("canvas").getContext("2d", { willReadFrequently: true });
  const rgb = (c) => {
    ctx.clearRect(0, 0, 1, 1);
    ctx.fillStyle = "rgba(0, 0, 0, 0)";
    ctx.fillStyle = c;
    ctx.fillRect(0, 0, 1, 1);
    const [r, g, b, a] = ctx.getImageData(0, 0, 1, 1).data;
    return { r, g, b, a: a / 255 };
  };
  const probe = document.createElement("div");
  probe.style.backgroundColor = "Canvas";
  document.body.append(probe);
  const canvas = rgb(getComputedStyle(probe).backgroundColor);
  probe.remove();
  const behind = (el) => {
    for (let e = el; e; e = e.parentElement) {
      const c = rgb(getComputedStyle(e).backgroundColor);
      if (c.a > 0) return c;
    }
    return canvas;
  };
  const lum = ({ r, g, b }) => {
    const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  };
  const ratio = (a, b) => {
    const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p);
    return (x + 0.05) / (y + 0.05);
  };
  const shown = (el) => el.getClientRects().length > 0 && !el.closest(".visually-hidden");
  const found = [];
  for (const el of document.querySelectorAll("body *")) {
    const own = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
    const field = el.matches("input, select");
    if ((!own && !field) || !shown(el)) continue;
    const name = el.id || el.className || el.tagName.toLowerCase();
    found.push({ name, ratio: ratio(rgb(getComputedStyle(el).color), behind(el)) });
    if (el.matches("input[placeholder]") && !el.value) {
      const hint = rgb(getComputedStyle(el, "::placeholder").color);
      found.push({ name: `${name}::placeholder`, ratio: ratio(hint, behind(el)) });
    }
  }
  return found;
}
"""


def open_theme(browser, url: str, theme: str, locale: str = "en-US", system: str = "light"):
    """The page in a browser whose system setting is `system`, switched to `theme` with the app bar's toggle."""
    page = browser.new_context(locale=locale, color_scheme=system).new_page()
    page.add_init_script(PAGE_PROBE)
    page.goto(url)
    page.wait_for_selector("body[data-ready=true]")
    if (theme == "dark") != is_dark(page):
        settle(page, lambda: page.click("#theme"))
        page.mouse.move(0, 0)
        page.wait_for_timeout(300)  # the fields' color transitions (at most --duration-slow, 250ms) end first
    assert is_dark(page) == (theme == "dark")
    return page


def is_dark(page) -> bool:
    return page.evaluate("document.documentElement.classList.contains('dark')")


def show_everything(page) -> None:
    """A result with both notices and the note on local election days (and, in Spanish, the note on business days), a
    day of one's own, and both formulas open; the field for a new day is left empty, so its placeholder shows."""
    count(page, "2026-01-02", "2025-12-29")  # reversed, and reaching into 2025
    add_holiday(page, "2026-10-28")
    for toggle in ("#how-total-toggle", "#how-business-toggle"):
        page.click(toggle)
    expect(page.locator("#how-business .how-example")).to_be_visible()


def open_guide(page) -> None:
    page.click("[data-tab=guide]")
    expect(page.locator("#help-body")).to_be_visible()


def color(page, selector: str, prop: str) -> str:
    """A color at rest: the pointer is moved off the page first, and the controls' color transitions (at most
    --duration-slow, 250ms) are given time to end."""
    page.mouse.move(0, 0)
    page.wait_for_timeout(300)
    return page.locator(selector).first.evaluate(f"e => getComputedStyle(e).{prop}")


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("language", ["en", "es"])
def test_ac15_every_text_keeps_its_contrast(server, browser, theme, language):
    page = open_theme(browser, server.url, theme)
    choose_language(page, language)
    show_everything(page)
    found = page.evaluate(CONTRAST)
    assert len(found) > 40, found  # the check reached the count tab's texts
    open_guide(page)
    guide = page.evaluate(CONTRAST)
    assert len(guide) > 20, guide  # and the guide's
    low = [f for f in found + guide if f["ratio"] < 4.5]
    assert not low, low


@pytest.mark.parametrize("theme", ["light", "dark"])
@pytest.mark.parametrize("language", ["en", "es"])
def test_ac15_the_error_keeps_its_contrast(server, browser, theme, language):
    page = open_theme(browser, server.url, theme)
    choose_language(page, language)
    count(page, "2026-02-30", "2026-03-02")
    expect(page.locator("#error")).to_be_visible()
    (error,) = [f for f in page.evaluate(CONTRAST) if f["name"] == "error"]
    assert error["ratio"] >= 4.5, error


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_ac15_the_placeholders_are_measured(server, browser, theme):
    """Each date field's placeholder is in the contrast check, and keeps its contrast."""
    page = open_theme(browser, server.url, theme)
    hints = [f for f in page.evaluate(CONTRAST) if f["name"].endswith("::placeholder")]
    assert {h["name"] for h in hints} == {"start::placeholder", "end::placeholder", "new-day::placeholder"}, hints
    low = [h for h in hints if h["ratio"] < 4.5]
    assert not low, low


# The visual standard's tokens (tokens.css), light and dark, as the browser reports them.
LIGHT = {"background": "rgb(244, 245, 247)", "card": "rgb(255, 255, 255)", "foreground": "rgb(25, 30, 41)",
         "muted": "rgb(77, 86, 102)", "primary": "rgb(35, 80, 216)", "destructive": "rgb(190, 42, 34)",
         "warning_soft": "rgb(253, 241, 220)"}
DARK = {"background": "rgb(15, 18, 24)", "card": "rgb(23, 27, 35)", "foreground": "rgb(232, 235, 241)",
        "muted": "rgb(174, 181, 194)", "primary": "rgb(127, 157, 255)", "destructive": "rgb(242, 128, 122)",
        "warning_soft": "rgb(46, 35, 17)"}


@pytest.mark.parametrize("theme,tokens", [("light", LIGHT), ("dark", DARK)])
def test_ac15_the_page_uses_the_standards_tokens(server, browser, theme, tokens):
    page = open_theme(browser, server.url, theme)
    show_everything(page)
    assert color(page, "body", "backgroundColor") == tokens["background"]
    assert color(page, "body", "color") == tokens["foreground"]
    assert color(page, "#result", "backgroundColor") == tokens["card"]
    assert color(page, "#count", "backgroundColor") == tokens["primary"]
    assert color(page, "#notice-swapped", "backgroundColor") == tokens["warning_soft"]
    assert color(page, ".note", "color") == tokens["muted"]
    assert color(page, "#sources-list a", "color") == tokens["primary"]
    count(page, "2026-02-30", "2026-03-02")  # the error, after the rest is on screen
    assert color(page, "#error", "color") == tokens["destructive"]


@pytest.mark.parametrize("theme", ["light", "dark"])
def test_rule_1_one_cobalt_filled_button_per_screen(server, browser, theme):
    """The visual standard's rule 1: Count is the screen's one primary button; every other button is outlined."""
    page = open_theme(browser, server.url, theme)
    show_everything(page)
    primary = (LIGHT if theme == "light" else DARK)["primary"]
    filled = page.locator("button").evaluate_all(
        f"bs => bs.filter(b => b.getClientRects().length && getComputedStyle(b).backgroundColor === '{primary}')"
        ".map(b => b.id || b.textContent.trim())"
    )
    assert filled == ["count"], filled


def test_rule_10_the_page_opens_light_even_when_the_system_is_dark(server, browser):
    """Nothing stored, a browser set to dark: the page opens light, as it loads, with no toggle touched."""
    page = browser.new_context(color_scheme="dark").new_page()
    page.add_init_script(PAGE_PROBE)
    page.goto(server.url)
    page.wait_for_selector("body[data-ready=true]")
    assert not is_dark(page)
    assert color(page, "body", "backgroundColor") == LIGHT["background"]
    expect(page.locator("#theme")).to_have_attribute("aria-label", EN["theme_to_dark"])


def test_rule_10_the_theme_toggle_is_remembered_through_the_api(server, open_page):
    page = open_page(server.url)
    toggle = page.locator("#theme")
    expect(toggle).to_have_attribute("aria-label", EN["theme_to_dark"])
    settle(page, lambda: toggle.click())
    assert is_dark(page)
    expect(toggle).to_have_attribute("aria-label", EN["theme_to_light"])
    assert server.call("GET", "/api/theme") == (200, {"theme": "dark"})
    server.restart()
    page = open_page(server.url)  # a new browser, with nothing of its own stored: the API's choice wins
    assert is_dark(page)
    settle(page, lambda: page.click("#theme"))
    assert not is_dark(page)
    assert server.call("GET", "/api/theme") == (200, {"theme": "light"})


def test_rule_10_a_theme_not_stored_is_said_and_kept_on_screen(server, open_page):
    page = open_page(server.url)
    page.route("**/api/theme", lambda route: route.abort() if route.request.method == "PUT" else route.continue_())
    page.click("#theme")
    expect(page.locator("#error")).to_have_text(EN["error_theme_not_stored"])
    assert is_dark(page)
    assert page.evaluate("document.querySelector('main').firstElementChild.id") == "error"


def announcement(strings: dict, calendar: str, start: str, end: str, total: tuple, business: tuple) -> str:
    return (
        strings["announce_result"]
        .replace("{calendar}", strings[f"calendar_{calendar}"])
        .replace("{start}", start).replace("{end}", end)
        .replace("{total_snc}", str(total[0])).replace("{total_bc}", str(total[1]))
        .replace("{business_snc}", str(business[0])).replace("{business_bc}", str(business[1]))
    )


def test_ac16_a_count_is_announced_with_its_notices_in_the_pages_language(server, open_page):
    """Ranges in 2150, the last year accepted, carry no past-years notice before then, so the expected text holds over
    time (as tests/test_page.py does for S9); a range reaching into 2025 carries it."""
    page = open_page(server.url)
    region = page.locator("#announce")
    expect(region).to_have_attribute("role", "status")
    choose_calendar(page, "us")
    count(page, "2150-12-24", "2150-12-31")  # K11
    expect(region).to_have_text(announcement(EN, "us", "2150-12-24", "2150-12-31", (7, 8), (4, 5)))
    count(page, "2150-12-31", "2150-12-24")  # K11 reversed: swapped, so the notice is announced too
    expected = announcement(EN, "us", "2150-12-24", "2150-12-31", (7, 8), (4, 5)) + " " + EN["notice_swapped"]
    expect(region).to_have_text(expected)
    choose_language(page, "es")
    expected = announcement(ES, "us", "2150-12-24", "2150-12-31", (7, 8), (4, 5)) + " " + ES["notice_swapped"]
    expect(region).to_have_text(expected)
    count(page, "2025-12-29", "2026-01-02")  # reaches into 2025: the past-years notice is announced
    _, body = server.call("GET", "/api/count?calendar=us&start=2025-12-29&end=2026-01-02")  # the same count, asked
    total = (body["total"]["start_not_counted"], body["total"]["both_counted"])
    business = (body["business"]["start_not_counted"], body["business"]["both_counted"])
    expected = announcement(ES, "us", "2025-12-29", "2026-01-02", total, business) + " " + ES["notice_past_years"]
    expect(region).to_have_text(expected)
    count(page, "2026-02-30", "2026-03-02")  # refused: the error is the alert, no result is announced
    expect(region).to_have_text("")


def test_ac16_each_remove_button_names_its_date(server, open_page):
    page = open_page(server.url)
    add_holiday(page, "2026-10-28")
    add_holiday(page, "2026-11-03")
    for day in ("2026-10-28", "2026-11-03"):
        expect(page.get_by_role("button", name=EN["remove_label"].replace("{day}", day), exact=True)).to_be_visible()
    choose_language(page, "es")
    for day in ("2026-10-28", "2026-11-03"):
        expect(page.get_by_role("button", name=ES["remove_label"].replace("{day}", day), exact=True)).to_be_visible()


@pytest.mark.parametrize("width", [1280, 375])
def test_ac16_every_control_is_at_least_24_px_tall(server, open_page, width):
    page = open_page(server.url)
    page.set_viewport_size({"width": width, "height": 900})
    show_everything(page)
    heights = page.locator("button, input, select, summary").evaluate_all(
        """els => els.filter(e => e.getClientRects().length)
                    .map(e => [e.id || e.className, e.getBoundingClientRect().height])"""
    )
    assert len(heights) >= 12, heights
    short = [h for h in heights if h[1] < 24]
    assert not short, short


@pytest.mark.parametrize("width", [1280, 375])
@pytest.mark.parametrize("language", ["en", "es"])
def test_ac16_each_label_sits_above_its_field(server, open_page, width, language):
    """The visual standard's rule 6: a label above each field, never beside it or inside it; each group of choices
    (the calendar) is named by the label above it."""
    page = open_page(server.url)
    page.set_viewport_size({"width": width, "height": 900})
    choose_language(page, language)
    pairs = page.locator("label[for], [id$=-label]").evaluate_all(
        """els => els.map(l => {
             const field = l.htmlFor ? document.getElementById(l.htmlFor)
                                     : document.querySelector(`[aria-labelledby="${l.id}"]`);
             const a = l.getBoundingClientRect(), b = field.getBoundingClientRect();
             return [field.id, a.bottom <= b.top + 1 && a.left < b.right && b.left < a.right];
           })"""
    )
    assert sorted(p[0] for p in pairs) == ["calendar", "end", "new-day", "start"], pairs
    apart = [p for p in pairs if not p[1]]
    assert not apart, apart


def test_no_placeholder_is_a_fields_only_label(server, open_page):
    """Rule 6's check: each field with a placeholder also has a label of its own."""
    page = open_page(server.url)
    unlabelled = page.locator("input[placeholder]").evaluate_all(
        "els => els.filter(e => !document.querySelector(`label[for='${e.id}']`)).map(e => e.id)"
    )
    assert unlabelled == []


def invalid_fields(page) -> list[str]:
    return page.locator("[aria-invalid=true]").evaluate_all("els => els.map(e => e.id)")


def error_follows(page, form: str) -> bool:
    return page.evaluate(f"document.getElementById('{form}').nextElementSibling?.id === 'error'")


def test_an_error_marks_its_field_and_shows_beside_its_form(server, open_page):
    """A refused date marks its field invalid and points it to the message, which shows beside the form that sent it;
    the next accepted request clears the mark (E1)."""
    page = open_page(server.url)
    count(page, "2026-02-30", "2026-03-02")
    assert invalid_fields(page) == ["start"]
    expect(page.locator("#start")).to_have_attribute("aria-describedby", "error")
    assert error_follows(page, "count-form")
    add_holiday(page, "2026-02-30")
    assert invalid_fields(page) == ["new-day"]
    assert error_follows(page, "add-form")
    expect(page.locator("#error")).to_be_visible()
    count(page, "2026-10-26", "2026-10-30")
    assert invalid_fields(page) == []
    expect(page.locator("#error")).to_be_hidden()
    expect(page.locator("#start")).not_to_have_attribute("aria-describedby", "error")


def test_a_failed_removal_marks_no_field_and_shows_beside_the_list(server, open_page):
    """A day removed elsewhere (another tab) cannot be removed again: the message shows beside the list and its add
    form, and the empty field for a new day is not marked invalid, since the user typed nothing there."""
    page = open_page(server.url)
    add_holiday(page, "2026-10-28")
    status, _ = server.call("DELETE", "/api/holidays/mx/2026-10-28")
    assert status == 204
    settle(page, lambda: page.click("#own-list .ag-row[row-id='2026-10-28'] button.remove"))
    expect(page.locator("#error")).to_have_text(EN["error_not_found"].replace("{field}", EN["field_day"]))
    assert error_follows(page, "add-form")
    assert invalid_fields(page) == []


def test_a_language_not_stored_shows_at_the_top_of_the_page(server, open_page):
    """The language field is in the page's header: its message shows at the top of the page, not in the count form."""
    page = open_page(server.url)
    page.route("**/api/language", lambda route: route.abort() if route.request.method == "PUT" else route.continue_())
    page.click("#language [data-value=es]")
    expect(page.locator("#error")).to_have_text(ES["error_language_not_stored"])
    assert page.evaluate("document.querySelector('main').firstElementChild.id") == "error"
    assert invalid_fields(page) == []
