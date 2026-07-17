#include "deauth_event.h"

/* Valor hex de un caracter (mayus o minus); -1 si no es hex. */
static int hex_value(char c)
{
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

int deauth_parse_bssid(const char *str, uint8_t out[6])
{
    size_t i;
    uint8_t tmp[6];   /* se parsea aparte y solo se copia a out en exito total */

    /* out en cero primero: ante cualquier fallo posterior queda determinista. */
    if (out != NULL) {
        for (i = 0; i < 6; ++i) {
            out[i] = 0;
        }
    }
    if (str == NULL || out == NULL) {
        return 0;
    }

    /* Exactamente 17 caracteres: str[0..16] no nulos y str[17] == '\0'. */
    for (i = 0; i < 17; ++i) {
        if (str[i] == '\0') {
            return 0;
        }
    }
    if (str[17] != '\0') {
        return 0;
    }

    /* 6 pares hex en offsets 0,3,6,9,12,15; separador ':' en 2,5,8,11,14. */
    for (i = 0; i < 6; ++i) {
        size_t p = i * 3;
        int hi = hex_value(str[p]);
        int lo = hex_value(str[p + 1]);
        if (hi < 0 || lo < 0) {
            return 0;
        }
        tmp[i] = (uint8_t)((hi << 4) | lo);
        if (i < 5 && str[p + 2] != ':') {
            return 0;
        }
    }

    for (i = 0; i < 6; ++i) {
        out[i] = tmp[i];
    }
    return 1;
}
