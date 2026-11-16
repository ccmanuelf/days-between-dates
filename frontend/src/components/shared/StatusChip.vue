<script setup lang="ts">
import { CircleCheckIcon, OctagonAlertIcon } from '@lucide/vue'
import { computed } from 'vue'
import { cn } from '@/lib/utils'

// Rule 2: every status is an icon plus a word, so it can still be read without its color. The starter's chip also has
// warning and neutral tones; this app shows two statuses, so it keeps two.
const props = defineProps<{
  tone: 'success' | 'danger'
  label: string
}>()

const icons = {
  success: CircleCheckIcon,
  danger: OctagonAlertIcon,
}

const icon = computed(() => icons[props.tone])
</script>

<template>
  <span data-slot="status-chip" :class="cn('ds-status', `ds-status--${tone}`)">
    <component :is="icon" aria-hidden="true" />
    {{ label }}
  </span>
</template>
