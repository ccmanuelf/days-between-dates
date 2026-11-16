---
name: Days between dates
description: Counts total and business days between two dates, every convention on screen.
colors:
  error: "#a00"
  notice-bg: "#fff4d6"
  note-text: "#444"
  table-border: "#999"
  surface: "#f6f7f9"
  line: "#dcdfe4"
  control-border: "#767676"
  error-dark: "#f2807a"
  notice-bg-dark: "#2e2311"
  note-text-dark: "#aeb5c2"
  table-border-dark: "#646d7e"
  surface-dark: "#1b1d22"
  line-dark: "#30343b"
  control-border-dark: "#8b919c"
typography:
  body:
    fontFamily: "system-ui, sans-serif"
    lineHeight: 1.5
  title:
    fontFamily: "system-ui, sans-serif"
    fontSize: "clamp(1.75rem, 1.45rem + 1.2vw, 2.25rem)"
    fontWeight: 700
  count:
    fontFamily: "system-ui, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 700
  label-small:
    fontFamily: "system-ui, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 600
  note:
    fontFamily: "system-ui, sans-serif"
    fontSize: "0.95em"
  error:
    fontFamily: "system-ui, sans-serif"
    fontWeight: 600
spacing:
  space-1: "0.25rem"
  space-2: "0.5rem"
  space-3: "0.75rem"
  space-4: "1rem"
  space-5: "1.5rem"
  space-6: "2rem"
  space-7: "3rem"
  page-gutter: "1rem"
rounded:
  radius: "0.75rem"
  radius-sm: "0.5rem"
components:
  card:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.radius}"
    padding: "1.5rem"
  button-primary:
    backgroundColor: "CanvasText"
    textColor: "Canvas"
    rounded: "{rounded.radius-sm}"
    height: "2.5rem"
  button:
    textColor: "CanvasText"
    rounded: "{rounded.radius-sm}"
    height: "2.5rem"
  field:
    backgroundColor: "Canvas"
    textColor: "CanvasText"
    rounded: "{rounded.radius-sm}"
    height: "2.5rem"
  error-message:
    textColor: "{colors.error}"
    typography: "{typography.error}"
  notice:
    backgroundColor: "{colors.notice-bg}"
    padding: "0.75rem 1rem"
  note:
    textColor: "{colors.note-text}"
    typography: "{typography.note}"
---

# Design System: Days between dates

## Overview

One plain page, no framework and no build step: `app/static/index.html`, `style.css` for the look, `tokens.css` for
the tokens it reads. The page is a teaching tool, so what matters is that every convention shows: both counting
conventions side by side, the active calendar named, each notice and each source in view. Simplify visual noise, never
analytical capability: columns, units, notices and sources stay.

The look is quiet and monochrome: the browser's own canvas and text, neutral gray cards, black (in dark mode, white)
primary buttons, and color where it means something: the error in red, a notice on its warm tint, links in the
browser's blue. Restyled 2026-11-15 on the owner's word, within this file's palette.

The owner's visual standard applies its rules to new apps; this app predates it and is not restyled to its palette.
What this app takes from it: charts are drawn with ECharts, motion uses the standard's tokens, and dark mode uses
four of its dark color values.

## Colors

The browser's defaults for text, background and links (`Canvas`, `CanvasText`, its link colors), which
`color-scheme: light dark` turns dark when the system is dark (SPEC, S13). Seven color tokens in `tokens.css`, read
by `style.css`:

- `--error` for every error message (refused input, storage, network, a language choice not stored) and the border
  of the field it names;
- `--notice-bg` behind notices (dates swapped, past years);
- `--note-text` for notes, the tagline, the small labels over the table and the guide's contents;
- `--table-border` for the result table's lines;
- `--surface`, a card's background; `--line`, the lines that divide a card and its edge;
- `--control-border`, the border of a field or a secondary button, at least 3:1 against what is around it (WCAG 2.2,
  1.4.11).

The first four tokens' light values are the page's colors as built; their dark values (`*-dark` above) are the owner's
visual standard's dark destructive, warning-soft, muted-foreground and input. The last three are neutral grays chosen
for this restyle. Fields, the guide's contents and its examples sit on `Canvas`, so in light mode the fields'
placeholders keep the browser's own color; in dark mode they take `--note-text`. AC15's tests measure each visible
text, field and placeholder on a page with a result, both notices, the notes, a day of one's own, Help and both
formulas open, plus the error, in both schemes and both languages: each keeps at least 4.5:1 with its background
(WCAG 2.2, 1.4.3). In `style.css`, each `background-color` is a token, a system color, `currentColor` or
`transparent` (searched for `background`), so the tests can read it as an RGB value; a `color-mix()` is reported in
another color space and is not used.

## Typography

