<script setup lang="ts">
import { ChevronDownIcon } from '@lucide/vue'

// "How this is calculated" under the result: the formula, then a worked example from the known answers (SPEC, S16).
// Static help, like the User Guide: it calls no route.
defineProps<{ id: string, title: string, formula: string, example: string }>()
</script>

<template>
  <details :id="id" class="how group rounded-md border border-border bg-card">
    <summary
      :id="`${id}-toggle`"
      class="flex min-h-8 cursor-pointer list-none items-center gap-2 px-3 py-1.5 text-body-compact font-medium [&::-webkit-details-marker]:hidden"
    >
      <ChevronDownIcon
        class="size-4 shrink-0 text-muted-foreground transition-transform duration-[var(--duration-base)] ease-[var(--ease-in-out)] group-open:rotate-180 motion-reduce:transition-none"
        aria-hidden="true"
      />
      {{ title }}
    </summary>
    <div class="flex flex-col gap-2 border-t border-border px-3 py-2 text-body">
      <p class="how-text">
        {{ formula }}
      </p>
      <p class="how-example rounded-sm bg-secondary px-2 py-1 tabular-nums">
        {{ example }}
      </p>
    </div>
  </details>
</template>
