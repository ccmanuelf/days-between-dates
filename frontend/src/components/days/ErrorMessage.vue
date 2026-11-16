<script setup lang="ts">
import { OctagonAlertIcon } from '@lucide/vue'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { state } from '@/state'

// The one error message, shown where state.error.place says (SPEC, E1–E3). It is kept as a key, so a language
// switch rewrites it.
const { t } = useI18n()
const text = computed(() => {
  const error = state.error
  if (!error)
    return ''
  return t(error.key, { field: error.field ? t(`field_${error.field}`) : '' })
})
</script>

<template>
  <p
    id="error"
    role="alert"
    class="flex items-start gap-2 rounded-md border border-destructive bg-destructive-soft px-3 py-2 text-body font-medium text-destructive"
  >
    <OctagonAlertIcon class="mt-0.5 size-4 shrink-0" aria-hidden="true" />
    {{ text }}
  </p>
</template>
