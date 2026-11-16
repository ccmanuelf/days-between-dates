<script setup lang="ts">
import type { AutoSizeStrategy, ColDef, GridApi, GridOptions, GridReadyEvent, Theme } from 'ag-grid-community'
import { AllCommunityModule, ModuleRegistry } from 'ag-grid-community'
import { AgGridVue } from 'ag-grid-vue3'
import { useI18n } from 'vue-i18n'
import { autoSizeFor, gridDefaults } from '@/design-system/grid-theme.js'

ModuleRegistry.registerModules([AllCommunityModule])

type Row = Record<string, any>

// The starter's grid, kept to what this app uses: rows to show, no selection and no editing.
const props = withDefaults(defineProps<{
  rows: Row[]
  columns: ColDef[]
  rowId?: string
}>(), {
  rowId: 'id',
})

const { t, locale } = useI18n()

let api: GridApi | undefined

// grid-theme.js is plain JavaScript, so TypeScript reads its fixed strings (the sizing strategy) as any string. These
// lines give its values AG Grid's types; the approved file stays as it is. Rows here are read, not chosen, so the
// approved defaults' row selection is switched off.
const defaults = { ...(gridDefaults as GridOptions<Row>), rowSelection: undefined }
const autoSizeStrategy = (columns: ColDef[]) => autoSizeFor(columns) as AutoSizeStrategy<Row>
// A grid that sizes to its rows (domLayout autoHeight) takes only the room they need: AG Grid otherwise keeps 150px
// for its body. The approved theme stays as it is; this app derives from it.
const theme = (defaults.theme as Theme).withParams({ autoHeightMinBodyHeight: 0 })

// Rule 5: columns fit their content. Inter loads after the first paint, so measure again once it has.
function fitColumns() {
  api?.autoSizeColumns(autoSizeFor(props.columns).colIds)
}

function onGridReady(event: GridReadyEvent) {
  api = event.api
  document.fonts?.ready.then(fitColumns)
}
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
    :locale-text="{ noRowsToShow: t('grid_no_rows') }"
    @grid-ready="onGridReady"
    @row-data-updated="fitColumns"
  />
</template>
