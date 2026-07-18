# Componente ESP-IDF de la biblioteca compartida DeauthJson (F5-1): serializador del
# contrato de eventos v1 (DEC-0003) por snprintf, sin librerias JSON ni heap. Consume
# deauth_event_t de DeauthEvent (SOLO el header). Se integra en el firmware via
# EXTRA_COMPONENT_DIRS + REQUIRES (F5-2); Arduino/PlatformIO lo consumen como biblioteca.
# No usa FreeRTOS, atomicos ni hardware; verificable en host (unit, ASAN/UBSAN, enlace
# C/C++, fuzz y contrato C->Python contra el parser real de la RPi).
idf_component_register(SRCS "src/deauth_json.c"
                       INCLUDE_DIRS "src"
                       REQUIRES DeauthEvent)
