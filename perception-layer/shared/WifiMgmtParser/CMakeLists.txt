# Componente ESP-IDF de la biblioteca compartida WifiMgmtParser (parser portable de
# tramas 802.11 management). Cada nodo ESP-IDF lo referencia via EXTRA_COMPONENT_DIRS
# (en su CMakeLists.txt de nivel superior) y lo declara en REQUIRES. Arduino/PlatformIO
# consumen el mismo `src/` como biblioteca. No accede a hardware.
idf_component_register(SRCS "src/wifi_mgmt_parser.c"
                       INCLUDE_DIRS "src")
