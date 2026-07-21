# Componente ESP-IDF de la biblioteca compartida DeauthEvent (F4c-1): modelo de evento
# POD (20 B) y parser de BSSID. Se consume via EXTRA_COMPONENT_DIRS + REQUIRES;
# Arduino/PlatformIO lo consumen como biblioteca. No usa FreeRTOS, atomicos ni hardware.
# La cola/worker y los contadores con seccion critica portMUX viven en cada variante de firmware
# desde F4c-2 (ya implementado), no en esta biblioteca.
# Incluye ademas el rate-limit compartido (deauth_ratelimit, F5-3) y el helper portable de
# instrumentacion diagnostica (deauth_diag, F6a-1); ninguno usa FreeRTOS.
# (F6a-1 fix) DEAUTH_DIAG tambien debe llegar a ESTA biblioteca: deauth_diag.c compila su
# cuerpo solo con el flag activo, de modo que con 0 no quedan simbolos ni literales.
set(DEAUTH_DIAG "0" CACHE STRING "Instrumentacion diagnostica F6a (0=off, 1=on)")
set_property(CACHE DEAUTH_DIAG PROPERTY STRINGS "0" "1")
if(NOT DEAUTH_DIAG STREQUAL "0" AND NOT DEAUTH_DIAG STREQUAL "1")
    message(FATAL_ERROR "DEAUTH_DIAG debe ser 0 o 1 (recibido: '${DEAUTH_DIAG}')")
endif()

idf_component_register(SRCS "src/deauth_event.c" "src/deauth_ratelimit.c" "src/deauth_diag.c"
                       INCLUDE_DIRS "src")

target_compile_definitions(${COMPONENT_LIB} PRIVATE DEAUTH_DIAG=${DEAUTH_DIAG})
