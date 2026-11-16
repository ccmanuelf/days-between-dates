<script setup lang="ts">
import type { ColDef } from 'ag-grid-community'
import { computed, markRaw } from 'vue'
import { useI18n } from 'vue-i18n'
import ErrorMessage from '@/components/days/ErrorMessage.vue'
import RemoveCell from '@/components/days/RemoveCell.vue'
import DataGrid from '@/components/shared/DataGrid.vue'
import Field from '@/components/shared/Field.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { addHoliday, removeHoliday, state } from '@/state'

const { t, locale } = useI18n()

// The weekday, named by the browser in the page's language: a day of one's own on a weekend changes no count (S8).
function weekday(day: string) {
  return new Intl.DateTimeFormat(locale.value, { weekday: 'long', timeZone: 'UTC' }).format(new Date(`${day}T00:00:00Z`))
}

const columns = computed<ColDef[]>(() => [
  { colId: 'day', field: 'day', headerName: t('own_col_day'), cellClass: 'tabular-nums' },
  { colId: 'weekday', field: 'weekday', headerName: t('own_col_weekday'), flex: 1 },
  {
    colId: 'action',
    headerName: t('own_col_action'),
    sortable: false,
    cellRenderer: markRaw(RemoveCell),
    cellRendererParams: {
      text: t('remove_button'),
      label: (day: string) => t('remove_label', { day }),
      onRemove: removeHoliday,
    },
  },
])
const rows = computed(() => state.ownDays.map(day => ({ id: day, day, weekday: weekday(day) })))
const invalid = computed(() => (state.error?.mark && state.error.field === 'day') || undefined)
</script>

<template>
  <Card id="own">
    <CardHeader>
      <CardTitle id="own-title" class="text-heading-2">
        {{ t('own_title', { name: t(`calendar_${state.calendar}`) }) }}
      </CardTitle>
    </CardHeader>
    <CardContent class="flex flex-col gap-4">
      <div v-if="state.ownDays.length" id="own-list">
        <DataGrid :rows="rows" :columns="columns" />
      </div>
      <p v-else-if="state.ownLoaded" id="own-empty" class="text-body text-muted-foreground">
        {{ t('own_empty') }}
      </p>
      <form id="add-form" class="flex flex-wrap items-end gap-2" @submit.prevent="addHoliday">
        <Field id="new-day" :label="t('add_label')" class="min-w-40 flex-1">
          <template #default="{ id }">
            <Input
              :id="id"
              v-model="state.newDay"
              autocomplete="off"
              :placeholder="t('date_hint')"
              :aria-invalid="invalid"
              :aria-describedby="invalid && 'error'"
              class="tabular-nums"
            />
          </template>
        </Field>
        <Button id="add" type="submit">
          {{ t('add_button') }}
        </Button>
      </form>
      <ErrorMessage v-if="state.error?.place === 'add'" />
    </CardContent>
  </Card>
</template>
