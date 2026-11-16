// The app's state and every call it makes to the JSON API. The page shows what is here; each control calls an action
// below, and each action reaches a route (SPEC, AC10).
import { reactive } from 'vue'
import type { Answer } from '@/api'
import { api, errorOf } from '@/api'
import type { Language } from '@/i18n'
import { applyLanguage, browserLanguage, LANGUAGES } from '@/i18n'

export type CalendarId = 'mx' | 'us'
export type Theme = 'light' | 'dark'
// Where an error shows: beside the count form, beside the list and its add form, or at the top of the page (the
// language and theme controls are in the app bar).
export type ErrorPlace = 'count' | 'add' | 'top'

export interface Pair {
  start_not_counted: number
  both_counted: number
}

export interface CountResult {
  calendar: CalendarId
  start: string
  end: string
  swapped: boolean
  past_years: boolean
  total: Pair
  business: Pair
}

export interface Source {
  key: string
  title: string
  url: string
  retrieved: string
}

export interface Calendar {
  id: CalendarId
  checked: string
  sources: Source[]
}

// A message to show, kept as its key so a language switch rewrites it. `field` names the field in the message;
// `mark` says the user typed that field's refused value, so the field is marked invalid.
export interface Shown {
  key: string
  field: string | null
  place: ErrorPlace
  mark: boolean
}

export const state = reactive({
  ready: false,
  storage: 'checking' as 'checking' | 'ok' | 'down',
  calendars: [] as Calendar[],
  calendar: 'mx' as CalendarId,
  start: '',
  end: '',
  newDay: '',
  result: null as CountResult | null,
  ownDays: [] as string[],
  ownLoaded: false,
  error: null as Shown | null,
  language: 'en' as Language,
  // What index.html painted before the first frame, from the browser's copy; the API's answer follows in start().
  theme: (document.documentElement.classList.contains('dark') ? 'dark' : 'light') as Theme,
})

// Each count and each list request is numbered; an answer that is not the latest is out of date and not shown (F1).
let countRequest = 0
let listRequest = 0
// Language and theme choices are stored one after another, in the order made, so the last choice made is the one
// kept; a choice overtaken before its turn is not sent, and only the latest choice's answer is shown.
let languageRequest = 0
let themeRequest = 0
let choicesStored: Promise<void> = Promise.resolve()

function show(key: string, field: string | null = null, place?: ErrorPlace, mark = true) {
  state.error = { key, field, place: place ?? (field === 'day' ? 'add' : 'count'), mark: mark && field !== null }
}

// A storage failure takes the count off the screen too: the message says no count is shown (SPEC, AC9), and the
// status in the app bar says the storage is unavailable. An answer from a route that used the database says it is
// available again.
function markStorageDown() {
  state.result = null
  state.storage = 'down'
}

function markStorageOk() {
  state.storage = 'ok'
}

function showAnswer(answer: Answer, place?: ErrorPlace) {
  const error = errorOf(answer)
  if (answer.status === 0 || !error) {
    show('error_network', null, place)
    return
  }
  if (error.code === 'storage')
    markStorageDown()
  show(`error_${error.code}`, error.field, place)
}

export function clearError() {
  state.error = null
}

export async function count() {
  const request = ++countRequest
  const query = new URLSearchParams({ calendar: state.calendar, start: state.start.trim(), end: state.end.trim() })
  const answer = await api<CountResult>('GET', `/api/count?${query}`)
  if (request !== countRequest)
    return
  if (answer.status === 200 && answer.body) {
    clearError()
    markStorageOk()
    state.result = answer.body
  }
  else {
    state.result = null
    showAnswer(answer)
  }
}

export async function loadHolidays() {
  const request = ++listRequest
  const calendar = state.calendar
  state.ownDays = [] // no list stays on screen under another calendar's title
  state.ownLoaded = false
  const answer = await api<{ holidays: string[] }>('GET', `/api/holidays?calendar=${calendar}`)
  if (request !== listRequest)
    return
  if (answer.status !== 200 || !answer.body) {
    showAnswer(answer)
    return
  }
  markStorageOk()
  state.ownDays = answer.body.holidays
  state.ownLoaded = true
}

async function afterListChange() {
  await loadHolidays()
  if (state.result)
    await count()
}

export async function switchCalendar(calendar: CalendarId) {
  state.calendar = calendar
  await afterListChange()
}

export async function addHoliday() {
  const answer = await api('POST', '/api/holidays', { calendar: state.calendar, day: state.newDay.trim() })
  if (answer.status === 201) {
    clearError()
    markStorageOk()
    state.newDay = ''
    await afterListChange()
  }
  else {
    showAnswer(answer)
  }
}

export async function removeHoliday(day: string) {
  const answer = await api('DELETE', `/api/holidays/${state.calendar}/${day}`)
  if (answer.status === 204) {
    clearError()
    markStorageOk()
    await afterListChange()
  }
  else {
    // Nothing was typed: the message shows beside the list, and no field is marked.
    const error = errorOf(answer)
    if (error?.code === 'storage')
      markStorageDown()
    show(answer.status === 0 || !error ? 'error_network' : `error_${error.code}`, error?.field ?? null, 'add', false)
  }
}

function storeChoice(path: string, body: object, isLatest: () => boolean, failure: string) {
  choicesStored = choicesStored.then(async () => {
    if (!isLatest())
      return
    const answer = await api('PUT', path, body)
    if (!isLatest())
      return
    if (answer.status === 200) {
      markStorageOk()
      if (state.error?.key === failure)
        clearError() // only this choice's own earlier failure; any other message stays
    }
    else {
      show(failure, null, 'top')
    }
  })
}

export function switchLanguage(language: Language) {
  const request = ++languageRequest
  state.language = language
  applyLanguage(language)
  storeChoice('/api/language', { language }, () => request === languageRequest, 'error_language_not_stored')
}

export function applyTheme(theme: Theme) {
  state.theme = theme
  document.documentElement.classList.toggle('dark', theme === 'dark')
  try {
    localStorage.setItem('theme', theme) // only so the next load paints in this theme before the API answers
  }
  catch {
    // Storage can be blocked: the page then paints light first, and the API's answer follows.
  }
}

// The visual standard's rule 10: light by default, a toggle in the app bar, the choice remembered (SPEC, S13).
export function toggleTheme() {
  const request = ++themeRequest
  const theme: Theme = state.theme === 'dark' ? 'light' : 'dark'
  applyTheme(theme)
  storeChoice('/api/theme', { theme }, () => request === themeRequest, 'error_theme_not_stored')
}

export async function checkStorage() {
  const answer = await api('GET', '/api/status')
  state.storage = answer.status === 200 ? 'ok' : 'down'
  return answer
}

export async function start() {
  const [catalog, language, theme, health] = await Promise.all([
    api<{ calendars: Calendar[] }>('GET', '/api/calendars'),
    api<{ language: Language | null }>('GET', '/api/language'),
    api<{ theme: Theme | null }>('GET', '/api/theme'),
    checkStorage(),
  ])
  state.calendars = catalog.status === 200 && catalog.body ? catalog.body.calendars : []
  const stored = language.status === 200 ? language.body?.language : null
  state.language = stored && LANGUAGES.includes(stored) ? stored : browserLanguage()
  applyLanguage(state.language)
  if (themeRequest === 0) // a choice made while the page was loading is the one that stays
    applyTheme(theme.status === 200 && theme.body?.theme === 'dark' ? 'dark' : 'light')
  if (health.status !== 200)
    showAnswer(health) // the database cannot be read: say so before any count
  await loadHolidays()
  state.ready = true
  document.body.dataset.ready = 'true'
}
