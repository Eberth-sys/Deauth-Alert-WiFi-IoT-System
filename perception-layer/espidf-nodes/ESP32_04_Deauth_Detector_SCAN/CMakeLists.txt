#perception-layer\espidf-nodes\ESP32_04_Deauth_Detector_SCAN\CMakeLists.txt

# For more information about build system see
# https://docs.espressif.com/projects/esp-idf/en/latest/api-guides/build-system.html
# The following five lines of boilerplate have to be in your project's
# CMakeLists in this exact order for cmake to work correctly
cmake_minimum_required(VERSION 3.16)

# Referencia centralizada a partitions.csv en perception-layer
# La tabla de particiones se define en sdkconfig.defaults (CONFIG_PARTITION_TABLE_CUSTOM_FILENAME="../partitions.csv").

# Componente compartido WifiMgmtParser (F4b): declararlo ANTES de project.cmake.
set(EXTRA_COMPONENT_DIRS
    "${CMAKE_SOURCE_DIR}/../../shared/WifiMgmtParser"
    "${CMAKE_SOURCE_DIR}/../../shared/DeauthEvent"
    "${CMAKE_SOURCE_DIR}/../../shared/DeauthJson")

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(ESP32_04_Deauth_Detector_SCANNER)
