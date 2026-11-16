<script setup lang="ts">
import type { VariantProps } from 'class-variance-authority'
import type { ToggleGroupRootEmits, ToggleGroupRootProps } from 'reka-ui'
import type { HTMLAttributes } from 'vue'
import type { toggleVariants } from '@/components/ui/toggle'
import { reactiveOmit } from '@vueuse/core'
import { cn } from 'cn'
import { ToggleGroupRoot, useForwardProps } from 'reka-ui'
import { provide, ref, watch } from 'vue'

type ToggleGroupVariants = VariantProps<typeof toggleVariants>

const props = withDefaults(defineProps<ToggleGroupRootProps & {
  class?: HTMLAttributes['class']
  variant?: ToggleGroupVariants['variant']
  size?: ToggleGroupVariants['size']
  spacing?: number
}>(), {
  spacing: 0,
})

const emits = defineEmits<ToggleGroupRootEmits>()

provide('toggleGroup', {
  variant: props.variant,
  size: props.size,
  spacing: props.spacing,
})

const delegatedProps = reactiveOmit(props, 'class', 'size', 'variant', 'modelValue', 'defaultValue')
const forwarded = useForwardProps(delegatedProps)

// A single-choice group always keeps a choice: reka-ui clears it when the selected item is clicked again.
const current = ref(props.modelValue ?? props.defaultValue)
watch(() => props.modelValue, (value) => {
  if (value !== undefined)
    current.value = value
})

function onChange(value: ToggleGroupRootProps['modelValue']) {
  if (props.type !== 'multiple' && (value === undefined || value === ''))
    return
  current.value = value
  emits('update:modelValue', value as never)
}
</script>

<template>
  <ToggleGroupRoot
    v-slot="slotProps"
    data-slot="toggle-group"
    :data-size="size"
    :data-variant="variant"
    :data-spacing="spacing"
    :style="{
      '--gap': spacing,
    }"
    v-bind="forwarded"
    :model-value="current"
    @update:model-value="onChange"
    :class="cn('rounded-md data-[size=sm]:rounded-[min(var(--radius-md),10px)] group/toggle-group flex w-fit flex-row items-center gap-[--spacing(var(--gap))] data-vertical:flex-col data-vertical:items-stretch', props.class)"
  >
    <slot v-bind="slotProps" />
  </ToggleGroupRoot>
</template>
