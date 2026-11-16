"""Dark mode and accessibility through the page, on the running server (SPEC, S13, S14; AC15, AC16)."""

import pytest
from playwright.sync_api import expect

from conftest import PAGE_PROBE
from test_page import CELLS, EN, ES, STRINGS, add_holiday, choose_calendar, choose_language, count, settle

# Every visible text on the page with its color and the color behind it, each field's text and each empty field's
# placeholder against the field's own background; the background is the first one up the tree that is not fully
# transparent, or the page's canvas.
CONTRAST = """
() => {
  const rgb = (c) => {
    const m = c.match(/rgba?\\(([^)]+)\\)/);
    if (!m) throw new Error(`unparsed color ${c}`);
    const p = m[1].split(/[\\s,\\/]+/).filter(Boolean).map(Number);
    return { r: p[0], g: p[1], b: p[2], a: p.length > 3 ? p[3] : 1 };
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


def open_scheme(browser, url: str, scheme: str, locale: str = "en-US"):
    page = browser.new_context(locale=locale, color_scheme=scheme).new_page()
    page.add_init_script(PAGE_PROBE)
    page.goto(url)
    page.wait_for_selector("body[data-ready=true]")
    return page


def show_everything(page) -> None:
    """A result with both notices and the note on local election days (and, in Spanish, the note on business days), a
    day of one's own, Help and both formulas open; the field for a new day is left empty, so its placeholder shows."""
    count(page, "2026-01-02", "2025-12-29")  # reversed, and reaching into 2025
    add_holiday(page, "2026-10-28")
    for toggle in ("#help-toggle", "#how-total-toggle", "#how-business-toggle"):
        settle(page, lambda t=toggle: page.click(t))


def color(page, selector: str, prop: str) -> str:
    return page.locator(selector).first.evaluate(f"e => getComputedStyle(e).{prop}")


@pytest.mark.parametrize("scheme", ["light", "dark"])
@pytest.mark.parametrize("language", ["en", "es"])
def test_ac15_every_text_keeps_its_contrast(server, browser, scheme, language):
    page = open_scheme(browser, server.url, scheme)
    choose_language(page, language)
    show_everything(page)
    found = page.evaluate(CONTRAST)
    assert len(found) > 40, found  # the check reached the page's texts
    low = [f for f in found if f["ratio"] < 4.5]
    assert not low, low


@pytest.mark.parametrize("scheme", ["light", "dark"])
@pytest.mark.parametrize("language", ["en", "es"])
def test_ac15_the_error_keeps_its_contrast(server, browser, scheme, language):
    page = open_scheme(browser, server.url, scheme)
    choose_language(page, language)
    count(page, "2026-02-30", "2026-03-02")
    expect(page.locator("#error")).to_be_visible()
    (error,) = [f for f in page.evaluate(CONTRAST) if f["name"] == "error"]
    assert error["ratio"] >= 4.5, error


@pytest.mark.parametrize("scheme", ["light", "dark"])
def test_ac15_the_placeholders_are_measured(server, browser, scheme):
    """Each date field's placeholder is in the contrast check, and keeps its contrast."""
    page = open_scheme(browser, server.url, scheme)
    hints = [f for f in page.evaluate(CONTRAST) if f["name"].endswith("::placeholder")]
    assert {h["name"] for h in hints} == {"start::placeholder", "end::placeholder", "new-day::placeholder"}, hints
    low = [h for h in hints if h["ratio"] < 4.5]
    assert not low, low


def test_ac15_light_keeps_the_colors_design_md_recorded(server, browser):
    page = open_scheme(browser, server.url, "light")
    show_everything(page)
    count(page, "2026-02-30", "2026-03-02")  # the error, after the rest is on screen
    assert color(page, "#error", "color") == "rgb(170, 0, 0)"
    assert color(page, "#notice-swapped", "backgroundColor") == "rgb(255, 244, 214)"
    assert color(page, ".note", "color") == "rgb(68, 68, 68)"
    assert color(page, "#result td", "borderTopColor") == "rgb(153, 153, 153)"
    assert color(page, "#sources-list a", "color") == "rgb(0, 0, 238)"  # the browser's own link color
    assert color(page, "body", "color") == "rgb(0, 0, 0)"


def test_ac15_dark_uses_the_dark_values_of_the_tokens(server, browser):
    page = open_scheme(browser, server.url, "dark")
    count(page, "2026-01-02", "2025-12-29")
    assert color(page, "#notice-swapped", "backgroundColor") == "rgb(46, 35, 17)"
    assert color(page, "#note-local-elections", "color") == "rgb(174, 181, 194)"
    assert color(page, "#result td", "borderTopColor") == "rgb(100, 109, 126)"
    count(page, "2026-02-30", "2026-03-02")
    assert color(page, "#error", "color") == "rgb(242, 128, 122)"


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
    shown = [int(page.locator(cell).text_content()) for cell in CELLS]
    expected = announcement(ES, "us", "2025-12-29", "2026-01-02", shown[:2], shown[2:]) + " " + ES["notice_past_years"]
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
    assert len(heights) >= 11, heights
    short = [h for h in heights if h[1] < 24]
    assert not short, short


@pytest.mark.parametrize("language", ["en", "es"])
def test_ac16_each_label_shares_a_line_with_its_field_at_375_px(server, open_page, language):
    page = open_page(server.url)
    page.set_viewport_size({"width": 375, "height": 900})
    choose_language(page, language)
    pairs = page.locator("label[for]").evaluate_all(
        """els => els.map(l => {
             const a = l.getBoundingClientRect(), b = document.getElementById(l.htmlFor).getBoundingClientRect();
             return [l.htmlFor, a.top + a.height / 2 >= b.top && a.top + a.height / 2 <= b.bottom];
           })"""
    )
    assert len(pairs) == 5, pairs
    apart = [p for p in pairs if not p[1]]
    assert not apart, apart


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
    settle(page, lambda: page.click("#own-list li[data-day='2026-10-28'] button.remove"))
    expect(page.locator("#error")).to_have_text(EN["error_not_found"].replace("{field}", EN["field_day"]))
    assert error_follows(page, "add-form")
    assert invalid_fields(page) == []


def test_a_language_not_stored_shows_at_the_top_of_the_page(server, open_page):
    """The language field is in the page's header: its message shows at the top of the page, not in the count form."""
    page = open_page(server.url)
    page.route("**/api/language", lambda route: route.abort() if route.request.method == "PUT" else route.continue_())
    page.select_option("#language", "es")
    expect(page.locator("#error")).to_have_text(ES["error_language_not_stored"])
    assert page.evaluate("document.querySelector('main').firstElementChild.id") == "error"
    assert invalid_fields(page) == []
