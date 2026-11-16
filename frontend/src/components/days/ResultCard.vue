<script setup lang="ts">
import type { ColDef } from 'ag-grid-community'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import HowPanel from '@/components/days/HowPanel.vue'
import NoticeLine from '@/components/days/NoticeLine.vue'
import DataGrid from '@/components/shared/DataGrid.vue'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { numberColumn } from '@/design-system/grid-theme.js'
import { state } from '@/state'

const { t } = useI18n()
const result = computed(() => state.result!)

// Both conventions side by side: the start date not counted, and both dates counted (SPEC, S1).
const columns = computed<ColDef[]>(() => [
  { colId: 'name', field: 'name', headerName: t('col_days'), flex: 1, sortable: false },
  { colId: 'snc', field: 'snc', headerName: t('col_start_not_counted'), sortable: false, ...numberColumn(0) },
  { colId: 'bc', field: 'bc', headerName: t('col_both_counted'), sortable: false, ...numberColumn(0) },
])
const rows = computed(() => [
  { id: 'total', name: t('row_total'), snc: result.value.total.start_not_counted, bc: result.value.total.both_counted },
  {
    id: 'business',
    name: t('row_business'),
    snc: result.value.business.start_not_counted,
    bc: result.value.business.both_counted,
  },
])
</script>

<template>
  <Card id="result" class="dbd-enter">
    <CardHeader class="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
      <h2 class="text-heading-2">
        {{ t('result_title') }}
      </h2>
      <p id="active-calendar" class="text-label text-muted-foreground">
        {{ t('active_calendar', { name: t(`calendar_${result.calendar}`) }) }}
      </p>
    </CardHeader>
    <CardContent class="flex flex-col gap-3">
      <p id="range" class="text-heading-3 tabular-nums">
        {{ t('range', { start: result.start, end: result.end }) }}
      </p>
      <NoticeLine
        v-if="result.swapped"
        id="notice-swapped"
        :word="t('notice_swapped_word')"
        :text="t('notice_swapped')"
      />
      <NoticeLine
        v-if="result.past_years"
        id="notice-past-years"
        :word="t('notice_past_years_word')"
        :text="t('notice_past_years')"
      />
      <div id="result-grid">
        <DataGrid :rows="rows" :columns="columns" />
      </div>
      <HowPanel
        id="how-total"
        :title="t('how_total_title')"
        :formula="t('how_total')"
        :example="t('example_total')"
      />
      <HowPanel
        id="how-business"
        :title="t('how_business_title')"
        :formula="t('how_business')"
        :example="t('example_business')"
      />
      <p v-if="result.calendar === 'mx'" id="note-local-elections" class="note text-body text-muted-foreground">
        {{ t('note_local_elections') }}
      </p>
      <p v-if="state.language === 'es'" id="note-business-days" class="note text-body text-muted-foreground">
        {{ t('note_business_days') }}
      </p>
    </CardContent>
  </Card>
</template>
