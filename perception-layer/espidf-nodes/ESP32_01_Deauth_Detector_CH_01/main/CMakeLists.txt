#perception-layer\espidf-nodes\ESP32_01_Deauth_Detector_CH_01\main\CMakeLists.txt

idf_component_register(SRCS "main.c"
                    INCLUDE_DIRS "."
                    REQUIRES bt esp_wifi nvs_flash WifiMgmtParser DeauthEvent DeauthJson)

target_include_directories(${COMPONENT_LIB} PRIVATE
    "${IDF_PATH}/components/bt/include/esp32/include"
    "${IDF_PATH}/components/bt/host/bluedroid/api/include/api"
)
