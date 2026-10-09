cmake_minimum_required(VERSION 3.15)
project(ct_stock_load_only LANGUAGES CXX)
# Reuse the sealed 19A source recipe without changing its files or manifests.
add_subdirectory("${CMAKE_CURRENT_LIST_DIR}/.." substrate)
add_executable(ct_stock_load main.cpp)
target_link_libraries(ct_stock_load PRIVATE replay_core bcrypt)
set_property(TARGET ct_stock_load PROPERTY CXX_STANDARD 17)
