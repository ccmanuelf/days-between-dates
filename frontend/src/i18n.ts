import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import es from './locales/es.json'

export type Language = 'en' | 'es'
export const LANGUAGES: Language[] = ['en', 'es']

// Every text exists in both languages (SPEC, AC13): a missing one shows its key, never the other language's text.
// tests/unit/locales.test.ts fails when the two files' keys differ, and tests/test_page.py when the page names a key
// that the files lack.
export const i18n = createI18n({
  legacy: false,
  locale: 'en',
  fallbackLocale: false,
  missingWarn: false,
  fallbackWarn: false,
  messages: { en, es },
})

export function applyLanguage(language: Language) {
  i18n.global.locale.value = language
  document.documentElement.lang = language
}

// The opening language when none is stored, or the stored one cannot be read (SPEC, Q16).
export function browserLanguage(): Language {
  const preferred = (navigator.languages?.[0] || navigator.language || 'en').toLowerCase()
  return LANGUAGES.find(code => preferred.startsWith(code)) ?? 'en'
}
