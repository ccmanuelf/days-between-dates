import type { Component } from 'vue'
import { createApp, h } from 'vue'

// Mounts the real component with Vue itself, into a real element, and returns what it rendered.
export function mount(component: Component, props: Record<string, unknown> = {}, text = 'text') {
  const host = document.createElement('div')
  document.body.append(host)
  createApp({ render: () => h(component, props, () => text) }).mount(host)
  return host.firstElementChild as HTMLElement
}
