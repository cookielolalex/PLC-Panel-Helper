
param(
  [Parameter(Mandatory=$true)][string]$WorkbookPath,
  [Parameter(Mandatory=$true)][string]$OutputDir
)
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

function Escape-CsvCell([string]$Value) {
  if ($null -eq $Value) { $Value = '' }
  $Value = $Value -replace '"', '""'
  if ($Value.Contains(',') -or $Value.Contains('"') -or $Value.Contains("`n") -or $Value.Contains("`r")) {
    return '"' + $Value + '"'
  }
  return $Value
}

$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$excel.DisplayAlerts = $false
try { $excel.AutomationSecurity = 3 } catch {}
$metadata = [ordered]@{
  workbook_file_name = [System.IO.Path]::GetFileName($WorkbookPath)
  excel_version = [string]$excel.Version
  opened_read_only = $true
  macros_disabled = $true
  links = @()
  names = @()
  sheets = @()
}

try {
  $wb = $excel.Workbooks.Open($WorkbookPath, 0, $true)
  try {
    $ls = $wb.LinkSources(1)
    if ($ls) {
      foreach ($l in $ls) { $metadata.links += [string]$l }
    }
  } catch {}
  try {
    foreach ($n in $wb.Names) {
      $metadata.names += [ordered]@{ name = [string]$n.Name; refers_to = [string]$n.RefersTo }
    }
  } catch {}

  $sheetIndex = 0
  foreach ($ws in $wb.Worksheets) {
    $sheetIndex += 1
    $used = $ws.UsedRange
    $rowCount = [int]$used.Rows.Count
    $colCount = [int]$used.Columns.Count
    $safeSheet = ([string]$ws.Name) -replace '[\\/:*?"<>|]', '_'
    $csvName = ('{0:D3}_{1}.csv' -f $sheetIndex, $safeSheet)
    $csvPath = Join-Path $OutputDir $csvName
    $utf8 = New-Object System.Text.UTF8Encoding($true)
    $writer = New-Object System.IO.StreamWriter($csvPath, $false, $utf8)
    $formulas = @()
    $nonEmptyRows = 0
    try {
      for ($r = 1; $r -le $rowCount; $r++) {
        $cells = @()
        $rowHasValue = $false
        for ($c = 1; $c -le $colCount; $c++) {
          $cell = $used.Cells.Item($r, $c)
          $text = [string]$cell.Text
          if (-not [string]::IsNullOrWhiteSpace($text)) { $rowHasValue = $true }
          $cells += (Escape-CsvCell $text)
          $formula = [string]$cell.Formula
          if ($formula.StartsWith('=')) {
            $formulas += [ordered]@{
              row = $r
              column = $c
              address = [string]$cell.Address($false, $false)
              formula = $formula
              text = $text
            }
          }
        }
        if ($rowHasValue) { $nonEmptyRows += 1 }
        $writer.WriteLine(($cells -join ','))
      }
    } finally {
      $writer.Close()
    }
    $metadata.sheets += [ordered]@{
      index = $sheetIndex
      name = [string]$ws.Name
      visible_code = [int]$ws.Visible
      visible = ([int]$ws.Visible -eq -1)
      used_rows = $rowCount
      used_columns = $colCount
      non_empty_rows = $nonEmptyRows
      formula_count = $formulas.Count
      formulas = $formulas
      csv_file_name = $csvName
    }
  }
  $wb.Close($false)
} finally {
  $excel.Quit()
  [System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null
}
$metadata | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $OutputDir 'metadata.json') -Encoding UTF8