`system-ui, sans-serif`, line height 1.5, at the browser's size. The title is fluid, from 1.75rem to 2.25rem, weight
700, with tighter letter spacing; section headings 1.25rem, the guide's headings 1.125rem. The counts in the result
table are 1.5rem, weight 700. Small labels (the active calendar, the table's column heads, the guide's contents) are
0.875rem, weight 600; the first and the last are in capitals with a little letter spacing. Notes at 0.95em; error
messages at weight 600. Counts and dates use tabular figures (`font-variant-numeric: tabular-nums`), so digits line
up. Running text in the guide is kept to 65 characters a line.

## Layout

A single column at most 48rem wide, centered, with a 1rem gutter. Spacing comes from one scale, `--space-1` to
`--space-7` (0.25rem to 3rem).

- **Masthead**: the title and its tagline, then the language field; on a wide screen the field moves to the title's
  line when there is room.
- **Cards**: Help, the count form, the result and your own holidays are cards (`--surface`, a `--line` edge, 0.75rem
  corners, 1.5rem padding, 1rem under 30rem wide), 1.5rem apart. The sources sit below them on the page itself, in
  two columns when there is room.
- **Forms**: a grid of two columns, labels in the first and their fields in the next, each label on its field's line;
  the button sits under the fields. Fields are 2.5rem tall and at most 20rem wide.

Every button, field, list and panel toggle is at least 24px tall (WCAG 2.2, 2.5.8). AC16's tests check the heights at
375px and 1280px wide, and the label groups at 375px.

## Components

- **Buttons**: the primary button (Count, Add) is filled with the text color, its label in the page's color; on hover
  it takes `--note-text`. A secondary button (Remove) has a `--control-border` outline and fills with the page's
  color on hover. A press scales a button to 97%, times `--motion-scale`.
- **Fields**: `Canvas` with a `--control-border` edge; a select draws its own arrow in the text color.
- **Focus**: a control reached by keyboard shows a 2px outline in the text color, 2px out (`:focus-visible`).
- **Result**: the active calendar (small, in capitals) and the range on one line, then the notices, then the table:
  two columns, the start date not counted and both dates counted; rows for total and business days, the counts
  right-aligned. The notes close the card.
- **Notices and notes**: a notice (tinted background, an information icon) reports something about this result; a
  note (muted text) explains a convention.
- **Error**: an alert icon and the message in `--error`, framed in the same color, on the page's color. It shows
  beside the form that sent the refused value; the field it names gets `aria-invalid` and a red edge, and points to
  the message with `aria-describedby`; the next accepted request clears both.
- **Help and user guide**: a card at the top of the page, closed until opened; its toggle carries a question-mark
  badge and a chevron that turns when it opens. Inside: a short introduction, the contents (a numbered list of links,
  in two columns when there is room), then one section per feature SPEC S15 lists, each with its heading and its text,
  and its worked examples where it has any, each example in its own block on `Canvas`. The section on a range also
  names the first and last dates accepted.
- **How this is calculated**: one disclosure under the result table for total days and one for business days: the
  formula, then a worked example in its own block.
- **Worked examples**: their numbers come from the API (`/api/guide`), counted when a panel opens; a weekday beside a
  date is named by the browser in the page's language. The guide's strings hold no digit of their own.
- **Announcement**: a visually hidden status region (`role="status"`, `aria-atomic="true"`) that holds one message
  per count, with its notices, in the page's language.
- **Charts**: ECharts, for any chart this app ever adds. The app has no chart today.

## Motion

The two transitions and the one animation in `style.css` read the motion tokens in `tokens.css`. Color and border
changes and a button's press take `--duration-fast` with `--ease-out`; a chevron turns in `--duration-base` with
`--ease-in-out`, times `--motion-scale`; an opened panel's content fades in over `--duration-slow` with `--ease-out`,
rising 0.25rem times `--motion-scale`. Under reduced motion, `--motion-scale` is 0: nothing moves or turns, and the
fade keeps its duration.

## Do's and Don'ts

- Do: draw any chart with ECharts.
- Do: write motion with the tokens in `app/static/tokens.css`: `--duration-fast` 150ms, `--duration-base` 200ms,
  `--duration-slow` 250ms, `--ease-out`, `--ease-in-out`, and every translate, scale or turn multiplied by
  `--motion-scale`, which is 0 under reduced motion. UI motion stays under 300ms.
- Do: take colors, spaces, radii and durations from a token or a system color. Tokens no rule reads yet (the
  exception in `CLAUDE.md`, *Definition of done*): none. As of 2026-11-15, each of the 28 custom properties
  `tokens.css` declares is read by `style.css` (searched for `var(<name>)` of each).
- Do: give every string shown on the page an English and a Spanish text in `app/static/strings.json`.
- Do: keep each section of the guide (Help and How this is calculated), as shown with its examples, at most 150 words,
  and write no digit into its strings: the figures come from the API's count (AC17, AC18).
- Don't: remove a column, a notice or a source to make the page look simpler.
- Don't: restyle the page to another palette without the owner's word.
- Don't: use `color-mix()` or another color space for a background or a text color: AC15's tests read RGB only.
