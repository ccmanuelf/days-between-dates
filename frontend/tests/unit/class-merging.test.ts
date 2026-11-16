import { describe, expect, it } from 'vitest'
import { Label } from '@/components/ui/label'
import { cn } from '@/lib/utils'
import { mount } from './mount'

// tailwind-merge reads an unknown text-* as a color. Without the tokens' sizes it silently drops text-label here.
describe('class merging knows the tokens', () => {
  it.each(['label', 'body-compact', 'body', 'heading-compact', 'heading-2', 'heading-3', 'heading-4'])(
    'keeps text-%s beside a text color',
    (size) => {
      expect(cn(`text-${size}`, 'text-muted-foreground')).toBe(`text-${size} text-muted-foreground`)
    },
  )

  it('still lets the later size, color or shadow win', () => {
    expect(cn('text-label', 'text-body')).toBe('text-body')
    expect(cn('text-muted-foreground', 'text-foreground')).toBe('text-foreground')
    expect(cn('shadow-card', 'shadow-pop')).toBe('shadow-pop')
  })

  it('reaches the generated components, which import from cn', () => {
    const label = mount(Label)
    expect(label.classList.contains('text-label')).toBe(true)
    expect(label.classList.contains('text-muted-foreground')).toBe(true)
  })
})
