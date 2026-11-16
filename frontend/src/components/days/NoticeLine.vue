<script setup lang="ts">
import { TriangleAlertIcon } from '@lucide/vue'

// Rule 2: a notice is an icon and a word, then its sentence; the color backs them up.
defineProps<{ word: string, text: string }>()
</script>

<template>
  <div class="flex items-start gap-2 rounded-md bg-warning-soft px-3 py-2 text-body text-foreground">
    <TriangleAlertIcon class="mt-0.5 size-4 shrink-0 text-warning" aria-hidden="true" />
    <p>
      <span class="notice-word font-semibold">{{ word }}.</span>{{ ' ' }}<span class="notice-text">{{ text }}</span>
    </p>
  </div>
</template>
