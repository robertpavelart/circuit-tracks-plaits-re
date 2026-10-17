$ErrorActionPreference='Stop'
$taskRoot=(Get-Location).Path
$vcRoot='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.44.35207'
$sdkRoot='C:\Program Files (x86)\Windows Kits\10'
$sdkVersion='10.0.26100.0'
$env:PATH="$sdkRoot\bin\$sdkVersion\x64;$vcRoot\bin\Hostx64\x64;"+$env:PATH
$env:LIB="$sdkRoot\Lib\$sdkVersion\um\x64;$sdkRoot\Lib\$sdkVersion\ucrt\x64;$vcRoot\lib\x64"
$env:INCLUDE="$vcRoot\include;$sdkRoot\Include\$sdkVersion\ucrt;$sdkRoot\Include\$sdkVersion\shared;$sdkRoot\Include\$sdkVersion\um"
$taskBuild=Join-Path $taskRoot 'builds/phase20f-va-vpre-admission/host'
New-Item -ItemType Directory -Path $taskBuild -Force | Out-Null
Push-Location $taskBuild
try {
 & (Join-Path $vcRoot 'bin/Hostx64/x64/cl.exe') /nologo /EHsc /std:c++17 /MDd /O2 /Ob2 /DDSP56K_FORCE_INTERPRETER=1 /DDSP56300_DEBUGGER=0 ('/I'+(Join-Path $taskRoot 'emulator/upstream/dsp56300/source')) ('/I'+(Join-Path $taskRoot 'emulator/upstream/asmjit/src')) (Join-Path $taskRoot 'plaits/poc/va_vpre/admission.cpp') /Fe:admission.exe /link /INCREMENTAL:NO (Join-Path $taskRoot 'builds/phase19a/core-build/replay_core.lib') (Join-Path $taskRoot 'builds/phase19a/core-build/upstream/asmjit/asmjit.lib') bcrypt.lib
 if ($LASTEXITCODE -ne 0) {throw 'Build failed'}
}finally{Pop-Location}
