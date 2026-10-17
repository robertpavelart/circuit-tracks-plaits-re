cmake_minimum_required(VERSION 3.15)
project(plaits_source_audit LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
get_filename_component(ROOT "${CMAKE_CURRENT_LIST_DIR}/../../.." ABSOLUTE)
file(GLOB_RECURSE DSP "${ROOT}/plaits/upstream/plaits/dsp/*.cc")
list(FILTER DSP EXCLUDE REGEX "/voice.cc$")
add_executable(plaits_probe probe.cpp ${DSP}
 "${ROOT}/builds/phase20e-full-plaits-audit/host-overlay/plaits/resources.cc"
 "${ROOT}/plaits/upstream/stmlib/dsp/units.cc"
 "${ROOT}/plaits/upstream/stmlib/utils/random.cc")
target_include_directories(plaits_probe PRIVATE "${ROOT}/builds/phase20e-full-plaits-audit/host-overlay" "${ROOT}/plaits/upstream")
target_compile_definitions(plaits_probe PRIVATE TEST)
if(MSVC)
 target_compile_options(plaits_probe PRIVATE /O2 /fp:strict "/FI${CMAKE_CURRENT_LIST_DIR}/host_compat.h")
endif()
