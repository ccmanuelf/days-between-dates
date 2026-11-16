<script setup lang="ts">
import { BookOpenIcon, CalculatorIcon } from '@lucide/vue'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import CountCard from '@/components/days/CountCard.vue'
import ErrorMessage from '@/components/days/ErrorMessage.vue'
import OwnHolidaysCard from '@/components/days/OwnHolidaysCard.vue'
import ResultCard from '@/components/days/ResultCard.vue'
import SourcesSection from '@/components/days/SourcesSection.vue'
import UserGuide from '@/components/days/UserGuide.vue'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { state } from '@/state'

const { t } = useI18n()

// One status message per count, in the page's language, for screen readers (SPEC, S14).
const announcement = computed(() => {
  const r = state.result
  if (!r)
    return ''
  const parts = [t('announce_result', {
    calendar: t(`calendar_${r.calendar}`),
    start: r.start,
    end: r.end,
    total_snc: r.total.start_not_counted,
    total_bc: r.total.both_counted,
    business_snc: r.business.start_not_counted,
    business_bc: r.business.both_counted,
  })]
  if (r.swapped)
    parts.push(t('notice_swapped'))
  if (r.past_years)
    parts.push(t('notice_past_years'))
  return parts.join(' ')
})
</script>

<template>
  <ErrorMessage v-if="state.error?.place === 'top'" class="mb-4" />
  <p id="announce" class="sr-only" role="status" aria-atomic="true">
    {{ announcement }}
  </p>
  <p class="tagline mb-3 text-body text-muted-foreground">
    {{ t('tagline') }}
  </p>
  <Tabs default-value="count" class="gap-4">
    <TabsList class="self-start">
      <TabsTrigger value="count" data-tab="count">
        <CalculatorIcon aria-hidden="true" />
        {{ t('tab_count') }}
      </TabsTrigger>
      <TabsTrigger value="guide" data-tab="guide">
        <BookOpenIcon aria-hidden="true" />
        {{ t('help_title') }}
      </TabsTrigger>
    </TabsList>
    <TabsContent value="count" class="dbd-enter flex flex-col gap-6">
      <div class="grid items-start gap-4 lg:grid-cols-[minmax(0,26rem)_minmax(0,1fr)]">
        <div class="flex flex-col gap-4">
          <CountCard />
          <OwnHolidaysCard />
        </div>
        <ResultCard v-if="state.result" />
      </div>
      <SourcesSection />
    </TabsContent>
    <TabsContent value="guide" class="dbd-enter">
      <UserGuide />
    </TabsContent>
  </Tabs>
</template>
