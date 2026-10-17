$ErrorActionPreference='Stop'
$vsRoot='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
$sdkRoot='C:\Program Files (x86)\Windows Kits\10'
$sdkVersion='10.0.26100.0'
$vcRoot=Join-Path $vsRoot 'VC\Tools\MSVC\14.44.35207'
$cmakeExe=Join-Path $vsRoot 'Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe'
$ninjaExe=Join-Path $vsRoot 'Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe'
$env:PATH="$sdkRoot\bin\$sdkVersion\x64;$vcRoot\bin\Hostx64\x64;"+$env:PATH
$env:LIB="$sdkRoot\Lib\$sdkVersion\um\x64;$sdkRoot\Lib\$sdkVersion\ucrt\x64;$vcRoot\lib\x64"
$env:INCLUDE="$vcRoot\include;$sdkRoot\Include\$sdkVersion\ucrt;$sdkRoot\Include\$sdkVersion\shared;$sdkRoot\Include\$sdkVersion\um"
$taskRoot=(Get-Location).Path
$taskBuild=Join-Path $taskRoot 'builds/phase20e-full-plaits-audit/host-direct'
New-Item -ItemType Directory -Path $taskBuild -Force | Out-Null
$taskSources=@((Join-Path $taskRoot 'plaits/poc/full_audit/probe.cpp'))
$taskSources+=@(Get-ChildItem -LiteralPath (Join-Path $taskRoot 'plaits/upstream/plaits/dsp') -Filter '*.cc' -Recurse | Where-Object Name -ne 'voice.cc' | ForEach-Object FullName)
$taskSources+=@(Join-Path $taskRoot 'builds/phase20e-full-plaits-audit/host-overlay/plaits/resources.cc')
$taskSources+=@('stmlib/dsp/units.cc','stmlib/utils/random.cc') | ForEach-Object { Join-Path $taskRoot ('plaits/upstream/'+$_) }
Push-Location $taskBuild
try {
 & (Join-Path $vcRoot 'bin/Hostx64/x64/cl.exe') /nologo /EHsc /std:c++17 /O2 /fp:strict /MD /DTEST ('/FI'+(Join-Path $taskRoot 'plaits/poc/full_audit/host_compat.h')) ('/I'+(Join-Path $taskRoot 'builds/phase20e-full-plaits-audit/host-overlay')) ('/I'+(Join-Path $taskRoot 'plaits/upstream')) /Fe:plaits_probe.exe $taskSources
 if ($LASTEXITCODE -ne 0) {throw 'Build failed'}
} finally {Pop-Location}
