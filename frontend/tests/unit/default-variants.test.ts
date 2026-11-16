import { describe, expect, it } from 'vitest'
import { Button } from '@/components/ui/button'
import { mount } from './mount'

// Re-running the shadcn-vue CLI on the button restores its filled cobalt default. These tests fail if it does,
// so that decision can't be undone silently (rule 1).
describe('default variants', () => {
  it('a Button with no variant is outline, not filled', () => {
    const plain = mount(Button)
    const outline = mount(Button, { variant: 'outline' })
    expect(plain.className).toBe(outline.className)
    expect(plain.classList.contains('border-border-strong')).toBe(true)
    expect(plain.classList.contains('bg-card')).toBe(true)
    expect(plain.classList.contains('bg-primary')).toBe(false)
  })

  it('filled cobalt has to be asked for by name', () => {
    expect(mount(Button, { variant: 'primary' }).classList.contains('bg-primary')).toBe(true)
  })
})
