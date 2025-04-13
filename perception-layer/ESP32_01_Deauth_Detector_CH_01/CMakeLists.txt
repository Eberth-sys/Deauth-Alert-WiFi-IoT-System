#perception-layer\ESP32_01_Deauth_Detector_CH_01\CMakeLists.txt

# For more information about build system see
# https://docs.espressif.com/projects/esp-idf/en/latest/api-guides/build-system.html
# The following five lines of boilerplate have to be in your project's
# CMakeLists in this exact order for cmake to work correctly
cmake_minimum_required(VERSION 3.16)

# Referencia centralizada a partitions.csv en perception-layer
set(PARTITION_TABLE_CSV "${CMAKE_SOURCE_DIR}/../partitions.csv") #localiza el archivo de particion.

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(ESP32_01_Deauth_Detector_CH_01)

