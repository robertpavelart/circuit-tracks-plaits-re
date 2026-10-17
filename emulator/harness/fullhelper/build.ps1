param([string]$BuildDir = 'builds/phase19c-fullhelper/core-build')
$ErrorActionPreference = 'Stop'
$vsRoot = 'C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
$sdkRoot = 'C:\Program Files (x86)\Windows Kits\10'
$sdkVersion = '10.0.26100.0'
$vcRoot = Join-Path $vsRoot 'VC\Tools\MSVC\14.44.35207'
$cmakeExe = Join-Path $vsRoot 'Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe'
$ninjaExe = Join-Path $vsRoot 'Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe'
$env:PATH = "$sdkRoot\bin\$sdkVersion\x64;$vcRoot\bin\Hostx64\x64;" + $env:PATH
$env:LIB = "$sdkRoot\Lib\$sdkVersion\um\x64;$sdkRoot\Lib\$sdkVersion\ucrt\x64;$vcRoot\lib\x64"
$env:INCLUDE = "$vcRoot\include;$sdkRoot\Include\$sdkVersion\ucrt;$sdkRoot\Include\$sdkVersion\shared;$sdkRoot\Include\$sdkVersion\um"
& $cmakeExe -S emulator/harness/fullhelper -B $BuildDir -G Ninja "-DCMAKE_MAKE_PROGRAM=$ninjaExe" -DCMAKE_BUILD_TYPE=Debug
if ($LASTEXITCODE -ne 0) { throw 'Configure failed' }
& $cmakeExe --build $BuildDir --target ct_fullhelper -j 4
if ($LASTEXITCODE -ne 0) { throw 'Build failed' }

