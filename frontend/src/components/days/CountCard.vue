<script setup lang="ts">
import type { AcceptableValue } from 'reka-ui'
import { useI18n } from 'vue-i18n'
import ErrorMessage from '@/components/days/ErrorMessage.vue'
import Field from '@/components/shared/Field.vue'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { ToggleGroup, ToggleGroupItem } from '@/components/ui/toggle-group'
import type { CalendarId } from '@/state'
import { count, state, switchCalendar } from '@/state'

const { t } = useI18n()

function chooseCalendar(value: AcceptableValue | AcceptableValue[]) {
  if ((value === 'mx' || value === 'us') && value !== state.calendar)
    switchCalendar(value as CalendarId)
}

function invalid(field: string) {
  return (state.error?.mark && state.error.field === field) || undefined
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle class="text-heading-2">
        {{ t('count_title') }}
      </CardTitle>
    </CardHeader>
    <CardContent class="flex flex-col gap-4">
      <form id="count-form" class="flex flex-col gap-4" @submit.prevent="count">
        <div class="grid gap-4 sm:grid-cols-2">
          <Field id="start" :label="t('start_label')">
            <template #default="{ id }">
              <Input
                :id="id"
                v-model="state.start"
                autocomplete="off"
                :placeholder="t('date_hint')"
                :aria-invalid="invalid('start')"
                :aria-describedby="invalid('start') && 'error'"
                class="tabular-nums"
              />
            </template>
          </Field>
          <Field id="end" :label="t('end_label')">
            <template #default="{ id }">
              <Input
                :id="id"
                v-model="state.end"
                autocomplete="off"
                :placeholder="t('date_hint')"
                :aria-invalid="invalid('end')"
                :aria-describedby="invalid('end') && 'error'"
                class="tabular-nums"
              />
            </template>
          </Field>
        </div>
        <div class="flex flex-col gap-1">
          <Label id="calendar-label" as="span">{{ t('calendar_label') }}</Label>
          <ToggleGroup
            id="calendar"
            :model-value="state.calendar"
            type="single"
            variant="outline"
            aria-labelledby="calendar-label"
            class="self-start"
            @update:model-value="chooseCalendar"
          >
            <ToggleGroupItem value="mx" data-value="mx">
              {{ t('calendar_mx') }}
            </ToggleGroupItem>
            <ToggleGroupItem value="us" data-value="us">
              {{ t('calendar_us') }}
            </ToggleGroupItem>
          </ToggleGroup>
        </div>
        <Button id="count" type="submit" variant="primary" class="self-start px-4">
          {{ t('count_button') }}
        </Button>
      </form>
      <ErrorMessage v-if="state.error?.place === 'count'" />
    </CardContent>
  </Card>
</template>
