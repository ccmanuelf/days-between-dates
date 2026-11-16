import type { ClassValue } from 'clsx'
import { clsx } from 'clsx'
import { extendTailwindMerge } from 'tailwind-merge'

// tailwind-merge reads an unknown text-* or shadow-* as a color, so text-label beside text-muted-foreground would drop
// the size. It has to know the sizes and shadows tokens.css defines.
const merge = extendTailwindMerge({
  extend: {
    theme: {
      text: ['label', 'body-compact', 'body', 'heading-compact', 'heading-2', 'heading-3', 'heading-4'],
      shadow: ['card', 'pop'],
    },
  },
})

export function cn(...inputs: ClassValue[]) {
  return merge(clsx(inputs))
}
