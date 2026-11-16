# SPEC — Days between dates

**Status:** approved (2026-10-26: the owner's conditional approval of the same day taking effect); changed after
approval by the owner's decisions listed in *Approval*

Provenance: 【M】 the owner said it · 【C】 an agent's inference, removable while a draft. The marks stay when the SPEC
is published. Q1–Q10 are the owner's answers in the discussion of 2026-10-25, live; Q11–Q16 of 2026-10-26, batched;
D1–D3 are decisions of 2026-10-25; D1 and D8 of 2026-10-26; D12, D19 and D25 of 2026-10-27.

## Problem

【M】 *"A small web app that counts the days between two dates, including how many are business days."*

【C】 A spreadsheet counts days with formulas whose conventions do not show: whether the start date counts, which
holidays are excluded, what happens when the dates are reversed. The count looks right and can be off by one day or
by one holiday. This app shows every convention on screen and proves each count against a known answer.

## Who it is for (didactic)

【M】 Didactic (Q1). The learner is a practitioner, an engineer or analyst who lives in spreadsheets and knows some
code, learning to build a tested tool instead of a formula (Q8).

【C】 The lesson is the app and its proof together: how a count is defined, wired and verified.

## Scenarios

### S1 — Count a range
Given the Mexico calendar, when the user enters 2026-10-26 and 2026-10-30, then the screen shows total days and
business days under both conventions side by side (start not counted · both counted) and names the active calendar.
【M】 Q4.

### S2 — The same date twice
Given any calendar, when start and end are the same date, then total days read 0 and 1. 【C】

### S3 — Reversed dates
Given an end date before the start date, when the user counts, then the dates are swapped, the counts are those of
the swapped range, and a notice says the dates were swapped. 【M】 Q5.

### S4 — Switch calendar
Given a range holding a day that is a holiday in one calendar only, when the user switches calendar, then the
business-day counts change and the newly active calendar is named. 【M】 Q3.

### S5 — Add a holiday of one's own
Given the US calendar, when the user adds a weekday inside the range as a holiday, then it is stored in the US list,
is still listed after the app restarts, and each business-day count drops by one. 【M】 Q2, Q9, Q10.

### S6 — A holiday stays in its calendar
Given a holiday added to the US list, when the user switches to Mexico, then it is not listed and does not change the
count. 【M】 Q10.

### S7 — Remove a holiday of one's own
Given a stored holiday, when the user removes it, then it is no longer listed, also after a restart, and the counts
return to their earlier values. 【C】

### S8 — A day is excluded once
Given an own holiday on a Saturday, a Sunday, or a day already a built-in holiday, when the user counts, then the
count is the same as without it. 【C】

### S9 — Past years
Given a range that includes any year before the current one, when the user counts, then a notice says the holidays
were computed with today's rules and past years may differ. With no such year, no notice. 【M】 Q7.

### S10 — Switch language
Given the page in English, when the user switches to Spanish, then every label, notice and message is in Spanish,
business days are labelled *días hábiles* with the note on art. 715, the counts are unchanged, and after the app
restarts the page opens in Spanish. 【M】 D3 (portfolio-wide), Q14, Q15. With nothing stored, or the stored choice
unreadable, the page opens in the browser's language when it is English or Spanish, and in English otherwise. 【M】
Q16.

### S11 — The note on local election days
Given the Mexico calendar active, when the user counts, then a note says local election days are not built in and
can be added to the user's own list; with the US calendar active, no such note. 【M】 Q13.

### S12 — Withdrawn
Withdrawn 2026-11-15: the project has no public demo (*Approval*).

### S13 — Light by default, with a dark mode
Given any system setting, when the page opens, then it is light; when the user switches the toggle in the app bar,
the page shows in the dark values of the visual standard's tokens, and the choice is stored through the API and kept,
after a restart too. In both, each text keeps a contrast ratio of at least 4.5:1 with its background, and the counts
and notices are unchanged. 【M】 2026-11-14, *"dark mode through the existing tokens, following DESIGN.md"*; 【M】
2026-11-16, the visual standard applies in full (*Approval*), whose rule 10 reads: light by default, a toggle in the
app bar that switches to dark and remembers the choice; 【C】 the choice stored through the API, as the language is
(Q15), so the toggle reaches a route (AC10). The 4.5:1: WCAG
2.2, success criterion 1.4.3 Contrast (Minimum), Level AA, *"a contrast ratio of at least 4.5:1"*
(https://www.w3.org/TR/WCAG22/#contrast-minimum, W3C Recommendation 12 December 2024, retrieved 2026-11-14).

### S14 — Results announced, controls within reach
Given a screen reader, when a count completes, then the active calendar, the range, the four counts and any notice
are announced, in the page's language; each Remove button's name includes its date; every button, field and list is
at least 24 px tall; and each field's label sits above it. 【M】 2026-11-14, four of the five findings of the design
audit of 2026-11-14 (the fifth is S13); 【M】 2026-11-16, the label above its field, the visual standard's rule 6, in
place of the label on its field's line (*Approval*). The 24 px: WCAG 2.2, success criterion 2.5.8 Target
Size (Minimum), Level AA, *"at least 24 by 24 CSS pixels"* (https://www.w3.org/TR/WCAG22/#target-size-minimum, W3C
Recommendation 12 December 2024, retrieved 2026-11-14).

### S15 — Help and user guide
Given the page in either language, when the user opens the guide's tab, beside the counter and in view when the page
opens, then it shows a short introduction, the guide's
contents, and one section per feature, in that language: a range and its two conventions, business days and the
calendars, your own holidays, reversed dates, past years, the note on local election days, the language switch, and
the sources. Each section explains its feature in plain words, in at most 150 words, worked examples not counted,
with its worked examples where it has any (S16): the guide is no more elaborate than the app. The section on a range names the first and last
dates accepted, from the app's own limit. 【M】 2026-11-14; 【M】 2026-11-15, a visible user guide that explains each
feature and how the counts are calculated, with examples from the known answers, in both languages, no more
elaborate than the app (*Approval*); 【C】 the introduction, the contents, the dates accepted, and the ceiling of 150
words per section, read from the owner's "about 150 words per feature"; 2026-11-16, worked examples not counted, as
the owner's app template words it (*Approval*).

### S16 — How a result is calculated
Given a result on screen, when the user opens "How this is calculated" beside total days or business days, then it
shows the formula and a worked example: a range from the known-answer checks, written in the guide's text with the
answer the checks expect. A test reads each example's dates and numbers from that text and counts them again through
the API, so changing the text or the code alone fails it. 【M】 2026-11-14, *"Every worked example is also a test, so
the guide can't drift from the code."*; 2026-11-16, the examples written in the guide's text and read by the test, as
the owner's app template's User Guide rule says, in place of examples counted by the API when a panel opens
(*Approval*).

### E1 — Invalid date
Given an empty or impossible date (2026-02-30), or one outside the years accepted (1949-12-31), when the user counts
or adds a holiday, then it is refused with a message naming the field, nothing is counted and nothing is stored. 【C】

### E2 — Duplicate own holiday
Given a date already in the selected calendar's list, when the user adds it again, then it is refused with a message
and the list is unchanged. 【C】

### E3 — Storage fails
Given the database cannot be read or written, when the user counts or edits the list, then an error says so, and no
business-day count is shown that silently leaves out the stored holidays. 【C】 From the definition of done (no lying).
【C】 A language choice that cannot be stored is reported the same way; the page keeps the language on screen (Q15).

## Expectations

Will:
- Count total days and business days between two dates, under both conventions at once. 【M】 Q4.
- Treat Saturday and Sunday as non-business days in both calendars. 【M】 Q2 ("Monday to Friday").
- Offer two built-in calendars, one active at a time and named on screen: Mexico, the mandatory rest days of the
  federal labour law; United States, the federal legal public holidays, with a weekend holiday observed on the Friday
  before or the Monday after. 【M】 Q3 for the calendar; 【C】 the observed-day rule, derived from 5 U.S.C. § 6103(b)(1)
  and Executive Order 11582 sec. 3(a) (*Holiday rules and their sources*).
- Keep the user's own holidays, one list per calendar, stored in SQLite: add, list, remove. 【M】 Q2, Q9, Q10.
- Accept any date from 1950-01-01 to 2150-12-31, applying today's holiday rules to every year, with the past-years
  notice. 【M】 Q6, Q7 · 【M】 the year limit, 2026-11-15 (*Approval*).
- Name each built-in calendar's source and the date its rules were last checked against it. 【C】
- With the Mexico calendar active, show a note that local election days are not built in and can be added to the
  user's own list. 【M】 Q13.
- Show every label, notice and message in English and Spanish, switchable. 【M】 D3, portfolio-wide. In Spanish,
  business days are *días hábiles*, with a note that [LFT] art. 715 gives the term a different meaning for labour
  proceedings. 【M】 Q14.
- Keep the language choice in SQLite, through the API, so it survives a restart. 【M】 Q15. With no choice stored, or
  one that cannot be read, open in the browser's language when it is English or Spanish, in English otherwise. 【M】
  Q16.
- Open light, with a toggle in the app bar for dark that is remembered (S13); announce each result to screen readers
  and keep every control within reach (S14). 【M】 2026-11-14; the toggle 2026-11-16 (*Approval*).
- Explain each feature in a Help panel, and each result with its formula and a worked example that is a known answer
  (S15, S16), in English and Spanish, each section of the guide at most 150 words, worked examples not counted. 【M】
  2026-11-14; its length 2026-11-15 and 2026-11-16 (*Approval*).

Will not:
- Other countries, state or municipal holidays, bank closing days. 【C】
- Built-in local election days in Mexico: the user's own list holds them (Q13). Inauguration Day in the US calendar
  (Q11).
- Holiday rules as they were in past years (Q7).
- Times of day or time zones: dates only. 【C】

## Goals

- 【M】 Get it out of the head: a deployed app that meets the definition of done: functional, no crashes, no lying.
- 【C】 Teach the learner the three things a spreadsheet formula hides: the counting convention, where a holiday comes
  from, and how a count is proven.
- 【C】 Every count on screen traces to a test with a sourced expected value.

## Approaches considered

| | Approach | Right when | Chosen |
|---|---|---|---|
| A | One static page, JavaScript only, nothing installed (rung 2). Path: page → module → page | The learner should open it with nothing installed, and the lesson is the date logic and its tests | |
| B | Localhost Python app, SQLite holding the user's holidays (rung 1). Path: page → API → SQLite → back | The lesson is the full wiring a practitioner builds to replace a spreadsheet, and entered holidays must persist | 【M】 Q9 |
| C | Localhost R Shiny app, SQLite holding the user's holidays (rung 1) | The learner's path out of spreadsheets is R | |

## Acceptance criteria

| ID | Criterion (observable) | Verified by |
|---|---|---|
| AC1 | Total days under both conventions, for any valid pair of dates, through page → API → back | K1–K7, through the API |
| AC2 | Business days under both conventions, for each calendar | K7–K9 and K11, sourced 2026-10-26 (*Holiday rules*, below) |
| AC3 | Reversed dates are swapped, the notice shows, and the counts equal those of the swapped range | K4; a test that asserts the notice's presence in the response and on the page |
| AC4 | The active calendar is named beside the result; switching it recomputes | S4 test through the page |
| AC5 | Own holidays: add, list and remove per calendar through page → API → SQLite → back; they survive a restart and affect only their calendar | S5–S7 tests against a real SQLite file, with a restart between write and read, run in CI; S5–S7 on a local install, with a restart |
| AC6 | A day is excluded once; a duplicate is refused | S8, E2 tests; K10 |
| AC7 | The past-years notice shows when the range includes an earlier year, and only then | S9 tests, both cases |
| AC8 | Invalid input is refused with a message naming the field; nothing is stored | E1 tests, including a database read after the refusal |
| AC9 | A storage failure shows an error and no business-day count; a language choice that cannot be stored shows an error, and the page keeps the language on screen | E3 tests with an unwritable and with an unreadable database, for the holidays and for the language setting, through the page |
| AC10 | No orphans: every control (two dates, calendar choice, add, remove, language switch, theme toggle) reaches a route that executes; every route has a caller; the holidays table and the language and theme settings are written and read. The guide's tab and the two "How this is calculated" are static help with no route (the app template's User Guide rule) | The judge's orphan list |
| AC11 | The screen names each built-in calendar's source and the date its rules were checked; with Mexico active, the note on local election days shows, and with the US calendar it does not (Q13) | A test on the page for each; S11, both cases |
| AC12 | The known-answer checks run on every pull request and every push to main, through the API | CI log |
| AC13 | Every label, notice and message exists in English and Spanish; in Spanish, business days read *días hábiles* with the art. 715 note (Q14); switching the language changes the text, not the counts; the choice is stored through page → API → SQLite and survives a restart (Q15); with none stored, or one unreadable, the page opens in the browser's language when it is English or Spanish, in English otherwise (Q16) | A test per notice in each language; S10 through the page, with a restart; the opening language with the browser set to English, to Spanish and to a third language, and with the stored choice unreadable |
| AC14 | Withdrawn 2026-11-15: the project has no public demo (S12) | — |
| AC15 | The page opens light whatever the system's setting; the app bar's toggle switches it to dark, and the choice is stored through the API and survives a restart; light and dark use the visual standard's tokens; in each, each text keeps at least 4.5:1 contrast with its background (WCAG 2.2, 1.4.3) (S13) | Page tests in each mode that compute every contrast ratio and read the tokens' values; the toggle through the page, with a restart |
| AC16 | After a count, a polite live region holds the result and its notices in the page's language; each Remove button's accessible name contains its date; every button, field and list is at least 24 px tall; each label sits above its field, at 375 px and 1280 px (S14) | Page tests for each, in both languages where text is involved |
| AC17 | The guide shows an introduction, its contents and one section per feature in English and Spanish; in each language, each section of the guide and each "How this is calculated", as shown, holds at most 150 words, worked examples not counted (S15) | A page test per language; a word count of each part, on the page, per language |
| AC18 | Every worked example is a known answer written in the guide's text, in each language: a test reads its dates and numbers from the text, counts them through the API, and fails if they differ from the count or from the K table, or name a range the table lacks (S16) | A test per example and language, shown failing on an altered example; the page test of S16 |

## Known-answer checks

Total days are derived by calendar arithmetic, shown below. Business days are the Monday–Friday days of the range
minus the active calendar's holidays that fall on a weekday in it, under the rules in *Holiday rules and their
sources* (below, retrieved 2026-10-26), with no holidays of the user's own unless the row says so. The Gregorian
calendar and arithmetic need no source (the owner's source rule, decided 2026-10-25); the values were
cross-checked with Python's `datetime` on 2026-10-25 and 2026-10-26 (K11's, as moved, on 2026-11-15).

| # | Input | Expected | Source |
|---|---|---|---|
| K1 | 2026-10-26 (Mon) → 2026-10-30 (Fri) | Total 4 · 5. Business 4 · 5 in both calendars: no holiday of either falls in the range | Derivation: four days later; both counted adds one. Holidays: [LFT], [USC], [EO] |
| K2 | 2026-10-26 → 2026-10-26 | Total 0 · 1 | Derivation |
| K3 | 2026-10-30 (Fri) → 2026-11-02 (Mon) | Total 3 · 4. Business 1 · 2 in both calendars: no holiday of either in the range | Derivation; [LFT], [USC], [EO] |
| K4 | 2026-10-30 → 2026-10-26 | Swapped; as K1; notice shown | Q5 |
| K5 | 2028-02-28 → 2028-03-01 | Total 2 · 3 (2028 is a leap year) | Derivation |
| K6 | 2027-02-28 → 2027-03-01 | Total 1 · 2 (2027 is not) | Derivation |
| K7 | 2026-01-01 (Thu) → 2026-12-31 (Thu) | Total 364 · 365. Monday–Friday days 260 · 261. Business: Mexico 254 · 254; United States 250 · 250 | Derivation: 52 weeks hold 260 Monday–Friday days, plus Thursday 31 December, 261; not counting the start drops Thursday 1 January, 260. Mexico: the seven rest days of K8a, all on weekdays; 1 January is one, so 260 − 6 and 261 − 7. United States: eleven observed holidays on weekdays, 4 July observed Friday 3 July (K9a); 1 January is one, so 260 − 10 and 261 − 11 |
| K8a | Mexico, 2026: the rest days on weekdays | Seven: 1 Jan (Thu), 2 Feb (Mon), 16 Mar (Mon), 1 May (Fri), 16 Sep (Wed), 16 Nov (Mon), 25 Dec (Fri). Fraction VII does not apply in 2026; IX: 2026 holds no federal or judicial ordinary election, and any local ordinary election falls on Sunday 7 June | [LFT] art. 74 I–VI, VIII; IX: [LGIPE] arts. 22.1, 494.2, [CPEUM] art. 116 IV a), whose exception applies only in a federal election year, and 2026 is none (*Holiday rules*); derivation for the Mondays |
| K8b | Mexico, 2030-09-30 (Mon) → 2030-10-04 (Fri) | Total 4 · 5. Business 3 · 4: Tuesday 1 October 2030 is a rest day | [LFT] art. 74 VII; the transfer years from [CPEUM] (*Holiday rules*) |
| K8c | Mexico, 2027-04-30 (Fri) → 2027-05-03 (Mon) | Total 3 · 4. Business 1 · 2: 1 May 2027 is a Saturday and is not moved | [LFT] art. 74 IV; no rule moves it (open question 4) |
| K9a | US, 2026-06-29 (Mon) → 2026-07-06 (Mon) | Total 7 · 8. Business 4 · 5: Independence Day, Saturday 4 July 2026, is observed Friday 3 July | [USC] § 6103(a), (b)(1) |
| K9b | US, 2027-07-02 (Fri) → 2027-07-06 (Tue) | Total 4 · 5. Business 1 · 2: Sunday 4 July 2027 is observed Monday 5 July | [USC] § 6103(a); [EO] sec. 3(a) |
| K9c | US, 2027-12-27 (Mon) → 2027-12-31 (Fri) | Total 4 · 5. Business 3 · 4: New Year's Day 2028 is a Saturday, observed Friday 31 December 2027, in the year before | [USC] § 6103(a), (b)(1); derivation |
| K9d | US, 2033-06-17 (Fri) → 2033-06-21 (Tue) | Total 4 · 5. Business 1 · 2: Juneteenth, Sunday 19 June 2033, a holiday added after 1971, is observed Monday 20 June | [USC] § 6103(a); [EO] secs. 2(a), 3(a), 6 |
| K10 | Own holiday on Saturday 2026-10-31, range K3 | Business 1 · 2, unchanged | S8; derivation |
| K11 | US, 2150-12-24 (Thu) → 2150-12-31 (Thu), the last dates accepted (the year limit, *Expectations*) | Total 7 · 8. Business 4 · 5: Christmas, Friday 25 December, is excluded; New Year's Day of 2151 is a Friday, kept on that day, outside the range | [USC] § 6103(a), (b)(1); the weekdays: Python's date type and cal(1) agree that 25 December 2150 and 1 January 2151 are Fridays, checked 2026-11-15. Moved 2026-11-15 to the new last dates (【C】 the range; *Approval*); before, it ran 9999-12-27 → 9999-12-31 |

