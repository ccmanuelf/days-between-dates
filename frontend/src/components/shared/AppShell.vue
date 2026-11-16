<script setup lang="ts">
import type { AcceptableValue } from 'reka-ui'
import { MoonIcon, SunIcon } from '@lucide/vue'
import { useEventListener } from '@vueuse/core'
import { watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
import StatusChip from '@/components/shared/StatusChip.vue'
import { Button } from '@/components/ui/button'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import type { Language } from '@/i18n'
import { checkStorage, state, switchLanguage, toggleTheme } from '@/state'

const { t } = useI18n()

watchEffect(() => {
  document.title = t('title')
})

// The storage status is read on load (state.start) and again when someone comes back to the page; no polling.
useEventListener(document, 'visibilitychange', () => {
  if (document.visibilityState === 'visible' && state.ready)
    checkStorage()
})

function chooseLanguage(value: AcceptableValue | AcceptableValue[]) {
  if ((value === 'en' || value === 'es') && value !== state.language)
    switchLanguage(value as Language)
}
</script>

<template>
  <div class="flex min-h-dvh flex-col">
    <header class="flex min-h-12 flex-wrap items-center gap-x-4 gap-y-2 border-b border-border bg-card px-4 py-2">
      <h1 class="text-heading-compact">
        {{ t('title') }}
      </h1>
      <div class="ml-auto flex items-center gap-2">
        <!-- Always present, so a screen reader announces the words when they arrive: a live region that appears
             already filled is often skipped. -->
        <div role="status" class="flex">
          <StatusChip
            v-if="state.storage !== 'checking'"
            id="storage-status"
            :tone="state.storage === 'ok' ? 'success' : 'danger'"
            :label="t(state.storage === 'ok' ? 'storage_ok' : 'storage_down')"
          />
        </div>
        <ToggleGroup
          id="language"
          :model-value="state.language"
          type="single"
          variant="outline"
          size="sm"
          :aria-label="t('language_label')"
          @update:model-value="chooseLanguage"
        >
          <ToggleGroupItem value="en" data-value="en" :aria-label="t('language_en')">
            EN
          </ToggleGroupItem>
          <ToggleGroupItem value="es" data-value="es" :aria-label="t('language_es')">
            ES
          </ToggleGroupItem>
        </ToggleGroup>
        <Button
          id="theme"
          variant="ghost"
          size="icon"
          :aria-label="t(state.theme === 'dark' ? 'theme_to_light' : 'theme_to_dark')"
          :aria-pressed="state.theme === 'dark'"
          @click="toggleTheme"
        >
          <SunIcon v-if="state.theme === 'dark'" />
          <MoonIcon v-else />
        </Button>
      </div>
    </header>
    <main class="mx-auto w-full max-w-6xl flex-1 p-4">
      <slot />
    </main>
  </div>
</template>
