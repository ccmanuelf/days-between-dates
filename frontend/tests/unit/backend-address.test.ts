// @vitest-environment node
import { readFileSync } from 'node:fs'
import { expect, it } from 'vitest'
import { readPorts } from '../../ports.js'
import viteConfig from '../../vite.config'

const ports = readPorts()

it('the dev proxy reaches the backend on BACKEND_PORT', () => {
  const proxy = new URL(viteConfig.server?.proxy?.['/api'] as string)
  expect(`${proxy.hostname}:${proxy.port}`).toBe(`127.0.0.1:${ports.backend}`)
})

it('npm run dev serves the page on FRONTEND_PORT, and stops rather than move to another port', () => {
  expect(viteConfig.server?.port).toBe(ports.frontend)
  expect(viteConfig.server?.strictPort).toBe(true)
})

it('npm run backend starts the app on BACKEND_PORT from ports.js, on 127.0.0.1', () => {
  const script = readFileSync(new URL('../../scripts/backend.js', import.meta.url), 'utf8')
  expect(script).toContain('readPorts()')
  expect(script).toMatch(/'--host', '127\.0\.0\.1', '--port', String\(port\)/)
})

it('neither the config nor the script writes a port number: both take it from ports.js', () => {
  for (const file of ['vite.config.ts', 'scripts/backend.js']) {
    const text = readFileSync(new URL(`../../${file}`, import.meta.url), 'utf8')
    expect(text, file).not.toMatch(/(127\.0\.0\.1|localhost):\d|--port\s+\d|\bport:\s*\d|\b(8000|5173)\b/)
  }
})
