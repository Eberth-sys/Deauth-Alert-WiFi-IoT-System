# Componente ESP-IDF de la biblioteca compartida DeauthEvent (F4c-1): modelo de evento
# POD (20 B) y parser de BSSID. Se consume via EXTRA_COMPONENT_DIRS + REQUIRES;
# Arduino/PlatformIO lo consumen como biblioteca. No usa FreeRTOS, atomicos ni hardware.
# La cola/worker y el contador de descartes (seccion critica portMUX) se agregan en F4c-2.
idf_component_register(SRCS "src/deauth_event.c"
                       INCLUDE_DIRS "src")
