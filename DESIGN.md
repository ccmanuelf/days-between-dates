---
name: Days between dates
description: Counts total and business days between two dates, every convention on screen.
colors:
  error: "#a00"
  notice-bg: "#fff4d6"
  note-text: "#444"
  table-border: "#999"
  error-dark: "#f2807a"
  notice-bg-dark: "#2e2311"
  note-text-dark: "#aeb5c2"
  table-border-dark: "#646d7e"
typography:
  body:
    fontFamily: "system-ui, sans-serif"
    lineHeight: 1.5
  note:
    fontFamily: "system-ui, sans-serif"
    fontSize: "0.95em"
  error:
    fontFamily: "system-ui, sans-serif"
    fontWeight: 600
spacing:
  gap: "0.5rem"
  page-gutter: "1rem"
components:
  error-message:
    textColor: "{colors.error}"
    typography: "{typography.error}"
  notice:
    backgroundColor: "{colors.notice-bg}"
    padding: "0.5rem"
  note:
    textColor: "{colors.note-text}"
    typography: "{typography.note}"
---

# Design System: Days between dates

## Overview

One plain page, no framework and no build step: `app/static/index.html`, `style.css` for the look, `tokens.css` for
the color and motion tokens. The page is a teaching tool, so what matters is that every convention shows: both counting
conventions side by side, the active calendar named, each notice and each source in view. Simplify visual noise, never
analytical capability: columns, units, notices and sources stay.

The owner's visual standard applies its rules to new apps; this app predates it and is not restyled to its palette.
What this app takes from it: charts are drawn with ECharts, motion uses the standard's tokens, and dark mode uses
four of its dark color values.

## Colors

The browser's defaults for text, background and links, which `color-scheme: light dark` turns dark when the
system is dark (SPEC, S13). Four color tokens in `tokens.css`, read by `style.css`: `--error` for every error message
(refused input, storage, network, a language choice not stored), `--notice-bg` behind notices (dates swapped, past
years), `--note-text` for notes, and `--table-border` for the result table's lines. Their
light values are the page's colors as built; their dark values (`*-dark` above) are the owner's visual standard's
dark destructive, warning-soft, muted-foreground and input. In dark mode the fields' placeholders take
`--note-text`; in light mode they keep the browser's own. AC15's tests measure each visible text, field and
placeholder on a page with a result, both notices, the notes, a day of one's own, Help and both formulas open, plus
the error, in both schemes and both languages: each keeps at least 4.5:1 with its background
(WCAG 2.2, 1.4.3).

## Typography

`system-ui, sans-serif` at the browser's size, line height 1.5; notes at 0.95em; error messages at weight 600.
Counts use tabular figures (`font-variant-numeric: tabular-nums`), so digits line up in the result table.

## Layout

A single column at most 48rem wide, centered, with a 1rem gutter on narrow screens. The header and the forms wrap
their controls in a row with a 0.5rem gap. Each field has a visible label, kept with its field in one group
(`.field`), so a narrow screen wraps the group as one; at 375px each label shares a line with its field. Every
button, field, list and panel toggle is at least 24px tall (WCAG 2.2, 2.5.8). AC16's tests check the heights at
375px and 1280px wide, and the label groups at 375px.

## Components

- **Result table**: two columns, the start date not counted and both dates counted; rows for total and business days.
  Numbers are right-aligned.
- **Notices and notes**: a notice (tinted background) reports something about this result; a note (muted text)
  explains a convention.
- **Help**: a disclosure under the header, one term and one short text for each feature SPEC S15 lists; three of
  them end with a worked example.
- **How this is calculated**: one disclosure under the result table for total days and one for business days: the
  formula, then a worked example. The examples' numbers come from the API (`/api/guide`), counted when a panel
  opens; the guide's strings hold no digit of their own.
- **Announcement**: a visually hidden status region (`role="status"`, `aria-atomic="true"`) that holds one message
  per count, with its notices, in the page's language.
- **Charts**: ECharts, for any chart this app ever adds. The app has no chart today.

## Do's and Don'ts

- Do: draw any chart with ECharts.
- Do: write motion with the tokens in `app/static/tokens.css`: `--duration-fast` 150ms, `--duration-base` 200ms,
  `--duration-slow` 250ms, `--ease-out`, `--ease-in-out`, and every translate or scale distance multiplied by
  `--motion-scale`, which is 0 under reduced motion. UI motion stays under 300ms.
- Tokens no rule reads yet (the exception in `CLAUDE.md`, *Definition of done*): all six motion tokens. As of
  2026-11-14, `style.css`, `app.js` and `index.html` read none of them (searched for the six token names), and with
  `tokens.css` they declare no transition or animation (searched for `transition`, `animation` and `keyframes`). The
  four color tokens are read by `style.css`.
- Do: give every string shown on the page an English and a Spanish text in `app/static/strings.json`.
- Do: keep the guide's text (Help and How this is calculated) shorter than the rest of the page's text, and write
  no digit into it: the figures come from the API's count (AC17, AC18).
- Don't: remove a column, a notice or a source to make the page look simpler.
- Don't: restyle the page to another palette without the owner's word.
