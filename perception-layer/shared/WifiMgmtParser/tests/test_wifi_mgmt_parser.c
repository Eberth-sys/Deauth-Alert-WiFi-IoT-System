/*
 * Unit tests de host para wifi_mgmt_parse. Sin framework externo; datos sinteticos
 * (MACs artificiales, cero PII/red real). Compila como C con ASAN/UBSAN.
 * Sale con codigo != 0 si algun check falla.
 */
#include "wifi_mgmt_parser.h"
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

/* Trama de management minima (24 bytes): subtype en bits 4-7 del byte 0, type=0.
 * addr1/2/3 rellenas con patrones distintos para verificar offsets. */
static void build_frame(uint8_t *f, uint8_t subtype)
{
    size_t i;
    for (i = 0; i < 24; ++i) {
        f[i] = 0;
    }
    f[0] = (uint8_t)(subtype << 4);          /* type = 0 (mgmt), subtype en bits 4-7 */
    for (i = 0; i < 6; ++i) {
        f[4  + i] = (uint8_t)(0x10 + i);     /* addr1 */
        f[10 + i] = (uint8_t)(0x20 + i);     /* addr2 */
        f[16 + i] = (uint8_t)(0x30 + i);     /* addr3 */
    }
}

static int is_zero(const wifi_mgmt_frame_t *o)
{
    wifi_mgmt_frame_t z;
    memset(&z, 0, sizeof(z));
    return memcmp(o, &z, sizeof(z)) == 0;
}

int main(void)
{
    uint8_t frame[64];
    wifi_mgmt_frame_t out;
    wifi_mgmt_status_t st;
    const uint8_t exp_a1[6] = { 0x10, 0x11, 0x12, 0x13, 0x14, 0x15 };
    const uint8_t exp_a2[6] = { 0x20, 0x21, 0x22, 0x23, 0x24, 0x25 };
    const uint8_t exp_a3[6] = { 0x30, 0x31, 0x32, 0x33, 0x34, 0x35 };

    /* 1. deauth 0x0C valido -> OK y direcciones por offset */
    build_frame(frame, 0x0C);
    st = wifi_mgmt_parse(frame, 24, &out);
    CHECK(st == WIFI_MGMT_OK, "deauth: status OK");
    CHECK(out.frame_type == 0, "deauth: frame_type 0");
    CHECK(out.frame_subtype == 0x0C, "deauth: subtype 0x0C");
    CHECK(memcmp(out.addr1, exp_a1, 6) == 0, "deauth: addr1 = offset 4..9 (6 bytes)");
    CHECK(memcmp(out.addr2, exp_a2, 6) == 0, "deauth: addr2 = offset 10..15 (6 bytes)");
    CHECK(memcmp(out.addr3, exp_a3, 6) == 0, "deauth: addr3 = offset 16..21 (6 bytes)");

    /* 2. disassoc 0x0A reconocido (el parser no alerta; eso es del consumidor) */
    build_frame(frame, 0x0A);
    st = wifi_mgmt_parse(frame, 24, &out);
    CHECK(st == WIFI_MGMT_OK, "disassoc: status OK");
    CHECK(out.frame_subtype == 0x0A, "disassoc: subtype 0x0A");

    /* 3. otro mgmt (beacon 0x08) -> OK, subtype propagado */
    build_frame(frame, 0x08);
    st = wifi_mgmt_parse(frame, 24, &out);
    CHECK(st == WIFI_MGMT_OK, "beacon: status OK");
    CHECK(out.frame_subtype == 0x08, "beacon: subtype 0x08");

    /* 4. too short: 0/10/23 -> ERR_TOO_SHORT. Se prellena out con 0xA5 antes de CADA
     * llamada para probar que esa ruta lo deja completamente en cero, sin depender
     * del resultado del caso anterior. */
    build_frame(frame, 0x0C);
    memset(&out, 0xA5, sizeof(out));
    st = wifi_mgmt_parse(frame, 0, &out);
    CHECK(st == WIFI_MGMT_ERR_TOO_SHORT, "len 0: TOO_SHORT");
    CHECK(is_zero(&out), "len 0: out en cero");
    memset(&out, 0xA5, sizeof(out));
    st = wifi_mgmt_parse(frame, 10, &out);
    CHECK(st == WIFI_MGMT_ERR_TOO_SHORT, "len 10: TOO_SHORT");
    CHECK(is_zero(&out), "len 10: out en cero");
    memset(&out, 0xA5, sizeof(out));
    st = wifi_mgmt_parse(frame, 23, &out);
    CHECK(st == WIFI_MGMT_ERR_TOO_SHORT, "len 23: TOO_SHORT");
    CHECK(is_zero(&out), "len 23: out en cero");

    /* 5. borde exacto 24 -> OK */
    build_frame(frame, 0x0C);
    st = wifi_mgmt_parse(frame, 24, &out);
    CHECK(st == WIFI_MGMT_OK, "len 24 (borde): OK");

    /* 6. frame_type != 0 (frame de control) -> ERR_NOT_MGMT, out en cero (sin fuga de subtype) */
    build_frame(frame, 0x0C);
    frame[0] = (uint8_t)(frame[0] | 0x04);   /* bits de tipo (2-3) = 01 -> control */
    memset(&out, 0xA5, sizeof(out));
    st = wifi_mgmt_parse(frame, 24, &out);
    CHECK(st == WIFI_MGMT_ERR_NOT_MGMT, "control: NOT_MGMT");
    CHECK(is_zero(&out), "control: out en cero (sin fuga de frame_subtype)");

    /* 7. NULL buf (out valido) -> ERR_NULL y out en cero; NULL out -> ERR_NULL sin crash */
    build_frame(frame, 0x0C);
    memset(&out, 0xA5, sizeof(out));
    st = wifi_mgmt_parse(NULL, 24, &out);
    CHECK(st == WIFI_MGMT_ERR_NULL, "buf NULL: ERR_NULL");
    CHECK(is_zero(&out), "buf NULL: out en cero");
    st = wifi_mgmt_parse(frame, 24, NULL);
    CHECK(st == WIFI_MGMT_ERR_NULL, "out NULL: ERR_NULL (sin crash)");

    printf("%d checks, %d fallos\n", g_checks, g_failures);
    return g_failures == 0 ? 0 : 1;
}
