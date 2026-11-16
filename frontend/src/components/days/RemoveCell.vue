<script setup lang="ts">
import type { ICellRendererParams } from 'ag-grid-community'
import { Button } from '@/components/ui/button'

// The grid's action cell for one day of one's own: an outlined button whose name includes its date (SPEC, S14).
const props = defineProps<{
  params: ICellRendererParams & { text: string, label: (day: string) => string, onRemove: (day: string) => void }
}>()
</script>

<template>
  <Button
    type="button"
    size="xs"
    class="remove"
    :aria-label="props.params.label(props.params.data.day)"
    @click="props.params.onRemove(props.params.data.day)"
  >
    {{ props.params.text }}
  </Button>
</template>
