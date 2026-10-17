$ErrorActionPreference='Stop'
$taskRoot=(Get-Location).Path
$vcRoot='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207'
$sdkRoot='C:\Program Files (x86)\Windows Kits\10'
$sdkVersion='10.0.26100.0'
$env:PATH="$sdkRoot\bin\$sdkVersion\x64;$vcRoot\bin\Hostx64\x64;"+$env:PATH
$env:LIB="$sdkRoot\Lib\$sdkVersion\um\x64;$sdkRoot\Lib\$sdkVersion\ucrt\x64;$vcRoot\lib\x64"
$env:INCLUDE="$vcRoot\include;$sdkRoot\Include\$sdkVersion\ucrt;$sdkRoot\Include\$sdkVersion\shared;$sdkRoot\Include\$sdkVersion\um"
$taskBuild=Join-Path $taskRoot 'builds/phase20f-va-vpre-admission/host-oracle'
New-Item -ItemType Directory -Path $taskBuild -Force | Out-Null
$taskObjs=@(Get-ChildItem -LiteralPath (Join-Path $taskRoot 'builds/phase20e-full-plaits-audit/host-direct') -Filter '*.obj' | Where-Object Name -ne 'probe.obj' | ForEach-Object FullName)
Push-Location $taskBuild
try {
 & (Join-Path $vcRoot 'bin/Hostx64/x64/cl.exe') /nologo /EHsc /std:c++17 /MD /O2 /fp:strict /DTEST ('/FI'+(Join-Path $taskRoot 'plaits/poc/va_vpre/host_compat.h')) ('/I'+(Join-Path $taskRoot 'builds/phase20e-full-plaits-audit/host-overlay')) ('/I'+(Join-Path $taskRoot 'plaits/upstream')) (Join-Path $taskRoot 'plaits/poc/va_vpre/oracle.cpp') (Join-Path $taskRoot 'plaits/upstream/plaits/dsp/voice.cc') $taskObjs /Fe:va_oracle.exe
 if ($LASTEXITCODE -ne 0) {throw 'Oracle build failed'}
}finally{Pop-Location}
