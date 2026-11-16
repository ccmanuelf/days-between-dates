// npm run backend: starts the backend on BACKEND_PORT, from ports.js. It serves the built page, so run `npm run build`
// first. The README's "Run it without Docker" section starts it this way.
import { spawn } from 'node:child_process'
import { fileURLToPath } from 'node:url'
import { readPorts } from '../ports.js'

const root = fileURLToPath(new URL('../../', import.meta.url))
const { backend: port } = readPorts()

const server = spawn(
  `${root}.venv/bin/python`,
  ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', String(port)],
  { cwd: root, stdio: 'inherit' },
)

server.on('error', (error) => {
  console.error(`Could not start the backend: ${error.message}. See the README's "Run it without Docker" section.`)
  process.exit(1)
})

// Ctrl-C in a terminal reaches the backend too, and it stops by itself. A SIGINT sent to this process alone (kill -INT,
// or a tool that stops only its own child) does not, so if the backend is still running a moment later, ask it to
// stop. With SIGTERM, not SIGINT: a second SIGINT makes uvicorn skip its clean shutdown.
process.on('SIGINT', () => {
  setTimeout(() => {
    if (server.exitCode === null && server.signalCode === null)
      server.kill('SIGTERM')
  }, 500)
})
// A plain kill reaches only this process, so pass it on.
process.on('SIGTERM', () => server.kill('SIGTERM'))

// Exit the way the backend did: with its code, or by the same signal, so a clean stop doesn't read as a failure.
server.on('exit', (code, signal) => {
  if (!signal)
    process.exit(code)
  process.removeAllListeners(signal)
  process.kill(process.pid, signal)
})
