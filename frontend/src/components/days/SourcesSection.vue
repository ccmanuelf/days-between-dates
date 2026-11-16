<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { state } from '@/state'

const { t } = useI18n()

// The official title stays as published, in its own language; the words around it are the page's (Q21).
function around(key: string) {
  const [before, after] = t(`source_${key.toLowerCase()}`, { title: '{title}' }).split('{title}')
  return { before, after }
}
</script>

<template>
  <section id="sources" class="flex flex-col gap-3" aria-labelledby="sources-title">
    <h2 id="sources-title" class="text-heading-2">
      {{ t('sources_title') }}
    </h2>
    <div id="sources-list" class="grid gap-x-8 gap-y-4 md:grid-cols-2">
      <div v-for="calendar in state.calendars" :key="calendar.id" class="calendar-sources" :data-calendar="calendar.id">
        <h3 class="text-heading-compact">
          {{ t(`calendar_${calendar.id}`) }}
        </h3>
        <p class="checked text-label text-muted-foreground">
          {{ t('checked', { date: calendar.checked }) }}
        </p>
        <ul class="mt-2 flex list-disc flex-col gap-2 pl-5 text-body-compact">
          <li v-for="source in calendar.sources" :key="source.key">
            {{ around(source.key).before }}<a
              :href="source.url"
              class="text-primary underline underline-offset-2"
            >{{ source.title }}</a>{{ around(source.key).after }} ({{ t('retrieved', { date: source.retrieved }) }})
          </li>
        </ul>
      </div>
    </div>
  </section>
</template>
