# Render the selected source without redrawing or annotating its geometry.
param([string]$Poppler = 'pdftoppm')
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$sourceDir = Join-Path $repoRoot 'HW3/sources/third_plan_candidates'
$pdf = Join-Path $sourceDir 'NIST_TN2351_2025.pdf'
# Printed page 9 is PDF page 17. Crop coordinates refer to the 1700-pixel render.
& $Poppler -f 17 -l 17 -singlefile -scale-to 1700 -png $pdf (Join-Path $sourceDir 'NIST_Page_09')
if ($LASTEXITCODE -ne 0) { throw 'Full-page rendering failed.' }
& $Poppler -f 17 -l 17 -singlefile -scale-to 1700 -x 370 -y 145 -W 580 -H 540 -png $pdf (Join-Path $sourceDir 'NIST_Figure_02_Plan')
if ($LASTEXITCODE -ne 0) { throw 'Figure rendering failed.' }
$manifestFiles = @('NIST_TN2351_2025.pdf', 'NIST_Page_09.png', 'NIST_Figure_02_Plan.png')
$hashRecords = foreach ($name in $manifestFiles) {
    $filePath = Join-Path $sourceDir $name
    [ordered]@{ file = $name; sha256 = (Get-FileHash -LiteralPath $filePath -Algorithm SHA256).Hash.ToLower(); bytes = (Get-Item -LiteralPath $filePath).Length }
}
$manifest = [ordered]@{
    source_url = 'https://nvlpubs.nist.gov/nistpubs/TechnicalNotes/NIST.TN.2351.pdf'
    doi = '10.6028/NIST.TN.2351'
    retrieved_date = '2026-11-10'
    printed_page = 9
    pdf_page_one_based = 17
    figure = 2
    status = 'source_selected_extraction_pending'
    render = [ordered]@{ scale_to_pixels = 1700; crop_xywh = @(370, 145, 580, 540); annotations_added = $false }
    files = @($hashRecords)
}
$json = $manifest | ConvertTo-Json -Depth 6
[System.IO.File]::WriteAllText((Join-Path $sourceDir 'NIST_Source_Manifest.json'), $json, (New-Object System.Text.UTF8Encoding($false)))