### Holiday rules and their sources

Retrieved 2026-10-26. Quotes are verbatim, in the language of the source. 【C】 The derivations are Claude's.

**Mexico** — [LFT] art. 74: *"Son días de descanso obligatorio: I. El 1o. de enero; II. El primer lunes de febrero en
conmemoración del 5 de febrero; III. El tercer lunes de marzo en conmemoración del 21 de marzo; IV. El 1o. de mayo;
V. El 16 de septiembre; VI. El tercer lunes de noviembre en conmemoración del 20 de noviembre; VII. El 1o. de octubre
de cada seis años, cuando corresponda a la transmisión del Poder Ejecutivo Federal; VIII. El 25 de diciembre, y IX. El
que determinen las leyes federales y locales electorales, en el caso de elecciones ordinarias, para efectuar la
jornada electoral."*
- VII, the transfer years. [CPEUM] art. 83: *"El Presidente entrará a ejercer su encargo el 1o. de octubre y durará en
  él seis años."* [CPEUM], the decree of DOF 10-02-2014, fifteenth transitional article: the 2018–2024 term
  *"concluirá el 30 de septiembre de 2024"*. 【C】 So the transfer years are 2024 + 6n; applied to every year under Q7,
  2018 included,
  whose transfer was on 1 December (the past-years notice, S9, covers it).
