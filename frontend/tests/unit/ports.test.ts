// @vitest-environment node
import { spawnSync } from 'node:child_process'
import { copyFileSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { parseEnv } from 'node:util'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'
import { DEFAULTS, readPorts, STARTER_ENV } from '../../ports.js'

const starter = (file: string) => fileURLToPath(new URL(`../../../${file}`, import.meta.url))

let folder: string
beforeEach(() => {
  folder = mkdtempSync(join(tmpdir(), 'ports-test-'))
})
afterEach(() => rmSync(folder, { recursive: true, force: true }))

const noFile = () => join(folder, 'missing.env')
function envFile(text: string) {
  const path = join(folder, '.env')
  writeFileSync(path, text)
  return path
}

describe('readPorts', () => {
  it('with no .env and nothing set, the defaults: 8765 for the backend and 5765 for the page', () => {
    expect(readPorts({ envFile: noFile(), environment: {} })).toEqual({ backend: 8765, frontend: 5765 })
  })

  it('takes the ports from .env', () => {
    const file = envFile('# this machine\nBACKEND_PORT=8811\nFRONTEND_PORT=5811\n')
    expect(readPorts({ envFile: file, environment: {} })).toEqual({ backend: 8811, frontend: 5811 })
  })

  it('a variable set in the environment wins over .env, one setting at a time', () => {
    const file = envFile('BACKEND_PORT=8811\nFRONTEND_PORT=5811\n')
    expect(readPorts({ envFile: file, environment: { BACKEND_PORT: '8912' } })).toEqual({ backend: 8912, frontend: 5811 })
  })

  it('an empty setting counts as not set', () => {
    const file = envFile('BACKEND_PORT=\n')
    expect(readPorts({ envFile: file, environment: { FRONTEND_PORT: '' } })).toEqual({ backend: 8765, frontend: 5765 })
  })

  // The range and its source, RFC 6335 section 6, are in ports.js.
  it('accepts both ends of the range, 1024 and 65535', () => {
    const environment = { BACKEND_PORT: '1024', FRONTEND_PORT: '65535' }
    expect(readPorts({ envFile: noFile(), environment })).toEqual({ backend: 1024, frontend: 65535 })
  })

  it.each(['abc', '87.10', '-8710', '8710x', '80', '1023', '65536'])('stops on BACKEND_PORT=%s, naming the setting', (value) => {
    expect(() => readPorts({ envFile: noFile(), environment: { BACKEND_PORT: value } }))
      .toThrow(`BACKEND_PORT must be a whole number from 1024 to 65535, not "${value}"`)
  })

  it('stops on a bad FRONTEND_PORT in .env too', () => {
    const file = envFile('FRONTEND_PORT=5173.5\n')
    expect(() => readPorts({ envFile: file, environment: {} }))
      .toThrow('FRONTEND_PORT must be a whole number from 1024 to 65535, not "5173.5"')
  })

  it('stops when the two ports are the same', () => {
    const file = envFile('BACKEND_PORT=8811\nFRONTEND_PORT=8811\n')
    expect(() => readPorts({ envFile: file, environment: {} }))
      .toThrow('BACKEND_PORT and FRONTEND_PORT must differ, both are 8811')
  })

  it('reads the .env at the repository\'s root, next to frontend/ and app/', () => {
    expect(STARTER_ENV).toBe(starter('.env'))
  })
})

describe('.env files', () => {
  it('.env.example shows exactly the two settings, with the defaults ports.js uses', () => {
    const example = parseEnv(readFileSync(starter('.env.example'), 'utf8'))
    expect({ ...example }).toEqual({
      BACKEND_PORT: String(DEFAULTS.BACKEND_PORT),
      FRONTEND_PORT: String(DEFAULTS.FRONTEND_PORT),
    })
  })

  it('the repository\'s .gitignore, alone in a new repository, keeps .env and .env.local out and .env.example in', () => {
    const git = (...args: string[]) => spawnSync('git', ['-c', 'core.excludesFile=/dev/null', ...args], { cwd: folder })
    expect(git('init', '-q').status).toBe(0)
    copyFileSync(starter('.gitignore'), join(folder, '.gitignore'))
    // check-ignore exits 0 when the file is ignored and 1 when it is not; anything else is an error.
    const ignored = (file: string) => {
      const { status } = git('check-ignore', '-q', file)
      if (status !== 0 && status !== 1)
        throw new Error(`git check-ignore ${file} exited ${status}`)
      return status === 0
    }
    expect({ '.env': ignored('.env'), '.env.local': ignored('.env.local'), '.env.example': ignored('.env.example') })
      .toEqual({ '.env': true, '.env.local': true, '.env.example': false })
  })
})
