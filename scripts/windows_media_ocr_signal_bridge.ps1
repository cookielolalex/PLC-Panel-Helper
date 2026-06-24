param(
  [Parameter(Mandatory = $true)]
  [string]$ImagePath,

  [string]$ProjectId = "",

  [string]$LanguageTag = "",

  [string]$RequestedClassifier = "windows_media_ocr_local_signal_bridge"
)

$ErrorActionPreference = "Stop"
$started = Get-Date

Add-Type -AssemblyName System.Runtime.WindowsRuntime
[void][Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType=WindowsRuntime]
[void][Windows.Globalization.Language, Windows.Foundation, ContentType=WindowsRuntime]
[void][Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime]
[void][Windows.Storage.Streams.IRandomAccessStreamWithContentType, Windows.Storage.Streams, ContentType=WindowsRuntime]
[void][Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType=WindowsRuntime]
[void][Windows.Graphics.Imaging.SoftwareBitmap, Windows.Graphics.Imaging, ContentType=WindowsRuntime]

function Await-Operation($AsyncOp, [Type]$ResultType) {
  $method = [System.WindowsRuntimeSystemExtensions].GetMethods() |
    Where-Object {
      $_.Name -eq "AsTask" -and
      $_.IsGenericMethodDefinition -and
      $_.GetGenericArguments().Length -eq 1 -and
      $_.GetParameters().Length -eq 1 -and
      $_.ReturnType.IsGenericType -and
      $_.ReturnType.GetGenericTypeDefinition().FullName -eq 'System.Threading.Tasks.Task`1'
    } |
    Select-Object -First 1
  if ($null -eq $method) {
    throw "AsTask generic IAsyncOperation overload not found"
  }
  $task = $method.MakeGenericMethod($ResultType).Invoke($null, @($AsyncOp))
  $task.Wait()
  return $task.Result
}

function Normalize-Role-Hits([string]$Text) {
  $upper = ($Text -replace "\s+", " ").ToUpperInvariant()
  $hits = New-Object System.Collections.Generic.List[string]
  if ($upper -match "PRODUCTION[ _-]*DRAWING|PRODUCTION|SEIKAN|CONTROL PANEL") {
    $hits.Add("PRODUCTION_DRAWING")
  }
  if ($upper -match "SHEET[ _-]*METAL|SHEETMETAL|SHEET METAL") {
    $hits.Add("SHEETMETAL_DRAWING")
  }
  if ($upper -match "PUNCH[ _-]*DRAWING|PUNCH|HOLE") {
    $hits.Add("PUNCH_DRAWING")
  }
  if ($upper -match "ELECTRICAL|WIRING|SCHEMATIC|SINGLE LINE") {
    $hits.Add("ELECTRICAL_DRAWING")
  }
  if ($upper -match "SOURCE[ _-]*DOCUMENT|CONTRACT|MATERIAL|QUOTATION") {
    $hits.Add("SOURCE_DOCUMENT")
  }
  return @($hits | Select-Object -Unique)
}

function Get-Identity-Status([string]$Text, [string]$ExpectedProjectId) {
  if ([string]::IsNullOrWhiteSpace($ExpectedProjectId)) {
    return "NOT_FOUND"
  }
  $ids = [regex]::Matches($Text, "\b\d{7}\b") | ForEach-Object { $_.Value } | Select-Object -Unique
  if ($ids -contains $ExpectedProjectId) {
    return "CONFIRMED"
  }
  if (@($ids).Count -gt 0) {
    return "CONFLICT"
  }
  return "NOT_FOUND"
}

try {
  $resolved = (Resolve-Path -LiteralPath $ImagePath).Path
  $languages = @([Windows.Media.Ocr.OcrEngine]::AvailableRecognizerLanguages | ForEach-Object { $_.LanguageTag })
  if ([string]::IsNullOrWhiteSpace($LanguageTag)) {
    $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromUserProfileLanguages()
  } else {
    $language = [Windows.Globalization.Language]::new($LanguageTag)
    $engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($language)
  }
  if ($null -eq $engine) {
    throw "No Windows.Media.Ocr engine available for requested language"
  }

  $file = Await-Operation ([Windows.Storage.StorageFile]::GetFileFromPathAsync($resolved)) ([Windows.Storage.StorageFile])
  $stream = Await-Operation ($file.OpenReadAsync()) ([Windows.Storage.Streams.IRandomAccessStreamWithContentType])
  $decoder = Await-Operation ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
  $bitmap = Await-Operation ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
  $result = Await-Operation ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])

  $text = [string]$result.Text
  $roleHits = Normalize-Role-Hits $text
  $identityStatus = Get-Identity-Status $text $ProjectId
  $elapsed = [int]((Get-Date) - $started).TotalMilliseconds

  [pscustomobject]@{
    status = "PASS"
    requested_classifier = $RequestedClassifier
    actual_classifier = "Windows.Media.Ocr.OcrEngine"
    host_process = "powershell.exe"
    installed_language_tags = $languages
    requested_language_tag = $LanguageTag
    actual_language_tag = $engine.RecognizerLanguage.LanguageTag
    role_hits = @($roleHits)
    project_identity_status = $identityStatus
    recognized_nonempty = ($text.Length -gt 0)
    elapsed_ms = $elapsed
    evidence_channel_codes = @("WIN_MEDIA_OCR_ROLE_SIGNAL", "WIN_MEDIA_OCR_IDENTITY_SIGNAL")
    minimization = @{
      raw_ocr_text_returned = $false
      raw_ocr_text_stdout = $false
      raw_ocr_text_stderr = $false
      raw_ocr_text_logged = $false
      image_path_returned = $false
    }
  } | ConvertTo-Json -Depth 6
} catch {
  $elapsed = [int]((Get-Date) - $started).TotalMilliseconds
  [pscustomobject]@{
    status = "FAIL"
    requested_classifier = $RequestedClassifier
    actual_classifier = "Windows.Media.Ocr.OcrEngine"
    host_process = "powershell.exe"
    installed_language_tags = @()
    requested_language_tag = $LanguageTag
    actual_language_tag = $null
    role_hits = @()
    project_identity_status = "NOT_FOUND"
    recognized_nonempty = $false
    elapsed_ms = $elapsed
    error_code = $_.Exception.GetType().Name
    evidence_channel_codes = @("WIN_MEDIA_OCR_FAILURE")
    minimization = @{
      raw_ocr_text_returned = $false
      raw_ocr_text_stdout = $false
      raw_ocr_text_stderr = $false
      raw_ocr_text_logged = $false
      image_path_returned = $false
    }
  } | ConvertTo-Json -Depth 6
  exit 1
}
