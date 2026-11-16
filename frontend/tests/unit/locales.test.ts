import { describe, expect, it } from 'vitest'
import en from '@/locales/en.json'
import es from '@/locales/es.json'

function flatten(messages: object, prefix = ''): Record<string, string> {
  return Object.entries(messages).reduce<Record<string, string>>((all, [key, value]) => {
    const path = prefix ? `${prefix}.${key}` : key
    return typeof value === 'string' ? { ...all, [path]: value } : { ...all, ...flatten(value, path) }
  }, {})
}

describe('the language files', () => {
  it('hold the same keys, so no text falls back to English', () => {
    expect(Object.keys(flatten(es)).sort()).toEqual(Object.keys(flatten(en)).sort())
  })

  it('leave no text empty', () => {
    for (const messages of [en, es])
      expect(Object.values(flatten(messages)).filter(text => !text.trim())).toEqual([])
  })
})