- IX, election day. Federal ordinary elections, [LGIPE] art. 22.1: *"Las elecciones ordinarias deberán celebrarse el
  primer domingo de junio del año que corresponda"*; the day is non-working *"en todo el territorio nacional"*
  (22.2). Judicial ordinary elections, art. 494.2: *"el primer domingo del mes de junio del año que corresponda de
  manera concurrente con los procesos electorales en que se renueve cualquiera de las Cámaras del Congreso de la
  Unión"*. Local ordinary elections, [CPEUM] art. 116 IV a): *"que la jornada comicial tenga lugar el primer domingo de
  junio del año que corresponda. Los Estados cuyas jornadas electorales se celebren en el año de los comicios
  federales y no coincidan en la misma fecha de la jornada federal, no estarán obligados por esta última
  disposición"*; the day is non-working *"en todo el territorio de la entidad"* ([LGIPE] art. 25.2), that state only.
  [LGIPE] art. 25.1 is not used: the compiled text prints, in brackets, the wording a Supreme Court ruling
  invalidated (DOF 24-11-2023), not the restored one. The next judicial elections, federal and local, are set by
  [CPEUM], the decree of DOF 02-06-2026, third transitional article: *"La jornada electoral de las elecciones
  judiciales federal y locales se celebrarán de forma coincidente el primer domingo de junio del año 2028."* 【C】 Two
  sources disagree on the year: [LGIPE] art. 494.2's rule, concurrent with a Chamber's renewal, would give 2027; the
  constitution's later transitional article gives 2028, and it is the one used. The SPEC needs no year: under either
  the day is a Sunday. Federal election years: [CPEUM], the decree of DOF 10-02-2014, second transitional article,
  II a), sets *"La celebración de elecciones federales y locales el primer domingo de junio del año que corresponda,
  en los términos de esta Constitución, a partir del 2015, salvo aquellas que se verifiquen en 2018, las cuales se
  llevarán a cabo el primer domingo de julio"*, and [CPEUM] art. 51 elects the Chamber of Deputies *"en su totalidad
  cada tres años"*. 【C】 So federal
  election years are 2015 + 3n (2024, 2027, 2030), and 2026 is not one; the national days of IX, federal and
  judicial, are always a Sunday; a local election day is a state's day and, under the exception, not bound to a
  Sunday (open question 3).
