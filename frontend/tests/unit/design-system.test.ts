// @vitest-environment node
// This test reads files and needs no DOM. Under jsdom, Vite rewrites new URL('...', import.meta.url) as an asset path.
import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'

const frontend = fileURLToPath(new URL('../..', import.meta.url))

function sourceFiles(folder: string): string[] {
  return readdirSync(folder).flatMap((entry) => {
    const path = join(folder, entry)
    if (statSync(path).isDirectory())
      return sourceFiles(path)
    return /\.(?:vue|ts|js|css)$/.test(entry) ? [path] : []
  })
}

describe('tokens.css is the only source of color', () => {
  const tokens = resolve(frontend, 'src/design-system/tokens.css')
  // A hex value, also inside brackets (bg-[#f00]), or a color function. color-mix() is how a token is softened, so it passes.
  const literal = /(?:^|[\s:'"(,[=])#[0-9a-f]{3,8}\b|\b(?:rgba?|hsla?|hwb|lab|lch|oklab|oklch|color)\(/i
  // CSS's named colors.
  const keywords = 'aliceblue|antiquewhite|aqua|aquamarine|azure|beige|bisque|black|blanchedalmond|blue|blueviolet|brown|burlywood|cadetblue|chartreuse|chocolate|coral|cornflowerblue|cornsilk|crimson|cyan|darkblue|darkcyan|darkgoldenrod|darkgray|darkgreen|darkgrey|darkkhaki|darkmagenta|darkolivegreen|darkorange|darkorchid|darkred|darksalmon|darkseagreen|darkslateblue|darkslategray|darkslategrey|darkturquoise|darkviolet|deeppink|deepskyblue|dimgray|dimgrey|dodgerblue|firebrick|floralwhite|forestgreen|fuchsia|gainsboro|ghostwhite|gold|goldenrod|gray|green|greenyellow|grey|honeydew|hotpink|indianred|indigo|ivory|khaki|lavender|lavenderblush|lawngreen|lemonchiffon|lightblue|lightcoral|lightcyan|lightgoldenrodyellow|lightgray|lightgreen|lightgrey|lightpink|lightsalmon|lightseagreen|lightskyblue|lightslategray|lightslategrey|lightsteelblue|lightyellow|lime|limegreen|linen|magenta|maroon|mediumaquamarine|mediumblue|mediumorchid|mediumpurple|mediumseagreen|mediumslateblue|mediumspringgreen|mediumturquoise|mediumvioletred|midnightblue|mintcream|mistyrose|moccasin|navajowhite|navy|oldlace|olive|olivedrab|orange|orangered|orchid|palegoldenrod|palegreen|paleturquoise|palevioletred|papayawhip|peachpuff|peru|pink|plum|powderblue|purple|rebeccapurple|red|rosybrown|royalblue|saddlebrown|salmon|sandybrown|seagreen|seashell|sienna|silver|skyblue|slateblue|slategray|slategrey|snow|springgreen|steelblue|tan|teal|thistle|tomato|turquoise|violet|wheat|white|whitesmoke|yellow|yellowgreen'
  // Tailwind's palette in every utility that takes a color (bg-red-500, outline-red-500), or a named color in brackets (bg-[red]).
  const palette = 'white|black|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose|slate|gray|zinc|neutral|stone'
  const utility = 'bg|text|border(?:-[trblxyse])?|ring(?:-offset)?|fill|stroke|outline|shadow|inset-shadow|drop-shadow|from|via|to|decoration|accent|caret|divide|placeholder'
  const named = new RegExp(`\\b(?:${utility})-(?:(?:${palette})\\b|\\[(?:${keywords})\\])`)
  // A named color as the value of a color property, in CSS or in a JavaScript style object: color: red.
  const keyword = new RegExp(`\\b(?:color|background(?:-color)?|border(?:-[a-z]+)?-color|outline-color|fill|stroke|caret-color|accent-color)\\s*:\\s*['"]?(?:${keywords})\\b(?![-(])`, 'i')
  // A named color anywhere in a shorthand value, up to ; or }: border: 1px solid red, box-shadow: 0 0 4px black. The
  // name must stand alone, so var(--chart-red) is not a color.
  const shorthands = 'border(?:-(?:top|right|bottom|left|block|inline)(?:-(?:start|end))?)?|outline|box-shadow|text-shadow|text-decoration|background'
  const shorthand = new RegExp(`\\b(?:${shorthands})\\s*:[^;}]*?(?<![-\\w])(?:${keywords})(?![-\\w(])`, 'i')
  const ownColor = (code: string) =>
    code.match(named)?.[0] ?? code.match(literal)?.[0] ?? code.match(keyword)?.[0] ?? code.match(shorthand)?.[0]

  // The guard proves nothing until it flags each way of writing a color, and passes what the tokens are used through.
  it.each([
    'class="bg-red-500"',
    'class="bg-[#ff0000]"',
    'class="text-[#123]"',
    'class="bg-[red]"',
    'class="outline-red-500"',
    'class="shadow-red-500"',
    'class="from-red-500"',
    'class="decoration-red-500"',
    'class="accent-red-500"',
    '.x { color: red }',
    '.x { background: white; }',
    '{ color: \'red\' }',
    '.x { color: #fff }',
    '.x { color: rgb(0 0 0) }',
    '.x { color: hsl(0 0% 0%) }',
    '.x { color: hwb(0 0% 0%) }',
    '.x { color: lab(50% 0 0) }',
    '.x { color: lch(50% 0 0) }',
    '.x { color: oklab(0.5 0 0) }',
    '.x { color: oklch(0.5 0 0) }',
    '.x { color: color(srgb 1 0 0) }',
    '.x { border: 1px solid red }',
    '.x { outline: 2px solid blue }',
    '.x { box-shadow: 0 0 4px black }',
  ])('flags %s', (sample) => {
    expect(ownColor(sample)).toBeDefined()
  })

  it.each([
    'class="bg-primary text-muted-foreground border-border"',
    'class="bg-destructive-soft text-success"',
    '.x { background: var(--primary) }',
    '.x { border: 1px solid var(--border) }',
    '.x { border: 1px solid var(--chart-red) }',
    '.ds-editable { background: color-mix(in srgb, var(--primary-soft) 35%, transparent); }',
    '.x { color: currentColor; fill: none }',
    '{ color: token(\'--subtle-foreground\') }',
    'function mainColor(context) { return token(\'--primary\') }',
  ])('passes %s', (sample) => {
    expect(ownColor(sample)).toBeUndefined()
  })

  // The vendor file adds no color of its own: its #000 values are scroll-fade masks, which set transparency, and its
  // oklch() values derive from currentColor, in a shimmer utility that no other file in frontend/src uses (searched for
  // 'shimmer').
  const vendor = resolve(frontend, 'src/vendor/shadcn-vue-tailwind.css')
  const checked = sourceFiles(resolve(frontend, 'src')).filter(path => path !== tokens && path !== vendor)

  it.each(checked)('%s defines no color of its own', (path) => {
    expect(ownColor(readFileSync(path, 'utf-8'))).toBeUndefined()
  })
})

describe('rule 4: only the approved grid theme sets row and header height', () => {
  const designSystem = resolve(frontend, 'src/design-system')
  const height = /\b(?:getRowHeight|rowHeight|headerHeight)\b|\b(?:row|header)-height\b/

  it('no file in src/ outside src/design-system sets them', () => {
    const offenders = sourceFiles(resolve(frontend, 'src'))
      .filter(path => !path.startsWith(designSystem))
      .filter(path => height.test(readFileSync(path, 'utf-8')))
    expect(offenders).toEqual([])
  })

  it('the approved grid theme does', () => {
    expect(readFileSync(resolve(designSystem, 'grid-theme.js'), 'utf-8')).toMatch(height)
  })
})
