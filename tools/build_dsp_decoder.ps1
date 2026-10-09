param([string]$Rustc = 'rustc')
$ErrorActionPreference = 'Stop'
$project = Split-Path $PSScriptRoot -Parent
$vendor = Join-Path $project 'builds/vendor/dsp56300-rust'
$output = Join-Path $project 'builds/dsp-tools'
if (Test-Path -LiteralPath $output) { throw 'Decoder build directory already exists' }
$revision = & git -C $vendor rev-parse HEAD
if ($LASTEXITCODE -ne 0 -or $revision -ne 'c60aeedb6a6014850204c71e53bc0cf5b3104222') { throw 'Unexpected source revision' }
& git -C $vendor diff --quiet
if ($LASTEXITCODE -ne 0) { throw 'Decoder source has tracked modifications' }
New-Item -ItemType Directory -Path $output | Out-Null
function Compile([string[]]$arguments) {
    & $Rustc @arguments
    if ($LASTEXITCODE -ne 0) { throw "rustc failed ($LASTEXITCODE)" }
}
$core = Join-Path $output 'libdsp56300_core.rlib'
$disasm = Join-Path $output 'libdsp56300_disasm.rlib'
Compile @('--edition=2024','--crate-name','dsp56300_core','--crate-type','rlib',(Join-Path $vendor 'crates/core/src/lib.rs'),'-o',$core)
Compile @('--edition=2024','--crate-name','dsp56300_disasm','--crate-type','rlib',(Join-Path $vendor 'crates/disasm/src/lib.rs'),'--extern',"dsp56300_core=$core",'-L',$output,'-o',$disasm)
Compile @('--edition=2024',(Join-Path $PSScriptRoot 'dsp_disasm.rs'),'--extern',"dsp56300_disasm=$disasm",'-L',$output,'-o',(Join-Path $output 'dsp_disasm.exe'))
Compile @('--edition=2024','--test',(Join-Path $vendor 'crates/core/tests/decode.rs'),'--extern',"dsp56300_core=$core",'-L',$output,'-o',(Join-Path $output 'decode_tests.exe'))
Compile @('--edition=2024','--test',(Join-Path $vendor 'crates/disasm/tests/disasm.rs'),'--extern',"dsp56300_disasm=$disasm",'-L',$output,'-o',(Join-Path $output 'disasm_tests.exe'))
& (Join-Path $output 'decode_tests.exe') --quiet
if ($LASTEXITCODE -ne 0) { throw 'Upstream decoder tests failed' }
& (Join-Path $output 'disasm_tests.exe') --quiet
if ($LASTEXITCODE -ne 0) { throw 'Upstream disassembler tests failed' }
