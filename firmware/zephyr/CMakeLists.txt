cmake_minimum_required(VERSION 3.20.0)
find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(civixrecord_ble_edge_firmware)

target_sources(app PRIVATE
    src/main.c
    src/ble_audio_service.c
    src/optical_glasses_service.c
    src/pen_digitizer_service.c
)

target_include_directories(app PRIVATE include)
