/*
 * Smoke test de enlace C/C++: verifica que deauth_json.c (compilado como C) enlaza
 * desde una unidad C++ gracias a las guardas extern "C" del header. Ejercita el
 * serializador con un vector valido y confirma el contrato de retorno. Compila como
 * C++ (g++) y enlaza con el objeto C.
 */
#include "deauth_json.h"
#include <cstdio>
#include <cstring>

int main()
{
    deauth_event_t ev;
    char out[DEAUTH_JSON_BUFFER_SIZE];
    int n;

    for (int i = 0; i < 6; ++i) {
        ev.src[i] = 0xAA; ev.dst[i] = 0xBB; ev.bssid[i] = 0xCC;
    }
    ev.channel = 6;
    ev.subtype = 12;

    n = deauth_json_serialize(&ev, "ESP32_2_CH_06", out, sizeof(out));
    if (n <= 0 || (size_t)n >= sizeof(out) || std::strlen(out) != (size_t)n) {
        std::printf("FAIL: serializacion desde C++ (n=%d)\n", n);
        return 1;
    }
    if (out[0] != '{' || out[n - 1] != '}' ||
        std::strstr(out, "\"e\":12") == NULL ||
        std::strstr(out, "\"n\":\"ESP32_2_CH_06\"") == NULL) {
        std::printf("FAIL: contenido inesperado desde C++: %s\n", out);
        return 1;
    }

    std::printf("OK: enlace C/C++ (extern \"C\") verificado\n");
    return 0;
}
