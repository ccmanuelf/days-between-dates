<script setup lang="ts">
import { onMounted } from 'vue'
import AppShell from '@/components/shared/AppShell.vue'
import DaysScreen from '@/components/days/DaysScreen.vue'
import { start } from '@/state'

onMounted(start)
</script>

<template>
  <AppShell>
    <DaysScreen />
  </AppShell>
</template>
