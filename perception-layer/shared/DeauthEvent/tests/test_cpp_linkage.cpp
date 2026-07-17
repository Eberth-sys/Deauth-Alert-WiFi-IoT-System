/*
 * Smoke test de enlace C/C++: verifica que deauth_event.c (compilado como C) enlaza
 * desde una unidad C++ gracias a las guardas extern "C" del header. Ejercita el POD
 * (tamano 20) y el parser de BSSID. Compila como C++ (g++) y enlaza con el objeto C.
 */
#include "deauth_event.h"
#include <cstdio>
#include <cstring>

int main()
{
    if (sizeof(deauth_event_t) != 20) {
        std::printf("FAIL: sizeof(deauth_event_t) != 20\n");
        return 1;
    }

    uint8_t out[6];
    const uint8_t exp[6] = { 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF };
    if (deauth_parse_bssid("AA:BB:CC:DD:EE:FF", out) != 1 || std::memcmp(out, exp, 6) != 0) {
        std::printf("FAIL: deauth_parse_bssid desde C++\n");
        return 1;
    }

    std::printf("OK: enlace C/C++ (extern \"C\") verificado\n");
    return 0;
}
