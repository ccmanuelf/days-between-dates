<script setup lang="ts">
import { useI18n } from 'vue-i18n'

// The User Guide, inside the app: one section per feature, with worked examples from the known answers (SPEC, S15,
// S16). It is static help with no backend; tests/test_guide.py reads each example from this text and counts it again.
const SECTIONS: [string, string[]][] = [
  ['range', ['help_range_dates', 'example_total']],
  ['business', ['example_weekend', 'example_business']],
  ['own', ['example_own']],
  ['reversed', ['example_reversed']],
  ['past', []],
  ['elections', []],
  ['language', []],
  ['sources', []],
]

const { t } = useI18n()
</script>

<template>
  <article id="help-body" class="mx-auto flex max-w-3xl flex-col gap-6">
    <p class="guide-intro text-body text-muted-foreground">
      {{ t('help_intro') }}
    </p>
    <nav class="guide-contents rounded-lg border border-border bg-card px-4 py-3" aria-labelledby="guide-contents-title">
      <p id="guide-contents-title" class="text-label text-muted-foreground">
        {{ t('help_contents') }}
      </p>
      <ol class="mt-2 list-decimal gap-x-8 pl-5 text-body-compact sm:columns-2">
        <li v-for="[id] in SECTIONS" :key="id" class="mb-1 break-inside-avoid">
          <a :href="`#guide-${id}`" class="text-primary underline underline-offset-2">{{ t(`help_${id}_title`) }}</a>
        </li>
      </ol>
    </nav>
    <section
      v-for="[id, examples] in SECTIONS"
      :id="`guide-${id}`"
      :key="id"
      class="guide-section flex scroll-mt-4 flex-col gap-2 border-t border-border pt-4"
      :aria-labelledby="`guide-${id}-title`"
    >
      <h2 :id="`guide-${id}-title`" class="text-heading-2">
        {{ t(`help_${id}_title`) }}
      </h2>
      <p v-for="(text, index) in t(`help_${id}`).split('\n\n')" :key="index" class="guide-text max-w-prose text-body">
        {{ text }}
      </p>
      <p
        v-for="key in examples"
        :key="key"
        class="guide-example rounded-md border border-border bg-card px-3 py-2 text-body tabular-nums"
        :data-example="key"
      >
        {{ t(key) }}
      </p>
    </section>
  </article>
</template>
