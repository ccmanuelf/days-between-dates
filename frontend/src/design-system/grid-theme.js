// Visual standard, batch 3: AG Grid theme. Approved by Manuel, 2026-11-03.
// Its colors come from the batch 1 tokens (tokens.css), so light and dark follow the .dark class with no
// second theme. For AG Grid Community 36 (Theming API). Rows are fixed at 32px (rule 4).
import { themeQuartz } from 'ag-grid-community'

export const gridTheme = themeQuartz.withParams({
  // Type: Inter at 13px in cells, 12px semibold headers. AG Grid needs the font stack written out.
  fontFamily: "'Inter', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, Arial, sans-serif",
  fontSize: 13,
  headerFontSize: 12,
  headerFontWeight: 600,

  // Density (rule 4): 32px rows, 36px header, 12px cell padding.
  rowHeight: 32,
  headerHeight: 36,
  spacing: 6,
  cellHorizontalPadding: 12,

  // Color, all from the tokens.
  backgroundColor: 'var(--card)',
  foregroundColor: 'var(--foreground)',
  headerBackgroundColor: 'var(--secondary)',
  headerTextColor: 'var(--muted-foreground)',
  chromeBackgroundColor: 'var(--secondary)',
  oddRowBackgroundColor: 'var(--card)',          // no zebra stripes; row lines instead
  rowHoverColor: 'var(--accent)',
  selectedRowBackgroundColor: 'var(--primary-soft)', // rule 1: the selected row
  accentColor: 'var(--primary)',                 // checkboxes, focus, column move hints
  borderColor: 'var(--border)',
  inputBorder: { color: 'var(--input)' },        // cell editors use the field outline
  inputFocusBorder: { color: 'var(--ring)' },

  // Shape: the grid is a card (8px), controls inside it are 6px.
  wrapperBorderRadius: 8,
  borderRadius: 6,
  wrapperBorder: true,
  rowBorder: true,
  columnBorder: false,
  headerColumnBorder: false,

  browserColorScheme: 'inherit',
})

// Grid options every grid starts from (rules 4, 5 and 7).
export const gridDefaults = {
  theme: gridTheme,
  rowHeight: 32,
  defaultColDef: { sortable: true, resizable: true, suppressMovable: true },
  rowSelection: { mode: 'singleRow', checkboxes: false, enableClickSelection: true }, // a row click selects; the chart follows
  singleClickEdit: true,
  stopEditingWhenCellsLoseFocus: true,
  animateRows: false,
}

// Rule 5: size every column to its content except the one flexible text column (marked flex: 1).
export function autoSizeFor(columnDefs) {
  return { type: 'fitCellContents', colIds: columnDefs.filter((c) => !c.flex).map((c) => c.colId || c.field) }
}

// Number columns: right-aligned with tabular figures. Use as { field: 'hours', ...numberColumn(1) }.
export const numberColumn = (digits = 0) => ({
  type: 'rightAligned', // AG Grid's own right-aligned type; grid-theme.css adds tabular figures
  valueFormatter: (p) => (p.value == null ? '' : Number(p.value).toFixed(digits)),
})

// Editable cells get a light tint so the user can see what they can change.
export const editableColumn = { editable: true, cellClassRules: { 'ds-editable': () => true } }
