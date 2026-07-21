# Componente ESP-IDF de la biblioteca compartida DeauthEvent (F4c-1): modelo de evento
# POD (20 B) y parser de BSSID. Se consume via EXTRA_COMPONENT_DIRS + REQUIRES;
# Arduino/PlatformIO lo consumen como biblioteca. No usa FreeRTOS, atomicos ni hardware.
# La cola/worker y los contadores con seccion critica portMUX viven en cada variante de firmware
# desde F4c-2 (ya implementado), no en esta biblioteca.
# Incluye ademas el rate-limit compartido (deauth_ratelimit, F5-3) y el helper portable de
# instrumentacion diagnostica (deauth_diag, F6a-1); ninguno usa FreeRTOS.
idf_component_register(SRCS "src/deauth_event.c" "src/deauth_ratelimit.c" "src/deauth_diag.c"
                       INCLUDE_DIRS "src")
