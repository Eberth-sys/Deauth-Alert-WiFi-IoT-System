/*
 * Smoke test de enlace C/C++: verifica que deauth_event.c, deauth_ratelimit.c y
 * deauth_diag.c (compilados como C) enlazan desde una unidad C++ gracias a las
 * guardas extern "C" de sus headers. Ejercita el POD (tamano 20), el parser de
 * BSSID, la API del rate-limit F5-3 (init + check: ALLOW inicial y SUPPRESS en
 * ventana) y la API diagnostica F6a-1 (init + observadores + acumulacion + format).
 * Compila como C++ (g++) y enlaza con los objetos C.
 */
#include "deauth_event.h"
#include "deauth_ratelimit.h"
#include "deauth_diag.h"
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

    // Instrumentacion diagnostica (F6a-1) invocada desde C++: init + observadores
    // + acumulacion + serializacion de la linea [DIAG].
    deauth_diag_state_t diag;
    deauth_diag_init(&diag);
    deauth_diag_observe_stack_free(&diag, 2048);
    deauth_diag_observe_heap_free(&diag, 98765);
    deauth_diag_observe_queue_depth(&diag, 7);
    deauth_diag_set_mtu(&diag, 247);
    deauth_diag_delta_t delta;
    delta.dropped_events = 0;
    delta.dropped_mtu = 0;
    delta.rate_limited_suppressed = 12;
    delta.rate_limit_fail_open = 0;
    deauth_diag_accumulate(&diag, &delta);
    if (diag.total_rate_limited_suppressed != 12u) {
        std::printf("FAIL: deauth_diag_accumulate desde C++\n");
        return 1;
    }
    char diag_line[DEAUTH_DIAG_BUFFER_SIZE];
    const int dn = deauth_diag_format(&diag, &delta, "ESP32_1_CH_01", 123456u,
                                      diag_line, sizeof(diag_line));
    if (dn <= 0 || static_cast<size_t>(dn) >= sizeof(diag_line) ||
        std::strncmp(diag_line, "[DIAG] {\"diag_v\":1,", 19) != 0) {
        std::printf("FAIL: deauth_diag_format desde C++\n");
        return 1;
    }

    std::printf("OK: enlace C/C++ (extern \"C\") verificado (deauth_event + deauth_ratelimit + deauth_diag)\n");
    return 0;
}
