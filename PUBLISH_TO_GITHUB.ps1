$ErrorActionPreference = 'Stop'

$RepoUrl = 'https://github.com/robertpavelart/circuit-tracks-plaits-re.git'
$SourceRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$TempRoot = Join-Path $env:TEMP ("circuit-tracks-plaits-re-publish-" + [guid]::NewGuid().ToString('N'))

Write-Host "Publishing reviewed source snapshot to:" $RepoUrl
Write-Host "Temporary clone:" $TempRoot

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git is not installed or not available in PATH.'
}

& git clone $RepoUrl $TempRoot
if ($LASTEXITCODE -ne 0) { throw 'git clone failed' }

# Replace the working tree while preserving the clone's .git directory/history.
Get-ChildItem -LiteralPath $TempRoot -Force |
    Where-Object { $_.Name -ne '.git' } |
    Remove-Item -Recurse -Force

$null = & robocopy $SourceRoot $TempRoot /E /XD '.git' /NFL /NDL /NJH /NJS /NP
if ($LASTEXITCODE -gt 7) { throw "robocopy failed with code $LASTEXITCODE" }

Push-Location $TempRoot
try {
    & git add -A
    if ($LASTEXITCODE -ne 0) { throw 'git add failed' }

    & git diff --cached --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host 'No changes to publish.'
        exit 0
    }

    & git commit -m 'source: import reviewed project code, tests, and research notes'
    if ($LASTEXITCODE -ne 0) { throw 'git commit failed' }

    & git push origin main
    if ($LASTEXITCODE -ne 0) { throw 'git push failed' }

    Write-Host ''
    Write-Host 'DONE: source snapshot pushed to GitHub.' -ForegroundColor Green
    Write-Host 'https://github.com/robertpavelart/circuit-tracks-plaits-re'
}
finally {
    Pop-Location
}