- A weekend rest day: art. 74 and art. 75 move none, and a search of the whole text for *"descanso obligatorio"*
  found no article that does (open question 4). Not stated on the page, so not moved.

**United States** — [USC] § 6103(a): *"The following are legal public holidays: New Year's Day, January 1. Birthday of
Martin Luther King, Jr., the third Monday in January. Washington's Birthday, the third Monday in February. Memorial
Day, the last Monday in May. Juneteenth National Independence Day, June 19. Independence Day, July 4. Labor Day, the
first Monday in September. Columbus Day, the second Monday in October. Veterans Day, November 11. Thanksgiving Day,
the fourth Thursday in November. Christmas Day, December 25."*
- Saturday. § 6103(b)(1): *"Instead of a holiday that occurs on a Saturday, the Friday immediately before is a legal
  public holiday for— (A) employees whose basic workweek is Monday through Friday"*.
- Sunday. [EO] sec. 3(a): an employee *"whose basic workweek does not include Sunday … shall be excused from work on
  the next workday of his basic workweek whenever a holiday falls on Sunday"*: Monday, for a Monday–Friday week.
  Sec. 2(a) lists the holidays of 1971 and adds *"or any other calendar day designated as a holiday by Federal
  statute or Executive order"*, which brings in those added or moved later (Birthday of Martin Luther King, Jr.;
  Juneteenth, K9d; Veterans Day, on 11 November since 1978, by Pub. L. 94-97 of 1975, as the [USC] notes list); sec. 6
  makes the day a holiday: *"the workdays referred to in sections 3, 4, and 5 shall be treated as
  holidays in lieu of the corresponding calendar holidays"*.
