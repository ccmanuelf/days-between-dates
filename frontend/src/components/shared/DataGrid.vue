<script setup lang="ts">
import type { AutoSizeStrategy, CellValueChangedEvent, ColDef, GridApi, GridOptions, GridReadyEvent, SelectionChangedEvent, Theme } from 'ag-grid-community'
import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community'
import { AgGridVue } from 'ag-grid-vue3'
import { watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { autoSizeFor, gridDefaults } from '@/design-system/grid-theme.js'

ModuleRegistry.registerModules([AllCommunityModule])

type Row = Record<string, any>
type RowId = string | number

const props = withDefaults(defineProps<{
  rows: Row[]
  columns: ColDef[]
  selectedId?: RowId | null
  rowId?: string
}>(), {
  selectedId: null,
  rowId: 'id',
})

const emit = defineEmits<{
  // null when the user clears the selection in the grid (Space or Ctrl/Cmd-click on the selected row).
  select: [id: RowId | null]
  cellEdit: [change: { id: RowId, field: string, value: unknown }]
}>()

const { t, locale } = useI18n()

let api: GridApi | undefined

function syncSelection() {
  if (!api)
    return
  const node = props.selectedId === null ? undefined : api.getRowNode(String(props.selectedId))
  if (node)
    node.setSelected(true, true, 'api')
  else
    api.deselectAll('all', 'api')
}

// grid-theme.js is plain JavaScript, so TypeScript reads its fixed strings (the row selection mode, the sizing
// strategy) as any string. These two lines give its values AG Grid's types; the approved file stays as it is.
const defaults = gridDefaults as GridOptions<Row>
// A grid that sizes to its rows (domLayout autoHeight) takes only the room they need: AG Grid otherwise keeps 150px
// for its body. The approved theme stays as it is; this app derives from it.
const theme = (defaults.theme as Theme).withParams({ autoHeightMinBodyHeight: 0 })
const autoSizeStrategy = (columns: ColDef[]) => autoSizeFor(columns) as AutoSizeStrategy<Row>

// Rule 5: columns fit their content. Inter loads after the first paint, so measure again once it has.
function fitColumns() {
  api?.autoSizeColumns(autoSizeFor(props.columns).colIds)
}

function onGridReady(event: GridReadyEvent) {
  api = event.api
  syncSelection()
  document.fonts?.ready.then(fitColumns)
}

function onSelectionChanged(event: SelectionChangedEvent) {
  if (event.source === 'api')
    return
  const [row] = event.api.getSelectedRows()
  emit('select', row ? row[props.rowId] : null)
}

function onCellValueChanged(event: CellValueChangedEvent) {
  emit('cellEdit', {
    id: event.data[props.rowId],
    field: event.colDef.field ?? '',
    value: event.newValue,
  })
}

function onRowDataUpdated() {
  syncSelection()
  fitColumns()
}

watch(() => props.selectedId, syncSelection)
watch(() => props.columns, fitColumns, { flush: 'post' })
</script>

<template>
  <!-- AG Grid reads its own text once, so a language change builds the grid again. -->
  <AgGridVue
    :key="locale"
    v-bind="defaults"
    :theme="theme"
    class="w-full"
    dom-layout="autoHeight"
    :row-data="rows"
    :column-defs="columns"
    :auto-size-strategy="autoSizeStrategy(columns)"
    :get-row-id="(params: { data: Row }) => String(params.data[rowId])"
    :locale-text="{ noRowsToShow: t('grid.noRows') }"
    @grid-ready="onGridReady"
    @selection-changed="onSelectionChanged"
    @cell-value-changed="onCellValueChanged"
    @row-data-updated="onRowDataUpdated"
  />
</template>
