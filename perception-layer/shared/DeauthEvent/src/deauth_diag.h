#ifndef DEAUTH_DIAG_H
#define DEAUTH_DIAG_H

/*
 * Instrumentacion diagnostica compartida (F6a-1). Modulo C puro y PORTABLE:
 * SIN FreeRTOS, SIN ESP-IDF/Arduino, SIN heap y SIN estado global oculto.
 *
 * Reparto de responsabilidades:
 *   - los ADAPTERS (worker/callback de cada variante) invocan las APIs de
 *     plataforma (uxTaskGetStackHighWaterMark, uxQueueMessagesWaiting,
 *     esp_get_minimum_free_heap_size / ESP.getMinFreeHeap) y pasan los valores
 *     YA CONVERTIDOS A BYTES a este helper;
 *   - este helper solo acumula minimos/maximos/totales y serializa la linea.
 *
 * DEAUTH_DIAG gobierna todo el modulo: con 0 no se declara ni define nada
 * (constantes, tipos, prototipos y cuerpo quedan fuera de la compilacion), de
 * modo que el binario final no contiene simbolos NI literales diagnosticos en
 * ninguna cadena de herramientas. La linea se emite SOLO por consola serie;
 * NUNCA por BLE (no contamina el contrato JSON v1 de DeauthJson).
 */

/* Desactivado por defecto si el build no lo proporciona. */
#ifndef DEAUTH_DIAG
#define DEAUTH_DIAG 0
#endif

/* Solo se aceptan 0 o 1: cualquier otro valor es un error de build. */
#if (DEAUTH_DIAG != 0) && (DEAUTH_DIAG != 1)
#error "DEAUTH_DIAG debe ser 0 o 1"
#endif

#if DEAUTH_DIAG

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define DEAUTH_DIAG_V               1u

/*
 * Peor caso EXACTO de la carga util (sin el NUL): NODE_ID de 64 caracteres y
 * todos los enteros en su maximo (uint64 = 20 digitos, uint32 = 10, uint16 = 5).
 * Verificado campo a campo contra el formato de deauth_diag_format().
 */
#define DEAUTH_DIAG_MAX_PAYLOAD_LEN 501u
#define DEAUTH_DIAG_BUFFER_SIZE     512u

/* El buffer debe poder alojar el peor caso + NUL. Assert portable (C99/C++). */
typedef char deauth_diag_buffer_size_assert
    [(DEAUTH_DIAG_BUFFER_SIZE > DEAUTH_DIAG_MAX_PAYLOAD_LEN) ? 1 : -1];

/* Longitud maxima de node_id aceptada (alineada con _MAX_NODE_LEN del receptor). */
#define DEAUTH_DIAG_MAX_NODE_LEN    64u

/* Estado vivo. Los minimos arrancan en UINT32_MAX = "sin dato observado". */
typedef struct {
    uint32_t stack_min_free_bytes;   /* minimo libre desde el inicio del worker */
    uint32_t heap_min_free_bytes;    /* minimo libre desde el arranque */
    uint16_t queue_max_depth;        /* maximo de las MUESTRAS observadas (no es un maximo absoluto) */
    uint16_t mtu_negotiated;         /* MTU vigente (no es minimo ni maximo) */
    uint64_t total_dropped_events;
    uint64_t total_dropped_mtu;
    uint64_t total_rate_limited_suppressed;
    uint64_t total_rate_limit_fail_open;
} deauth_diag_state_t;

/* Deltas de la ventana de 5 s (una unica captura por ventana). */
typedef struct {
    uint32_t dropped_events;
    uint32_t dropped_mtu;
    uint32_t rate_limited_suppressed;
    uint32_t rate_limit_fail_open;
} deauth_diag_delta_t;

/* Inicializa (o reinicia) el estado. Con st == NULL no hace nada. */
void deauth_diag_init(deauth_diag_state_t *st);

/* Observadores de minimos/maximos. El valor llega YA en bytes / unidades finales. */
void deauth_diag_observe_stack_free(deauth_diag_state_t *st, uint32_t free_bytes);
void deauth_diag_observe_heap_free(deauth_diag_state_t *st, uint32_t free_bytes);
void deauth_diag_observe_queue_depth(deauth_diag_state_t *st, uint16_t depth);
void deauth_diag_set_mtu(deauth_diag_state_t *st, uint16_t mtu);

/* Acumula los deltas de la ventana a los totales, SATURANDO en UINT64_MAX. */
void deauth_diag_accumulate(deauth_diag_state_t *st, const deauth_diag_delta_t *d);

/*
 * Serializa la linea diagnostica a partir de un SNAPSHOT (no toca estado vivo):
 *   [DIAG] {"diag_v":1,"n":...,"up_ms":...,...}
 * Orden de claves FIJO. Retorno estilo snprintf: numero de caracteres que se
 * habrian escrito sin el NUL; >= out_size indica truncamiento. Devuelve -1 ante
 * argumentos invalidos (punteros NULL, node_id vacio/ >64 / con caracteres fuera
 * de [A-Za-z0-9_-], out_size == 0). En CUALQUIER error o truncamiento deja
 * out[0] = '\0' (si hay al menos 1 byte). No usa heap.
 */
int deauth_diag_format(const deauth_diag_state_t *snapshot,
                       const deauth_diag_delta_t *delta,
                       const char *node_id,
                       uint64_t uptime_ms,
                       char *out, size_t out_size);

#ifdef __cplusplus
}
#endif

#endif /* DEAUTH_DIAG */

#endif /* DEAUTH_DIAG_H */
