// The app's two ports, read in one place: vite.config.ts and `npm run backend` take them from here. A variable set in
// the environment wins, then the .env at the repository's root, then the default.
import { existsSync, readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { parseEnv } from 'node:util'

// Off 8000 and 5173, uvicorn's and Vite's default ports (https://uvicorn.dev/settings/ and
// https://vite.dev/config/server-options#server-port, both retrieved 2026-11-11), so the app runs next to others
// that use them. This app's own pair: each app made from the web starter picks its own.
export const DEFAULTS = { BACKEND_PORT: 8765, FRONTEND_PORT: 5765 }

// The repository's root, next to frontend/ and app/: one file for both halves.
export const STARTER_ENV = fileURLToPath(new URL('../.env', import.meta.url))

/** @returns {{ backend: number, frontend: number }} */
export function readPorts({ envFile = STARTER_ENV, environment = process.env } = {}) {
  const file = existsSync(envFile) ? parseEnv(readFileSync(envFile, 'utf8')) : {}
  const port = (name) => {
    // An empty setting counts as not set.
    const value = environment[name] || file[name] || String(DEFAULTS[name])
    // 1024 to 65535: RFC 6335's User Ports (1024-49151) and Dynamic Ports (49152-65535); below 1024 are its System
    // Ports. https://www.rfc-editor.org/rfc/rfc6335.html#section-6 (retrieved 2026-11-11).
    if (!/^\d+$/.test(value) || Number(value) < 1024 || Number(value) > 65535)
      throw new Error(`${name} must be a whole number from 1024 to 65535, not "${value}"`)
    return Number(value)
  }
  const ports = { backend: port('BACKEND_PORT'), frontend: port('FRONTEND_PORT') }
  if (ports.backend === ports.frontend)
    throw new Error(`BACKEND_PORT and FRONTEND_PORT must differ, both are ${ports.backend}`)
  return ports
}
