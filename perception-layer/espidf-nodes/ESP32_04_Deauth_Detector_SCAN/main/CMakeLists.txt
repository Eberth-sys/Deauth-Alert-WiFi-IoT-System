#perception-layer\espidf-nodes\ESP32_04_Deauth_Detector_SCAN\main\CMakeLists.txt
# (F6a-1) Instrumentacion diagnostica: variable CACHEADA, por defecto 0 (firmware normal).
# Se activa con: idf.py -DDEAUTH_DIAG=1 build. NO se sobrescribe CMAKE_C_FLAGS.
set(DEAUTH_DIAG "0" CACHE STRING "Instrumentacion diagnostica F6a (0=off, 1=on)")
set_property(CACHE DEAUTH_DIAG PROPERTY STRINGS "0" "1")
if(NOT DEAUTH_DIAG STREQUAL "0" AND NOT DEAUTH_DIAG STREQUAL "1")
    message(FATAL_ERROR "DEAUTH_DIAG debe ser 0 o 1 (recibido: '${DEAUTH_DIAG}')")
endif()

idf_component_register(SRCS "main.c"
                    INCLUDE_DIRS "."
                    REQUIRES bt esp_wifi nvs_flash WifiMgmtParser DeauthEvent DeauthJson)

target_include_directories(${COMPONENT_LIB} PRIVATE
    "${IDF_PATH}/components/bt/include/esp32/include"
    "${IDF_PATH}/components/bt/host/bluedroid/api/include/api"
)

# (F6a-1) El macro llega SOLO al componente main; las bibliotecas compartidas no lo necesitan
# (deauth_diag.c es un helper portable que compila igual con o sin diagnostico).
target_compile_definitions(${COMPONENT_LIB} PRIVATE DEAUTH_DIAG=${DEAUTH_DIAG})
