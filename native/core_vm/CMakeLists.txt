cmake_minimum_required(VERSION 3.22)
project(civixrecord_core_engine VERSION 0.4.1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Compiler optimization flags
if(MSVC)
    add_compile_options(/O2 /arch:AVX2 /W4 /permissive-)
else()
    add_compile_options(-O3 -march=native -Wall -Wextra -Wpedantic -pthread)
endif()

include_directories(include)

file(GLOB_RECURSE CORE_SOURCES
    "src/*.cpp"
)

add_library(civix_core_lib STATIC ${CORE_SOURCES})

add_executable(civix_kernel_daemon src/main.cpp)
target_link_libraries(civix_kernel_daemon PRIVATE civix_core_lib)

if(WIN32)
    target_link_libraries(civix_kernel_daemon PRIVATE ws2_32)
    target_link_libraries(civix_core_lib PRIVATE ws2_32)
endif()

if(UNIX AND NOT APPLE)
    target_link_libraries(civix_kernel_daemon PRIVATE pthread rt)
endif()
