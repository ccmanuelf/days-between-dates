import { fileURLToPath, URL } from 'node:url'
import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vitest/config'
import { readPorts } from './ports.js'

const src = (path: string) => fileURLToPath(new URL(`./src/${path}`, import.meta.url))
const ports = readPorts()

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  define: {
    // vue-i18n's feature flags: the Composition API only, no devtools hook in production.
    __VUE_I18N_FULL_INSTALL__: true,
    __VUE_I18N_LEGACY_API__: false,
    __INTLIFY_PROD_DEVTOOLS__: false,
  },
  server: {
    // npm run dev serves the page on FRONTEND_PORT, and stops if that port is taken instead of moving to another one.
    // The API stays in the backend, which has to be running on BACKEND_PORT. Both come from ports.js.
    port: ports.frontend,
    strictPort: true,
    proxy: { '/api': `http://127.0.0.1:${ports.backend}` },
  },
  resolve: {
    alias: {
      // Generated shadcn-vue components import from 'cn'. It resolves to src/lib/utils.ts, which knows the tokens.
      cn: src('lib/utils.ts'),
      '@': src(''),
    },
  },
  test: {
    environment: 'jsdom',
    include: ['tests/unit/**/*.test.ts'],
  },
})
