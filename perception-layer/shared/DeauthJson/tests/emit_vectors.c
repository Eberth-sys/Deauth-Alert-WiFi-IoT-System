/*
 * Emisor de vectores dorados para el cruce de contrato C->Python (F5-1). Serializa con
 * deauth_json_serialize SOLO vectores VALIDOS y los imprime, uno por linea, con columnas
 * de GROUND-TRUTH separadas por tab, calculadas desde la ENTRADA (no desde el JSON):
 *
 *   <expected_node>\t<event_type>\t<s>\t<d>\t<b>\t<c>\t<json>
 *
 * Asi contract_cross.py compara la salida de parse_event contra el ground-truth (columnas),
 * NO contra el propio JSON emitido: un intercambio accidental s/d/b en el serializador se
 * detecta porque las MAC de src/dst/bssid son DISTINTAS por campo. Preserva el mapeo DT-24
 * (src->s, dst->d, bssid->b); no lo corrige.
 *
 * Los RECHAZOS del serializador se prueban en test_deauth_json.c; los rechazos de JSON
 * arbitrario por el parser estan cubiertos por los tests F3. Aqui NO se fabrica JSON invalido.
 */
#include "deauth_json.h"
#include <stdio.h>
#include <string.h>

/* Formatea una MAC de 6 bytes de forma INDEPENDIENTE del serializador (ground truth). */
static void fmt_mac(char out[18], const unsigned char m[6])
{
    snprintf(out, 18, "%02X:%02X:%02X:%02X:%02X:%02X",
             m[0], m[1], m[2], m[3], m[4], m[5]);
}

static int emit(const char *expected_node, const char *node_id,
                unsigned char subtype, unsigned char channel,
                const unsigned char s[6], const unsigned char d[6], const unsigned char b[6])
{
    deauth_event_t ev;
    char out[DEAUTH_JSON_BUFFER_SIZE];
    char smac[18], dmac[18], bmac[18];
    const char *ev_type;
    int n;

    memcpy(ev.src, s, 6);
    memcpy(ev.dst, d, 6);
    memcpy(ev.bssid, b, 6);
    ev.channel = channel;
    ev.subtype = subtype;

    n = deauth_json_serialize(&ev, node_id, out, sizeof(out));
    if (n < 0 || (size_t)n >= sizeof(out)) {
        fprintf(stderr, "emit_vectors: fallo inesperado al serializar un vector valido (n=%d)\n", n);
        return 1;
    }

    /* Ground-truth desde la ENTRADA (no desde el JSON). */
    fmt_mac(smac, s);
    fmt_mac(dmac, d);
    fmt_mac(bmac, b);
    ev_type = (subtype == 12) ? "deauth" : "disassoc";   /* 12 -> deauth, 10 -> disassoc */

    printf("%s\t%s\t%s\t%s\t%s\t%u\t%s\n",
           expected_node, ev_type, smac, dmac, bmac, (unsigned)channel, out);
    return 0;
}

int main(void)
{
    /* MAC DISTINTAS por campo en los vectores sensibles al mapeo (detectan swap s/d/b). */
    const unsigned char s1[6] = { 0x11,0x11,0x11,0x11,0x11,0x11 };
    const unsigned char d1[6] = { 0x22,0x22,0x22,0x22,0x22,0x22 };
    const unsigned char b1[6] = { 0x33,0x33,0x33,0x33,0x33,0x33 };
    const unsigned char s2[6] = { 0x44,0x44,0x44,0x44,0x44,0x44 };
    const unsigned char d2[6] = { 0x55,0x55,0x55,0x55,0x55,0x55 };
    const unsigned char b2[6] = { 0x66,0x66,0x66,0x66,0x66,0x66 };
    const unsigned char mac_zero[6] = { 0,0,0,0,0,0 };
    const unsigned char mac_ff[6]   = { 0xFF,0xFF,0xFF,0xFF,0xFF,0xFF };
    const unsigned char s5[6] = { 0xAA,0xAA,0xAA,0xAA,0xAA,0xAA };
    const unsigned char d5[6] = { 0xBB,0xBB,0xBB,0xBB,0xBB,0xBB };
    const unsigned char b5[6] = { 0xCC,0xCC,0xCC,0xCC,0xCC,0xCC };
    int rc = 0;

    /* V1 deauth (e=12), canal 1, MAC distintas -> detecta swap s/d/b */
    rc |= emit("ESP32_1_CH_01", "ESP32_1_CH_01", 12, 1, s1, d1, b1);
    /* V2 disassoc (e=10), canal 6, MAC distintas */
    rc |= emit("ESP32_2_CH_06", "ESP32_2_CH_06", 10, 6, s2, d2, b2);
    /* V3 extremo MAC 00:00:.., canal 11 */
    rc |= emit("ESP32_3_CH_11", "ESP32_3_CH_11", 12, 11, mac_zero, mac_zero, mac_zero);
    /* V4 extremo MAC FF:FF:.., canal 14 (limite superior) */
    rc |= emit("ESP32_4_SCANN", "ESP32_4_SCANN", 10, 14, mac_ff, mac_ff, mac_ff);
    /* V5 discrepancia: "n" del payload (ESP32_1_CH_01) != expected_node (ESP32_2_CH_06) + MAC distintas */
    rc |= emit("ESP32_2_CH_06", "ESP32_1_CH_01", 12, 1, s5, d5, b5);

    return rc;
}
