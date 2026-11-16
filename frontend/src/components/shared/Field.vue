<script setup lang="ts">
import { useId } from 'vue'
import { Label } from '@/components/ui/label'

// Rule 6: the label sits above the control and points to it. Give the slot's id to the control; a page that names
// its controls passes its own id.
const props = defineProps<{ label: string, id?: string }>()

const id = props.id ?? useId()
</script>

<template>
  <div class="flex flex-col gap-1">
    <Label :for="id">{{ label }}</Label>
    <slot :id="id" />
  </div>
</template>
