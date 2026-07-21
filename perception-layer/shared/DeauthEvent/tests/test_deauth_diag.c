/*
 * Unit tests de deauth_diag (F6a-1). Cubren: init, minimos/maximos, acumulacion
 * delta->total, saturacion en UINT64_MAX, peor caso EXACTO (501 + NUL = 502),
 * buffer exacto, truncamiento, punteros NULL, node_id invalido y longitudes
 * 1/64/65, y salida vacia (out[0]=='\0') ante CUALQUIER error.
 * NOTA: este modulo NO tiene fuzzing; el fuzz de DeauthEvent cubre el parser de
 * BSSID y se conserva como gate de regresion.
 * Bajo ASAN/UBSAN, -Wall -Wextra -Werror, C99.
 */
#include "deauth_diag.h"
#include <stdio.h>
#include <string.h>

static int g_fail = 0;

#define CHECK(cond, msg)                                                   \
    do {                                                                   \
        if (!(cond)) {                                                     \
            printf("FAIL: %s (linea %d)\n", (msg), __LINE__);              \
            ++g_fail;                                                      \
        }                                                                  \
    } while (0)

/* Rellena buf con n caracteres validos + NUL. */
static void mk_node(char *buf, size_t n)
{
    size_t i;
    for (i = 0; i < n; ++i) buf[i] = 'A';
    buf[n] = '\0';
}