- Not in the calendar: § 6103(c), Inauguration Day, *"January 20 of each fourth year after 1965"*, a legal public
  holiday for employees in the Washington, D.C. area only; left out (Q11, open question 5). 【C】 Other days *"declared
  to be a
  holiday by … Executive order"* (§ 6103(b)) come one at a time and cannot be computed; the user's own list (Q2)
  holds them.

Sources:
- [LFT] Ley Federal del Trabajo, texto vigente, última reforma DOF 14-05-2026, Cámara de Diputados,
  https://www.diputados.gob.mx/LeyesBiblio/pdf/LFT.pdf, retrieved 2026-10-26.
- [LGIPE] Ley General de Instituciones y Procedimientos Electorales, última reforma DOF 02-06-2026,
  https://www.diputados.gob.mx/LeyesBiblio/pdf/LGIPE.pdf, retrieved 2026-10-26.
- [CPEUM] Constitución Política de los Estados Unidos Mexicanos, última reforma DOF 07-10-2026,
  https://www.diputados.gob.mx/LeyesBiblio/pdf/CPEUM.pdf, retrieved 2026-10-26.
- [USC] 5 U.S.C. § 6103, United States Code, 2024 Edition, GovInfo (U.S. Government Publishing Office),
  https://www.govinfo.gov/content/pkg/USCODE-2024-title5/html/USCODE-2024-title5-partIII-subpartE-chap61-subchapI-sec6103.htm,
  retrieved 2026-10-26. The current text at uscode.house.gov could not be read: its section pages
  https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title5-section6103&num=0&edition=prelim and
  https://uscode.house.gov/view.xhtml?req=(title:5%20section:6103%20edition:prelim) returned 404 on 2026-10-26, and
  the site said some features were temporarily unavailable. Amendments after the 2024 edition are not checked; that
  edition lists the last amendment of § 6103 in 2021 (Juneteenth).
