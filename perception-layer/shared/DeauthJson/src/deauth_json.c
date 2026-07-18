#include "deauth_json.h"
#include <stdio.h>   /* snprintf */

/* Charset seguro para el campo "n" sin escaping: [A-Za-z0-9_-], validado por rango
 * ASCII explicito (sin isalnum, que depende del locale). */
static int json_safe_node_char(char c)
{
    return (c >= 'A' && c <= 'Z') ||
           (c >= 'a' && c <= 'z') ||
           (c >= '0' && c <= '9') ||
           c == '_' || c == '-';
}

/* Mide node_id acotando la lectura a lo sumo a 65 bytes (C99 portable; sin strnlen,
 * que es de POSIX). Devuelve:
 *   0..64 : longitud exacta (terminador hallado dentro del rango valido).
 *   65    : hay 65 caracteres no-NUL -> longitud > 64 (rechazo).
 *   -1    : algun caracter no pertenece a [A-Za-z0-9_-] (rechazo).
 * Nunca lee mas alla de node_id[64]. */
static int node_id_len_checked(const char *node_id)
{
    int i;
    for (i = 0; i <= 64; ++i) {
        char c = node_id[i];
        if (c == '\0') {
            return i;            /* longitud exacta en [0, 64] */
        }
        if (!json_safe_node_char(c)) {
            return -1;           /* caracter inseguro */
        }
    }
    return 65;                    /* 65 caracteres no-NUL -> > 64 */
}

int deauth_json_serialize(const deauth_event_t *ev, const char *node_id,
                          char *out, size_t out_size)
{
    int len;
    int n;

    /* out_size == 0 (o out NULL) -> ni siquiera podemos escribir el terminador. */
    if (out == NULL || out_size == 0) {
        return -1;
    }
    /* Estado vacio ANTES de validar (out != NULL, out_size > 0 garantizados aqui). */
    out[0] = '\0';

    if (ev == NULL || node_id == NULL) {
        return -1;
    }
    len = node_id_len_checked(node_id);
    if (len <= 0 || len > 64) {        /* vacio (0), inseguro (-1) o > 64 (65) */
        return -1;
    }
    if (ev->subtype != 10 && ev->subtype != 12) {
        return -1;
    }
    if (ev->channel < 1 || ev->channel > 14) {
        return -1;
    }

    n = snprintf(out, out_size,
                 "{\"v\":1,\"e\":%u,\"n\":\"%s\","
                 "\"s\":\"%02X:%02X:%02X:%02X:%02X:%02X\","
                 "\"d\":\"%02X:%02X:%02X:%02X:%02X:%02X\","
                 "\"b\":\"%02X:%02X:%02X:%02X:%02X:%02X\","
                 "\"c\":%u}",
                 (unsigned)ev->subtype, node_id,
                 (unsigned)ev->src[0], (unsigned)ev->src[1], (unsigned)ev->src[2],
                 (unsigned)ev->src[3], (unsigned)ev->src[4], (unsigned)ev->src[5],
                 (unsigned)ev->dst[0], (unsigned)ev->dst[1], (unsigned)ev->dst[2],
                 (unsigned)ev->dst[3], (unsigned)ev->dst[4], (unsigned)ev->dst[5],
                 (unsigned)ev->bssid[0], (unsigned)ev->bssid[1], (unsigned)ev->bssid[2],
                 (unsigned)ev->bssid[3], (unsigned)ev->bssid[4], (unsigned)ev->bssid[5],
                 (unsigned)ev->channel);

    if (n < 0) {                        /* error de codificacion de snprintf (no esperado) */
        out[0] = '\0';
        return -1;
    }
    if ((size_t)n >= out_size) {        /* truncamiento: no cabe con el NUL */
        out[0] = '\0';
        return n;                       /* ret >= out_size: senal de truncamiento */
    }
    return n;                           /* exito: out[n] == '\0', strlen(out) == n */
}
