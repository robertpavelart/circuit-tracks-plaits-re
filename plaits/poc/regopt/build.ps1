param([string]$BuildDir='builds/phase20a-regopt/core-build')
$ErrorActionPreference='Stop'
$taskRoot=(Resolve-Path 'plaits/poc/regopt/../../..').Path
$taskBuild=[IO.Path]::GetFullPath((Join-Path $taskRoot $BuildDir))
$taskAllowed=[IO.Path]::GetFullPath((Join-Path $taskRoot 'builds/phase20a-regopt'))
if (-not $taskBuild.StartsWith($taskAllowed+[IO.Path]::DirectorySeparatorChar) -or (Test-Path -LiteralPath $taskBuild)) { throw 'Fresh Phase20A build directory required' }
$vsRoot='C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools'
$sdkRoot='C:\Program Files (x86)\Windows Kits\10'
$sdkVersion='10.0.26100.0'
$vcRoot=Join-Path $vsRoot 'VC\Tools\MSVC\14.44.35207'
$cmakeExe=Join-Path $vsRoot 'Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe'
$ninjaExe=Join-Path $vsRoot 'Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe'
$env:PATH="$sdkRoot\bin\$sdkVersion\x64;$vcRoot\bin\Hostx64\x64;"+$env:PATH
$env:LIB="$sdkRoot\Lib\$sdkVersion\um\x64;$sdkRoot\Lib\$sdkVersion\ucrt\x64;$vcRoot\lib\x64"
$env:INCLUDE="$vcRoot\include;$sdkRoot\Include\$sdkVersion\ucrt;$sdkRoot\Include\$sdkVersion\shared;$sdkRoot\Include\$sdkVersion\um"
& $cmakeExe -S plaits/poc/regopt -B $taskBuild -G Ninja "-DCMAKE_MAKE_PROGRAM=$ninjaExe" -DCMAKE_BUILD_TYPE=Debug
if ($LASTEXITCODE -ne 0) {throw 'Configure failed'}
& $cmakeExe --build $taskBuild -j 2
if ($LASTEXITCODE -ne 0) {throw 'Build failed'}