int main(void)
{
    deauth_diag_state_t st;
    deauth_diag_delta_t d;
    char out[DEAUTH_DIAG_BUFFER_SIZE];
    int n;

    /* 1) init: minimos en UINT32_MAX (sin dato), maximos y totales en 0. */
    deauth_diag_init(&st);
    CHECK(st.stack_min_free_bytes == UINT32_MAX, "1a: stack_min init");
    CHECK(st.heap_min_free_bytes == UINT32_MAX, "1b: heap_min init");
    CHECK(st.queue_max_depth == 0 && st.mtu_negotiated == 0, "1c: max/mtu init");
    CHECK(st.total_dropped_events == 0 && st.total_dropped_mtu == 0, "1d: totales init");
    CHECK(st.total_rate_limited_suppressed == 0 && st.total_rate_limit_fail_open == 0, "1e: totales rl init");
    deauth_diag_init(NULL);   /* defensivo: no debe desreferenciar */

    /* 2) minimos: se conserva el MENOR observado. */
    deauth_diag_observe_stack_free(&st, 3000);
    deauth_diag_observe_stack_free(&st, 1500);
    deauth_diag_observe_stack_free(&st, 2500);
    CHECK(st.stack_min_free_bytes == 1500, "2a: stack_min conserva el menor");
    deauth_diag_observe_heap_free(&st, 90000);
    deauth_diag_observe_heap_free(&st, 80000);
    deauth_diag_observe_heap_free(&st, 85000);
    CHECK(st.heap_min_free_bytes == 80000, "2b: heap_min conserva el menor");

    /* 3) maximo de cola: se conserva el MAYOR observado. */
    deauth_diag_observe_queue_depth(&st, 5);
    deauth_diag_observe_queue_depth(&st, 12);
    deauth_diag_observe_queue_depth(&st, 7);
    CHECK(st.queue_max_depth == 12, "3: queue_max conserva el mayor");

    /* 4) mtu: es valor vigente, NO minimo ni maximo. */
    deauth_diag_set_mtu(&st, 247);
    deauth_diag_set_mtu(&st, 23);
    CHECK(st.mtu_negotiated == 23, "4: mtu es el vigente");

    /* 5) acumulacion delta -> total (varias ventanas). */
    d.dropped_events = 2; d.dropped_mtu = 3; d.rate_limited_suppressed = 40; d.rate_limit_fail_open = 1;
    deauth_diag_accumulate(&st, &d);
    deauth_diag_accumulate(&st, &d);
    CHECK(st.total_dropped_events == 4, "5a: total dropped_events");
    CHECK(st.total_dropped_mtu == 6, "5b: total dropped_mtu");
    CHECK(st.total_rate_limited_suppressed == 80, "5c: total suppressed");
    CHECK(st.total_rate_limit_fail_open == 2, "5d: total fail_open");
    deauth_diag_accumulate(&st, NULL);   /* defensivo */
    deauth_diag_accumulate(NULL, &d);    /* defensivo */
    CHECK(st.total_dropped_events == 4, "5e: NULL no altera totales");

    /* 6) saturacion: total cerca de UINT64_MAX + delta -> UINT64_MAX (no envuelve). */
    deauth_diag_init(&st);
    st.total_dropped_events = UINT64_MAX - 5u;
    d.dropped_events = 10; d.dropped_mtu = 0; d.rate_limited_suppressed = 0; d.rate_limit_fail_open = 0;
    deauth_diag_accumulate(&st, &d);
    CHECK(st.total_dropped_events == UINT64_MAX, "6a: satura en UINT64_MAX");
    deauth_diag_accumulate(&st, &d);
    CHECK(st.total_dropped_events == UINT64_MAX, "6b: se mantiene saturado");

    /* 7) formato valido: prefijo, version y claves esperadas. */
    deauth_diag_init(&st);
    deauth_diag_observe_stack_free(&st, 2048);
    deauth_diag_observe_heap_free(&st, 98765);
    deauth_diag_observe_queue_depth(&st, 7);
    deauth_diag_set_mtu(&st, 247);
    d.dropped_events = 0; d.dropped_mtu = 0; d.rate_limited_suppressed = 12; d.rate_limit_fail_open = 0;
    deauth_diag_accumulate(&st, &d);
    n = deauth_diag_format(&st, &d, "ESP32_1_CH_01", 123456u, out, sizeof(out));
    CHECK(n > 0 && (size_t)n < sizeof(out), "7a: formato exitoso");
    CHECK(strncmp(out, "[DIAG] {\"diag_v\":1,", 19) == 0, "7b: prefijo y version");
    CHECK(strstr(out, "\"n\":\"ESP32_1_CH_01\"") != NULL, "7c: node_id");
    CHECK(strstr(out, "\"stack_min_free_bytes\":2048") != NULL, "7d: stack_min");
    CHECK(strstr(out, "\"queue_max_depth\":7") != NULL, "7e: queue_max");
    CHECK(strstr(out, "\"heap_min_free_bytes\":98765") != NULL, "7f: heap_min");
    CHECK(strstr(out, "\"mtu_negotiated\":247") != NULL, "7g: mtu");
    CHECK(strstr(out, "\"d_rl_suppressed\":12") != NULL, "7h: delta suppressed");
    CHECK(strstr(out, "\"t_rl_suppressed\":12") != NULL, "7i: total suppressed");
    CHECK((size_t)n == strlen(out), "7j: retorno == longitud escrita");

    /* 8) PEOR CASO EXACTO: node_id de 64 y todos los enteros al maximo -> 501. */
    {
        char node64[DEAUTH_DIAG_MAX_NODE_LEN + 1];
        mk_node(node64, DEAUTH_DIAG_MAX_NODE_LEN);
        deauth_diag_init(&st);
        st.stack_min_free_bytes = UINT32_MAX;
        st.heap_min_free_bytes  = UINT32_MAX;
        st.queue_max_depth      = UINT16_MAX;
        st.mtu_negotiated       = UINT16_MAX;
        st.total_dropped_events = UINT64_MAX;
        st.total_dropped_mtu    = UINT64_MAX;
        st.total_rate_limited_suppressed = UINT64_MAX;
        st.total_rate_limit_fail_open    = UINT64_MAX;
        d.dropped_events = UINT32_MAX; d.dropped_mtu = UINT32_MAX;
        d.rate_limited_suppressed = UINT32_MAX; d.rate_limit_fail_open = UINT32_MAX;

        n = deauth_diag_format(&st, &d, node64, UINT64_MAX, out, sizeof(out));
        CHECK(n == (int)DEAUTH_DIAG_MAX_PAYLOAD_LEN, "8a: peor caso == 501 caracteres");
        CHECK((size_t)n == strlen(out), "8b: peor caso escrito completo");
        CHECK(DEAUTH_DIAG_BUFFER_SIZE >= (size_t)n + 1u, "8c: buffer 512 aloja 501+NUL");

        /* 8d) buffer EXACTO (501+1=502) -> exito sin truncar. */
        {
            char exacto[DEAUTH_DIAG_MAX_PAYLOAD_LEN + 1u];
            n = deauth_diag_format(&st, &d, node64, UINT64_MAX, exacto, sizeof(exacto));
            CHECK(n == (int)DEAUTH_DIAG_MAX_PAYLOAD_LEN && strlen(exacto) == (size_t)n,
                  "8d: buffer exacto 502 escribe el peor caso");
        }
        /* 8e) un byte MENOS -> trunca -> salida vacia. */
        {
            char corto[DEAUTH_DIAG_MAX_PAYLOAD_LEN];   /* 501 = falta el NUL */
            n = deauth_diag_format(&st, &d, node64, UINT64_MAX, corto, sizeof(corto));
            CHECK(n == (int)DEAUTH_DIAG_MAX_PAYLOAD_LEN, "8e1: retorno estilo snprintf al truncar");
            CHECK(corto[0] == '\0', "8e2: truncamiento -> salida vacia");
        }
    }

    /* 9) node_id: longitudes 1 y 64 validas; 65 invalida. */
    {
        char n1[2], n64[DEAUTH_DIAG_MAX_NODE_LEN + 1], n65[DEAUTH_DIAG_MAX_NODE_LEN + 2];
        deauth_diag_init(&st);
        d.dropped_events = 0; d.dropped_mtu = 0; d.rate_limited_suppressed = 0; d.rate_limit_fail_open = 0;
        mk_node(n1, 1);
        mk_node(n64, DEAUTH_DIAG_MAX_NODE_LEN);
        mk_node(n65, DEAUTH_DIAG_MAX_NODE_LEN + 1u);
        CHECK(deauth_diag_format(&st, &d, n1, 0, out, sizeof(out)) > 0, "9a: node_id de 1 valido");
        CHECK(deauth_diag_format(&st, &d, n64, 0, out, sizeof(out)) > 0, "9b: node_id de 64 valido");
        n = deauth_diag_format(&st, &d, n65, 0, out, sizeof(out));
        CHECK(n == -1 && out[0] == '\0', "9c: node_id de 65 invalido -> vacio");
        n = deauth_diag_format(&st, &d, "", 0, out, sizeof(out));
        CHECK(n == -1 && out[0] == '\0', "9d: node_id vacio invalido");
        n = deauth_diag_format(&st, &d, "ESP32 CH01", 0, out, sizeof(out));
        CHECK(n == -1 && out[0] == '\0', "9e: node_id con espacio invalido");
        n = deauth_diag_format(&st, &d, "ESP32{01}", 0, out, sizeof(out));
        CHECK(n == -1 && out[0] == '\0', "9f: node_id con llaves invalido");
    }

    /* 10) NULLs y out_size == 0 -> -1 y salida vacia. */
    n = deauth_diag_format(NULL, &d, "N1", 0, out, sizeof(out));
    CHECK(n == -1 && out[0] == '\0', "10a: snapshot NULL");
    n = deauth_diag_format(&st, NULL, "N1", 0, out, sizeof(out));
    CHECK(n == -1 && out[0] == '\0', "10b: delta NULL");
    n = deauth_diag_format(&st, &d, NULL, 0, out, sizeof(out));
    CHECK(n == -1 && out[0] == '\0', "10c: node_id NULL");
    CHECK(deauth_diag_format(&st, &d, "N1", 0, NULL, sizeof(out)) == -1, "10d: out NULL");
    CHECK(deauth_diag_format(&st, &d, "N1", 0, out, 0) == -1, "10e: out_size 0");

    if (g_fail == 0) {
        printf("OK: deauth_diag (init, min/max, delta->total, saturacion, peor caso 501, buffer exacto, truncamiento, NULL/node_id)\n");
        return 0;
    }
    printf("FALLARON %d comprobaciones\n", g_fail);
    return 1;
}
