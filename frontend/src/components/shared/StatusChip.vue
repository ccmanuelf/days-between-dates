<script setup lang="ts">
import { CircleCheckIcon, CircleIcon, OctagonAlertIcon, TriangleAlertIcon } from '@lucide/vue'
import { computed } from 'vue'
import { cn } from '@/lib/utils'

// Rule 2: every status is an icon plus a word, so it can still be read without its color.
const props = defineProps<{
  tone: 'success' | 'warning' | 'danger' | 'neutral'
  label: string
  chip?: boolean
}>()

const icons = {
  success: CircleCheckIcon,
  warning: TriangleAlertIcon,
  danger: OctagonAlertIcon,
  neutral: CircleIcon,
}

const chipClasses = {
  success: 'bg-success-soft',
  warning: 'bg-warning-soft',
  danger: 'bg-destructive-soft',
  neutral: 'bg-muted',
}

const icon = computed(() => icons[props.tone])
</script>

<template>
  <span
    data-slot="status-chip"
    :class="cn('ds-status', `ds-status--${tone}`, chip && ['rounded-sm px-2 py-0.5', chipClasses[tone]])"
  >
    <component :is="icon" aria-hidden="true" />
    {{ label }}
  </span>
</template>