- [EO] Executive Order 11582, *Observance of Holidays by Government Agencies*, 11 February 1971, Federal Register vol.
  36, no. 31, 13 February 1971, p. 2957, https://www.govinfo.gov/content/pkg/FR-1971-02-13/pdf/FR-1971-02-13.pdf,
  retrieved 2026-10-26; also set out in the notes to § 6103 in [USC], with no note of revocation.

## Out of scope

Rule history (Q7) · other countries and regional holidays · bank closing days · times and time zones · importing or
exporting holiday lists · user accounts: one local user · Inauguration Day, 5 U.S.C. § 6103(c), a holiday of the
Washington, D.C. area only (【M】 Q11) · Mexico's local election days as built-in days, left to the user's own list
(【M】 Q13) · a public demo or an external host (【M】 2026-11-15). 【C】 except where marked.

## Stack and deployment

Delivery rung: 1 — user space, no admin. 【M】 Q9.
Python and SQLite on localhost (the portfolio's stack); the web framework is chosen in the plan: FastAPI (【M】 Q12,
2026-10-26).
Real-wiring path: page → API → SQLite → back.
Deployment: Docker only. `Dockerfile` and `compose.yaml` run the app with its database in a named volume, and the
passing Docker check (CI's `docker` job, `scripts/docker_check.py`) is the deployment validation. No public demo and
no external host. 【M】 2026-11-15.
Web interface: follows the owner's visual standard (its rules and tokens), built on the owner's web starter: Vue 3,
Vite and TypeScript, Tailwind CSS 4 with shadcn-vue, vue-i18n, AG Grid for the grids; FastAPI serves the built page.
【M】 2026-11-16 (*Approval*).
Licence: MIT. 【M】 D2, portfolio-wide, 2026-10-25.
Interface language: English and Spanish, switchable. 【M】 D3, portfolio-wide, 2026-10-25.

## Open questions

1. Licence and interface language: decided 2026-10-25, portfolio-wide: MIT; English and Spanish.
2. **Research, answered 2026-10-26.** The holiday rules' primary sources are retrieved (*Holiday rules and their
   sources*). The article and section numbers given from memory on 2026-10-25 were right. The Sunday rule is not in
   § 6103 but in Executive Order 11582.
