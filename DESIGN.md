---
name: Days between dates
description: Counts total and business days between two dates, every convention on screen.
source: the owner's visual standard, applied in full (frontend/src/design-system/, its values copied unchanged)
colors:
  background: "#f4f5f7"
  card: "#ffffff"
  foreground: "#191e29"
  muted-foreground: "#4d5666"
  border: "#e3e6eb"
  border-strong: "#c9cfd8"
  input: "#8b94a3"
  primary: "#2350d8"
  primary-soft: "#e8eeff"
  success: "#1d7a4b"
  warning: "#965a00"
  warning-soft: "#fdf1dc"
  destructive: "#be2a22"
  destructive-soft: "#fcebe9"
  background-dark: "#0f1218"
  card-dark: "#171b23"
  foreground-dark: "#e8ebf1"
  muted-foreground-dark: "#aeb5c2"
  primary-dark: "#7f9dff"
  warning-soft-dark: "#2e2311"
  destructive-dark: "#f2807a"
typography:
  family: "Inter, then the system's sans-serif"
  label: "12px / 16px, 500"
  body: "14px / 20px, 400"
  body-compact: "14px / 18px, 400"
  heading-compact: "14px / 18px, 600"
  heading-2: "16px / 24px, 600"
  heading-3: "20px / 28px, 600"
rounded:
  sm: "4px"
  md: "6px (buttons, fields, toggles)"
  lg: "8px (cards, grids)"
spacing: "Tailwind's 4px unit; Carbon's 2, 4, 8, 12, 16, 24, 32, 40, 48 px"
grid:
  rowHeight: "32px"
  headerHeight: "36px"
---

# Design System: Days between dates

## Overview

This app follows the owner's visual standard in full, and is built on the owner's web starter: Vue 3, Vite and
TypeScript, Tailwind CSS 4 with shadcn-vue, vue-i18n, AG Grid, with FastAPI serving the built page. The standard's files
are in `frontend/src/design-system/`, their values copied unchanged: `tokens.css` (colors, radius, shadows, type and
motion, light and dark), `grid-theme.js` and `grid-theme.css` (AG Grid). Two comment lines are narrowed for publication
(`tokens.css` line 5, `grid-theme.js` line 2); the same change goes back to the standard's source. This file says how
the app applies them; where it and those files disagree, those files win.

The page is a teaching tool, so every convention shows: both counting conventions side by side, the active calendar
named, each notice and each source in view. Simplify visual noise, never analytical capability: columns, units,
notices and sources stay.

## The ten rules, as this app applies them

1. **One cobalt primary per screen.** Count is the one filled cobalt button. Add, Remove and the theme toggle are
   outlined or plain; selected toggles (the calendar, the language) stay neutral. Cobalt also marks links, the active
   tab's underline and focus rings. A page test counts the cobalt-filled buttons.
2. **Status is an icon plus a word.** The storage status in the app bar ("Storage OK", "Storage unavailable"); each
   notice opens with an icon and a word ("Dates swapped", "Past years") before its sentence; an error has its icon.
3. **Green only for status.** The storage chip is the one place that shows `success`.
4. **Grid rows are 32px.** The result's counts and the list of your own holidays are AG Grids with the approved
   theme: 32px rows, a 36px header, no row-height control. They take only the height their rows need, and their rows
   are read, not chosen: row selection is off.
5. **Columns fit their content.** The result's first column ("Days") and the own list's weekday are the flexible
   columns; counts are right-aligned with tabular figures.
6. **Labels sit above fields.** Every field has a `text-label` label in `muted-foreground` above it; the calendar's
   choices are named by the label above them. A page test finds no placeholder standing in for a label.
7. **A chart beside its grid.** The app has no chart. Any chart it adds is drawn with ECharts, beside its grid.
8. **Ranges with their interval.** The app shows no estimated number.
9. **Optimizer actions in one menu.** The app has none.
10. **Light by default, with a working dark mode.** The page opens light whatever the system's setting. The moon and
    sun button in the app bar switches the `.dark` class, and the choice is stored through the API, as the language
    is, so it is kept after a restart and in another browser. A copy in the browser's storage only paints the next
    load in the right mode before the API answers.

## Colors

