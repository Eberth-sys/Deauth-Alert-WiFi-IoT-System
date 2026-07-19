/*
 * Smoke test de enlace C/C++: verifica que deauth_event.c y deauth_ratelimit.c
 * (compilados como C) enlazan desde una unidad C++ gracias a las guardas extern "C"
 * de sus headers. Ejercita el POD (tamano 20), el parser de BSSID y la API del
 * rate-limit F5-3 (init + check: ALLOW inicial y SUPPRESS dentro de la ventana).
 * Compila como C++ (g++) y enlaza con los objetos C.
 */
#include "deauth_event.h"
#include "deauth_ratelimit.h"
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

    // Rate-limit (F5-3) invocado desde C++: init + ALLOW inicial + SUPPRESS en ventana.
    deauth_rate_limiter_t rl;
    deauth_ratelimit_init(&rl);
    const uint8_t dst[6] = { 0x11, 0x22, 0x33, 0x44, 0x55, 0x66 };
    if (deauth_ratelimit_check(&rl, dst, 12, 100, 1000) != DEAUTH_RL_ALLOW) {
        std::printf("FAIL: deauth_ratelimit_check ALLOW inicial desde C++\n");
        return 1;
    }
    if (deauth_ratelimit_check(&rl, dst, 12, 500, 1000) != DEAUTH_RL_SUPPRESS) {
        std::printf("FAIL: deauth_ratelimit_check SUPPRESS en ventana desde C++\n");
        return 1;
    }

    std::printf("OK: enlace C/C++ (extern \"C\") verificado (deauth_event + deauth_ratelimit)\n");
    return 0;
}