3. **Research, answered 2026-10-26; one part for the owner** (Q13, 2026-10-26). Federal and judicial ordinary
   elections fall on the first Sunday of June ([LGIPE] arts. 22.1, 494.2): they never change a Monday–Friday count,
   no dated list is needed, and Q7's "today's rules for every year" holds for them. A local ordinary election is bound
   to that Sunday too, except a state's election held in a federal election year on another date ([CPEUM] art. 116
   IV a)), and its day is non-working in that state only ([LGIPE] art. 25.2): it cannot be computed from today's
   rules. An extraordinary election is no rest day under IX (*"en el caso de elecciones ordinarias"*). The owner's part,
   answered 2026-10-26 (Q13, C): local election days are left to the user's own list, with a note on screen.
4. **Research, answered 2026-10-26.** No: no article of [LFT] moves a rest day that falls on a weekend (K8c).
5. **For the owner** (Q11, 2026-10-26). Found by the research: § 6103(c) makes Inauguration Day, every fourth
   20 January (next in 2029), a legal public holiday for federal employees in the Washington, D.C. area only.
   Answered 2026-10-26 (Q11, A): left out; *Out of scope* names it.
6. **For the owner** (Q14, 2026-10-26). The Spanish label for "business days" (AC13). [LFT] art. 715 defines
   *días hábiles*, for labour proceedings, as *"todos los del año con excepción de los sábados y domingos, los de
   descanso obligatorio, los festivos que señale el calendario oficial y aquéllos en que las autoridades laborales
   señaladas en el artículo anterior suspendan sus labores"*: a different set from the app's count. Answered
   2026-10-26 (Q14, A): *días hábiles*, with a note naming art. 715's meaning.
7. **For the owner** (Q15, 2026-10-26). The language switch is a control AC10's list leaves out; if it acts
   only in the page, it reaches no route, and the orphan check would flag it. Found by the plan's review.
   Answered 2026-10-26 (Q15, B): the choice goes through the API into SQLite (AC10, AC13, S10).
8. **For the owner** (Q16, 2026-10-26). The language the page opens in when nothing is stored, or when the stored
   choice cannot be read. Found by the SPEC's review, 2026-10-26. Answered 2026-10-26 (Q16, C): the browser's
   language when it is English or Spanish, English otherwise (S10, AC13).

