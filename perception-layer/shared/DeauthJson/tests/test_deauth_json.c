/*
 * Unit tests de deauth_json_serialize (F5-1). Verifican el contrato de retorno estilo
 * snprintf, los tamanos EXACTOS (113 B con NODE_ID de 13 chars, 164 B con 64 chars),
 * los limites de out_size, la salida vacia ante error/truncamiento y el rechazo de
 * entradas invalidas. Bajo ASAN/UBSAN, -Wall -Wextra -Werror.
 */
#include "deauth_json.h"
#include <stdio.h>
#include <string.h>

static int g_fail = 0;

#define CHECK(cond, msg)                                                       \
    do {                                                                       \
        if (!(cond)) {                                                         \
            printf("FAIL: %s (linea %d)\n", (msg), __LINE__);                  \
            ++g_fail;                                                          \
        }                                                                      \
    } while (0)

/* Construye un evento con MAC uniforme (todos los octetos = fill). */
static void make_event(deauth_event_t *ev, unsigned char fill,
                       unsigned char subtype, unsigned char channel)
{
    memset(ev->src, fill, 6);
    memset(ev->dst, fill, 6);
    memset(ev->bssid, fill, 6);
    ev->channel = channel;
    ev->subtype = subtype;
}

int main(void)
{
    deauth_event_t ev;
    char buf[DEAUTH_JSON_BUFFER_SIZE];
    char node64[65];
    int n;

    /* ---- Peor caso con NODE_ID actual (13 chars) = 113 B ---- */
    make_event(&ev, 0xAB, 12, 11);   /* subtype 12, canal 11 (2 digitos) */
    n = deauth_json_serialize(&ev, "ESP32_3_CH_11", buf, sizeof(buf));
    CHECK(n == 113, "peor caso NODE_ID 13 chars debe medir 113 B");
    CHECK((size_t)n < sizeof(buf), "113 B < buffer 256");
    CHECK(strlen(buf) == (size_t)n, "strlen == retorno en exito (113)");
    CHECK(buf[n] == '\0', "out[n] == NUL en exito (113)");
    CHECK(buf[0] == '{' && buf[n - 1] == '}', "JSON bien delimitado (113)");

    /* 113 B con out_size = 114 (n+1) -> EXITO exacto */
    n = deauth_json_serialize(&ev, "ESP32_3_CH_11", buf, 114);
    CHECK(n == 113 && strlen(buf) == 113 && buf[113] == '\0', "113 B con buffer 114 -> exito");

    /* 113 B con out_size = 113 -> TRUNCAMIENTO y salida vacia */
    n = deauth_json_serialize(&ev, "ESP32_3_CH_11", buf, 113);
    CHECK(n >= 113, "buffer 113 -> retorno >= out_size (truncamiento)");
    CHECK(buf[0] == '\0', "buffer 113 -> salida vacia en truncamiento");

    /* ---- Peor caso teorico con NODE_ID de 64 chars = 164 B ---- */
    memset(node64, 'A', 64);
    node64[64] = '\0';
    make_event(&ev, 0xFF, 12, 11);
    n = deauth_json_serialize(&ev, node64, buf, sizeof(buf));
    CHECK(n == 164, "NODE_ID de 64 chars debe medir 164 B exactos");
    CHECK(strlen(buf) == 164 && buf[164] == '\0', "strlen/NUL consistentes (164)");

    /* 164 B con out_size = 165 (n+1) -> EXITO exacto */
    n = deauth_json_serialize(&ev, node64, buf, 165);
    CHECK(n == 164 && strlen(buf) == 164, "164 B con buffer 165 -> exito");

    /* 164 B con out_size = 164 -> TRUNCAMIENTO y salida vacia */
    n = deauth_json_serialize(&ev, node64, buf, 164);
    CHECK(n >= 164 && buf[0] == '\0', "buffer 164 -> truncamiento y salida vacia");

    /* ---- Mapeo DT-24 (PRESERVADO, no corregido): src->s, dst->d, bssid->b ----
     * Con MAC DISTINTAS por campo, un intercambio accidental s/d/b se detecta. */
    {
        deauth_event_t ev2;
        static const unsigned char SRC[6]   = { 0x11, 0x11, 0x11, 0x11, 0x11, 0x11 };
        static const unsigned char DST[6]   = { 0x22, 0x22, 0x22, 0x22, 0x22, 0x22 };
        static const unsigned char BSSID[6] = { 0x33, 0x33, 0x33, 0x33, 0x33, 0x33 };
        memcpy(ev2.src, SRC, 6);
        memcpy(ev2.dst, DST, 6);
        memcpy(ev2.bssid, BSSID, 6);
        ev2.channel = 6;
        ev2.subtype = 12;
        n = deauth_json_serialize(&ev2, "ESP32_1_CH_01", buf, sizeof(buf));
        CHECK(n > 0, "serializa con MAC distintas");
        /* Expectativas EXACTAS e independientes (no derivadas del propio JSON): */
        CHECK(strstr(buf, "\"s\":\"11:11:11:11:11:11\"") != NULL, "src -> campo s (spoofed_bssid)");
        CHECK(strstr(buf, "\"d\":\"22:22:22:22:22:22\"") != NULL, "dst -> campo d (target_mac)");
        CHECK(strstr(buf, "\"b\":\"33:33:33:33:33:33\"") != NULL, "bssid -> campo b (bssid)");
        /* Negativo: ninguna MAC debe aparecer en el campo equivocado. */
        CHECK(strstr(buf, "\"s\":\"22:") == NULL && strstr(buf, "\"s\":\"33:") == NULL, "s no lleva dst/bssid");
        CHECK(strstr(buf, "\"d\":\"11:") == NULL && strstr(buf, "\"d\":\"33:") == NULL, "d no lleva src/bssid");
        CHECK(strstr(buf, "\"b\":\"11:") == NULL && strstr(buf, "\"b\":\"22:") == NULL, "b no lleva src/dst");
    }

    /* ---- Contenido: deauth (e=12) y disassoc (e=10), MAC 00 y FF ---- */
    make_event(&ev, 0x00, 12, 1);
    n = deauth_json_serialize(&ev, "ESP32_1_CH_01", buf, sizeof(buf));
    CHECK(n > 0 && strstr(buf, "\"e\":12") != NULL, "deauth emite e:12");
    CHECK(strstr(buf, "\"s\":\"00:00:00:00:00:00\"") != NULL, "MAC 00 emitida como 00:..");
    CHECK(strstr(buf, "\"v\":1") == buf + 1 || strstr(buf, "\"v\":1") != NULL, "v hardcodeado a 1");
    CHECK(strstr(buf, "\"c\":1}") != NULL, "canal 1 emitido");

    make_event(&ev, 0xFF, 10, 14);
    n = deauth_json_serialize(&ev, "ESP32_4_SCANN", buf, sizeof(buf));
    CHECK(n > 0 && strstr(buf, "\"e\":10") != NULL, "disassoc emite e:10");
    CHECK(strstr(buf, "\"b\":\"FF:FF:FF:FF:FF:FF\"") != NULL, "MAC FF emitida en mayuscula");
    CHECK(strstr(buf, "\"c\":14}") != NULL, "canal 14 emitido");

    /* ---- Errores de contrato -> retorno < 0 y salida vacia ---- */
    make_event(&ev, 0xAB, 12, 6);

    n = deauth_json_serialize(&ev, "ESP32_1_CH_01", buf, 0);
    CHECK(n < 0, "out_size 0 -> error");

    n = deauth_json_serialize(&ev, "ESP32_1_CH_01", NULL, sizeof(buf));
    CHECK(n < 0, "out NULL -> error");

    buf[0] = 'x';
    n = deauth_json_serialize(NULL, "ESP32_1_CH_01", buf, sizeof(buf));
    CHECK(n < 0 && buf[0] == '\0', "ev NULL -> error y salida vacia");

    buf[0] = 'x';
    n = deauth_json_serialize(&ev, NULL, buf, sizeof(buf));
    CHECK(n < 0 && buf[0] == '\0', "node_id NULL -> error y salida vacia");

    buf[0] = 'x';
    n = deauth_json_serialize(&ev, "", buf, sizeof(buf));
    CHECK(n < 0 && buf[0] == '\0', "node_id vacio -> error y salida vacia");

    /* node_id de 65 chars -> > 64 -> error */
    {
        char node65[66];
        memset(node65, 'A', 65);
        node65[65] = '\0';
        n = deauth_json_serialize(&ev, node65, buf, sizeof(buf));
        CHECK(n < 0, "node_id de 65 chars -> error");
    }

    /* node_id con caracteres inseguros para JSON -> error */
    n = deauth_json_serialize(&ev, "bad node", buf, sizeof(buf));   /* espacio */
    CHECK(n < 0, "node_id con espacio -> error");
    n = deauth_json_serialize(&ev, "bad\"quote", buf, sizeof(buf)); /* comilla */
    CHECK(n < 0, "node_id con comilla -> error");
    n = deauth_json_serialize(&ev, "ESP32.1", buf, sizeof(buf));    /* punto */
    CHECK(n < 0, "node_id con punto -> error");

    /* subtype fuera de {10,12} -> error */
    make_event(&ev, 0xAB, 8, 6);
    n = deauth_json_serialize(&ev, "ESP32_1_CH_01", buf, sizeof(buf));
    CHECK(n < 0, "subtype 8 -> error");

    /* canal fuera de [1,14] -> error */
    make_event(&ev, 0xAB, 12, 0);
    n = deauth_json_serialize(&ev, "ESP32_1_CH_01", buf, sizeof(buf));
    CHECK(n < 0, "canal 0 -> error");
    make_event(&ev, 0xAB, 12, 15);
    n = deauth_json_serialize(&ev, "ESP32_1_CH_01", buf, sizeof(buf));
    CHECK(n < 0, "canal 15 -> error");

    /* node_id valido de 64 chars limite -> exito (no error) */
    make_event(&ev, 0xAB, 12, 6);
    n = deauth_json_serialize(&ev, node64, buf, sizeof(buf));
    CHECK(n > 0 && (size_t)n == strlen(buf), "NODE_ID de 64 chars (limite) -> exito, ret==strlen");

    if (g_fail == 0) {
        printf("OK: deauth_json_serialize (tamanos 113/164, limites, salida vacia, rechazos)\n");
        return 0;
    }
    printf("FALLARON %d comprobaciones\n", g_fail);
    return 1;
}
