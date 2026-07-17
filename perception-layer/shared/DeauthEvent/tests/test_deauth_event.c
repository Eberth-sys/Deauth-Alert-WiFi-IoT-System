/*
 * Unit tests de host para DeauthEvent (F4c-1): tamano del POD + parser de BSSID.
 * Sin framework; datos sinteticos. Compila como C con ASAN/UBSAN. Sale con codigo
 * != 0 si algun check falla. (El contador de descartes vive en F4c-2 con seccion
 * critica FreeRTOS, no aqui.)
 */
#include "deauth_event.h"
#include <stdio.h>
#include <string.h>

static int g_checks = 0;
static int g_failures = 0;

#define CHECK(cond, msg)                                             \
    do {                                                            \
        g_checks++;                                                 \
        if (!(cond)) {                                              \
            g_failures++;                                           \
            printf("  FAIL (linea %d): %s\n", __LINE__, (msg));     \
        }                                                          \
    } while (0)

static int all_zero(const uint8_t *b, size_t n)
{
    size_t i;
    for (i = 0; i < n; ++i) {
        if (b[i] != 0) return 0;
    }
    return 1;
}

static void test_bssid_valid(void)
{
    uint8_t out[6];
    const uint8_t exp[6] = { 0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF };

    /* mayusculas */
    memset(out, 0xA5, sizeof(out));
    CHECK(deauth_parse_bssid("AA:BB:CC:DD:EE:FF", out) == 1, "BSSID upper: ok");
    CHECK(memcmp(out, exp, 6) == 0, "BSSID upper: bytes correctos");

    /* minusculas -> mismo valor */
    memset(out, 0xA5, sizeof(out));
    CHECK(deauth_parse_bssid("aa:bb:cc:dd:ee:ff", out) == 1, "BSSID lower: ok");
    CHECK(memcmp(out, exp, 6) == 0, "BSSID lower: bytes correctos");

    /* mixto + valores variados */
    {
        const uint8_t exp2[6] = { 0x01, 0x23, 0x45, 0x67, 0x89, 0xAB };
        memset(out, 0xA5, sizeof(out));
        CHECK(deauth_parse_bssid("01:23:45:67:89:aB", out) == 1, "BSSID mixto: ok");
        CHECK(memcmp(out, exp2, 6) == 0, "BSSID mixto: bytes correctos");
    }
}

/* Cada caso de error: prefill 0xA5 -> debe fallar y dejar out COMPLETO en cero. */
static void test_bssid_errors(void)
{
    uint8_t out[6];

    memset(out, 0xA5, sizeof(out));
    CHECK(deauth_parse_bssid("AA:BB:CC:DD:EE:F", out) == 0, "corto (16): falla");
    CHECK(all_zero(out, 6), "corto: out en cero");

    memset(out, 0xA5, sizeof(out));
    CHECK(deauth_parse_bssid("AA:BB:CC:DD:EE:FF:00", out) == 0, "largo (20): falla");
    CHECK(all_zero(out, 6), "largo: out en cero");

    memset(out, 0xA5, sizeof(out));
    CHECK(deauth_parse_bssid("", out) == 0, "vacio: falla");
    CHECK(all_zero(out, 6), "vacio: out en cero");

    memset(out, 0xA5, sizeof(out));
    CHECK(deauth_parse_bssid("AA-BB:CC:DD:EE:FF", out) == 0, "separador '-': falla");
    CHECK(all_zero(out, 6), "separador: out en cero");

    memset(out, 0xA5, sizeof(out));
    CHECK(deauth_parse_bssid("AA:BB:CC:DD:EE:FG", out) == 0, "hex invalido 'G': falla");
    CHECK(all_zero(out, 6), "hex invalido: out en cero");

    memset(out, 0xA5, sizeof(out));
    CHECK(deauth_parse_bssid(":A:BB:CC:DD:EE:FF", out) == 0, "hex en posicion de ':' : falla");
    CHECK(all_zero(out, 6), "hex en ':' : out en cero");

    memset(out, 0xA5, sizeof(out));
    CHECK(deauth_parse_bssid(NULL, out) == 0, "str NULL: falla");
    CHECK(all_zero(out, 6), "str NULL: out en cero");

    /* out NULL: no debe crashear */
    CHECK(deauth_parse_bssid("AA:BB:CC:DD:EE:FF", NULL) == 0, "out NULL: falla sin crash");
}

int main(void)
{
    CHECK(sizeof(deauth_event_t) == 20, "sizeof(deauth_event_t) == 20");

    test_bssid_valid();
    test_bssid_errors();

    printf("%d checks, %d fallos\n", g_checks, g_failures);
    return g_failures == 0 ? 0 : 1;
}