## Approval

2026-10-25, D1, selected "Approve after sources": a conditional approval, taking effect once K8
and K9 carry sources. 2026-10-26: K8 and K9 sourced; the review failed twice; not in effect. 2026-10-26, D1 option A,
a new condition: Q11–Q15 answered and folded in, and the review passing its next run. Q11–Q15 folded in and the
review passed on its rerun, 2026-10-26; held by Q16 until answered. Q16 answered and folded in 2026-10-26, and the
review passed on its rerun: approved, 2026-10-26. Changes after approval: 2026-10-26, D8: a live demo with a notice
that its storage resets on restart (S12, AC14; AC5's proof; *Stack and deployment*), approved in the owner's answer:
【M】 *"This answer also approves the SPEC change it requires."*; withdrawn 2026-11-15 (below). 2026-10-26: the
year limit's source added, a correction the review before publication required: every number carries its source;
confirmed by the owner, 2026-10-27 (D12). 2026-10-27, D25: AC12 reads "on every pull request and every push to
main", matching CI's triggers, approved in the owner's answer: 【M】 *"Update AC12, the app's CLAUDE.md and the plan to
"on every pull request and every push to main", matching D19."* 2026-11-14: S13–S16, AC15–AC18, the two
*Expectations* lines that name them and AC10's new controls, approved in the owner's pick 【M】 *"Approve as drafted
(Recommended)"*, with *"Follow the system (Recommended)"* for what turns dark mode on (S13) and *"Counted by the API
(Recommended)"* for where the worked examples' numbers come from (S16, AC18); the options' labels were written by
Claude. 2026-11-14: the source of S13's and AC15's 4.5:1, WCAG 2.2 success criterion 1.4.3, added after the review
before publication found it missing, approved in the owner's pick 【M】 *"Add the citation (Recommended)"*.
2026-11-15: Docker only: S12 and AC14 withdrawn; the live demo's notice removed from S15 and *Expectations*, and its
mentions from AC1, AC4, AC5, AC11 and AC13; *Stack and deployment* and *Out of scope* rewritten; D8's entry above
names no host, in the owner's decision:
【M】 *"Docker only. No public demo and no external host for this project, now or as a pending item. The passing
Docker check is the deployment validation."* 2026-11-15: the years accepted narrowed to 1950–2150 (*Expectations*,
E1), in the owner's answer to the cost of a count over years 1 to 9999: 【M】 *"1950-2150 is more than enough"*; K11
moved to the new last dates, the range and its values derived by the agent from that limit (【C】). 2026-11-15:
the user guide (S15, AC17 and the *Expectations* line that names them), in the owner's request: 【M】 *"Add a visible
Help / User Guide in the app itself. It explains each feature and how the day counts are calculated, with examples
taken from SPEC's known answers, in both languages. Keep it smaller than the app itself, about 150 words per
feature."*; on AC17's comparison with the rest of the page's text, which that length could not meet, the owner's
answer: 【M】 *"This rules shouldn't be taken literal. The goal is the user-guide must not be more elaborated and
complicated that the app solution and features."* The comparison is replaced by a ceiling of 150 words per section,
and S15 names the guide's introduction, contents and dates accepted: the agent's reading of those two answers
(【C】), not text the owner approved word for word. 2026-11-15: S13's and AC15's light clause, "the page looks as
before" and "the colors are those `DESIGN.md` recorded before", narrowed to the four color tokens keeping their light
values, because the owner asked for the page to be restyled "in light and dark" (【M】 *"Restyle days-between-dates
so it can count as finished. [...] Follow DESIGN.md: polish the layout, typography, spacing and states, in light and
dark, with accessibility."*); the narrowed wording is the agent's (【C】). 2026-11-16: the app
reflects the owner's whole foundation, in the owner's decision: 【M】 *"New scope: days-between-dates is the first app
that must reflect our whole foundation, not an app that predates it. DESIGN.md's line saying the visual standard
doesn't apply is wrong; it applies in full."*, and, asked whether to rebuild on the web starter or keep the plain
page: 【M】 *"Rebuild on the web starter."* The SPEC follows: S13 and AC15 (light by default, a toggle in the app bar,
remembered), S14 and AC16 (labels above fields), S15, S16, AC17 and AC18 (the guide a tab; its examples written in
its text and read by a test; worked examples not counted in its length), AC10 (the theme toggle; the guide as static
help), *Expectations* and *Stack and deployment*. The wording, the theme stored through the API, and the guide as a
tab are the agent's (【C】).
