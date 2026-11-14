---
name: Days between dates
description: Counts total and business days between two dates, every convention on screen.
colors:
  error: "#a00"
  notice-bg: "#fff4d6"
  note-text: "#444"
  table-border: "#999"
typography:
  body:
    fontFamily: "system-ui, sans-serif"
    lineHeight: 1.5
  note:
    fontFamily: "system-ui, sans-serif"
    fontSize: "0.95em"
spacing:
  gap: "0.5rem"
  page-gutter: "1rem"
components:
  error-message:
    textColor: "{colors.error}"
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
the motion tokens. The page is a teaching tool, so what matters is that every convention shows: both counting
conventions side by side, the active calendar named, each notice and each source in view. Simplify visual noise, never
analytical capability: columns, units, notices and sources stay.

The owner's visual standard applies its rules to new apps; this app predates it and is not restyled to its palette.
What this app takes from it: charts are drawn with ECharts, and motion uses the standard's tokens.

## Colors

The browser's defaults for text and background. Four colors, each from `style.css`: `error` for the refused-input
message, `notice-bg` behind notices (dates swapped, past years, the live demo's storage), `note-text` for notes, and
`table-border` for the result table's lines.

## Typography

`system-ui, sans-serif` at the browser's size, line height 1.5; notes at 0.95em. Counts use tabular figures
(`font-variant-numeric: tabular-nums`), so digits line up in the result table.

## Layout

A single column at most 48rem wide, centered, with a 1rem gutter on narrow screens. The header and the forms wrap
their controls in a row with a 0.5rem gap. Each field has a visible label.

## Components

- **Result table**: two columns, the start date not counted and both dates counted; rows for total and business days.
  Numbers are right-aligned.
- **Notices and notes**: a notice (tinted background) reports something about this result; a note (muted text)
  explains a convention.
- **Charts**: ECharts, for any chart this app ever adds. The app has no chart today.

## Do's and Don'ts

- Do: draw any chart with ECharts.
- Do: write motion with the tokens in `app/static/tokens.css`: `--duration-fast` 150ms, `--duration-base` 200ms,
  `--duration-slow` 250ms, `--ease-out`, `--ease-in-out`, and every translate or scale distance multiplied by
  `--motion-scale`, which is 0 under reduced motion. UI motion stays under 300ms. As of 2026-11-14, `style.css`,
  `app.js`, `index.html` and `tokens.css` declare no transition or animation (searched for `transition`,
  `animation` and `keyframes`).
- Do: give every string shown on the page an English and a Spanish text in `app/static/strings.json`.
- Don't: remove a column, a notice or a source to make the page look simpler.
- Don't: restyle the page to another palette without the owner's word.
