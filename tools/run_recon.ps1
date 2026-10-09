param(
    [Parameter(Mandatory=$true)][string]$Python,
    [Parameter(Mandatory=$true)][string]$OutputDirectory
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$reportRoot = [System.IO.Path]::GetFullPath($OutputDirectory)
$protectedRoot = [System.IO.Path]::GetFullPath((Join-Path $projectRoot 'original'))
if ($reportRoot -eq $protectedRoot -or $reportRoot.StartsWith($protectedRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase)) { throw 'Protected original/ directory' }
if (Test-Path -LiteralPath $reportRoot) { throw 'Output directory exists; choose a new directory' }
New-Item -ItemType Directory -Path $reportRoot | Out-Null
function Invoke-Static([string]$scriptName, [string[]]$scriptArguments) {
    & $Python -B (Join-Path $PSScriptRoot $scriptName) @scriptArguments
    if ($LASTEXITCODE -ne 0) { throw "$scriptName failed ($LASTEXITCODE)" }
}
Invoke-Static 'ct_static.py' @('baseline','--output',(Join-Path $reportRoot 'baseline.json'))
Invoke-Static 'ct_static.py' @('survey','--output',(Join-Path $reportRoot 'survey.json'))
foreach ($item in @(@('uploading','0x0801F5F0'),@('uploaded','0x0801F608'),@('upload-wrapper','0x0801F554'))) {
    Invoke-Static 'ct_static.py' @('xrefs','--target',$item[1],'--output',(Join-Path $reportRoot ('xrefs-'+$item[0]+'.json')))
}
Invoke-Static 'ct_evidence.py' @('--output',(Join-Path $reportRoot 'evidence.json'))
$ranges = @(
    @('upload','0x0801F51E','0x0801F5C6'),
    @('dsp-driver','0x08029190','0x08029710'),
    @('transport','0x0803B9D8','0x0803BAE8'),
    @('spi-driver','0x08037770','0x080379A0'),
    @('dma','0x0801C072','0x0801C142'),
    @('irq','0x080573D8','0x0805760C'),
    @('data-decoder','0x080596C4','0x0805973C')
)
foreach ($range in $ranges) {
    Invoke-Static 'ct_static.py' @('disasm','--start',$range[1],'--end',$range[2],'--output',(Join-Path $reportRoot ($range[0]+'.txt')))
}
Invoke-Static 'ct_data_decode.py' @('--output',(Join-Path $reportRoot 'initialized-data.bin'),'--report',(Join-Path $reportRoot 'initialized-data.json'))
Invoke-Static 'ct_dsp_extract.py' @('--output-dir',(Join-Path $reportRoot 'dsp'))
Write-Output "Offline evidence written to $reportRoot"