In `frontend/src`, colors come from `tokens.css`: the starter's unit test `tests/unit/design-system.test.ts` fails on
one written in any other file there, the vendored shadcn-vue stylesheet aside (its `#000` values are masks; its
`oklch()` values derive from `currentColor`). The page is `background`; panels are `card` with a `border` edge and the
card shadow; text is `foreground`, labels and notes `muted-foreground`; fields have an `input` outline; notices sit on
`warning-soft` with a `warning` icon; errors are `destructive` text on `destructive-soft`, framed in `destructive`.
AC15's tests measure every visible text in both modes and both languages, on the count tab and in the guide: each keeps
at least 4.5:1 with its background (WCAG 2.2, 1.4.3). They read whatever color form the browser reports, by painting it
on a canvas. The page's icon, `frontend/public/favicon.svg`, is the one file outside `frontend/src` that holds colors:
an SVG icon cannot read the page's custom properties, so it copies `--primary` (`#2350d8`) and `--primary-foreground`
(`#ffffff`), and a page test checks that both copies match `tokens.css`.

## Typography

Inter, self-hosted (`@fontsource/inter`, weights 400, 500 and 600), on the standard's Carbon scale. The app bar's
title is `heading-compact`; card titles and the guide's section headings `heading-2`; the range above the result
`heading-3`; labels `label`; running text `body`. Counts and dates use tabular figures. The guide's running text keeps
to a readable measure (`max-w-prose`).

## Layout

- **App bar**: 48px, on `card`, with a bottom border: the title, then the storage status, the EN/ES switch and the
  theme toggle. On a narrow screen it wraps to two lines.
- **Main**: at most 72rem wide, 16px padding. A line saying what the app does, then two tabs: *Count* and *Help and
  user guide*, both in view when the page opens.
- **Count tab**: from 1024px wide, two columns: the count form and your own holidays on the left (at most 26rem), the
  result on the right; below them, the sources, in two columns from 768px. Under 1024px, one column.
- **Guide tab**: one column at most 48rem wide: an introduction, the contents (two columns from 640px), then one
  section per feature.

Every button, field and toggle is at least 24px tall (WCAG 2.2, 2.5.8); AC16's tests check it at 375px and 1280px.

## Components

From the starter: `AppShell`, `Field`, `StatusChip`, `DataGrid`, and shadcn-vue's `Button`, `Card`, `Input`, `Label`,
`Tabs` and `ToggleGroup`, with the starter's defaults (a button with no variant is outlined); the grid and the status
chip keep only what this page uses.

- **Count form**: start and end dates (text fields, YYYY-MM-DD), the calendar as a two-choice toggle group, Count.
- **Result**: the active calendar and the range, the notices, the grid of counts, the two "How this is calculated"
  panels (the formula, then a worked example in its own block), and the notes.
- **Your own holidays**: the grid (date, weekday, a Remove button whose name includes its date), then the add form.
- **Error**: one message, shown beside the form that sent a refused value, beside the list when a removal fails, or
  at the top of the page when a language or theme choice is not stored. A field the user typed a refused value into
  is marked `aria-invalid` and points to the message.
- **Help and user guide**: static help with no backend (the app template's User Guide rule). Each worked example is
  written in the text with its numbers; `tests/test_guide.py` reads it from there and counts it again.
- **Announcement**: a visually hidden status region with one message per count, in the page's language.

## Motion

The standard's motion tokens. Controls' color changes use the starter's 150ms transitions; a "How this is calculated"
chevron turns in `--duration-base` with `--ease-in-out`, and flips at once under reduced motion; a result, or a tab's
content, comes in over `--duration-slow` with `--ease-out`, rising 4px times `--motion-scale`, so under reduced
motion only the fade remains.

## Do's and Don'ts

- Do: take every color from `tokens.css`, through Tailwind's utilities (`bg-card`, `text-muted-foreground`).
- Do: keep the standard's files in `frontend/src/design-system/` unchanged. The app derives from them where it must:
  its grids drop AG Grid's 150px minimum body height with `withParams`, outside the approved file.
- Do: give every string an English and a Spanish text in `frontend/src/locales/`; the unit test fails on a key one
  of them lacks.
- Do: write each worked example in the guide's text, from the SPEC's known answers, and give it a test that reads it.
  Keep each feature's explanation to about 150 words, worked examples not counted.
- Do: draw any chart with ECharts.
- Don't: remove a column, a notice or a source to make the page look simpler.
- Don't: add a second cobalt-filled button to a screen.
- Tokens no rule reads yet (the exception in `CLAUDE.md`, *Definition of done*): `--popover`, `--popover-foreground`,
  `--secondary-foreground`, `--accent-foreground`, `--subtle-foreground`, `--chart-1`, `--chart-2`, `--chart-grid`
  and `--duration-fast`. The app has no menu, no hint text and no chart, and its transitions use the starter's
  durations. As of 2026-11-16, the built page reads each of the other 30 custom properties that `tokens.css` declares
  on `:root` (searched the built CSS and JavaScript for `var(<name>)`).
