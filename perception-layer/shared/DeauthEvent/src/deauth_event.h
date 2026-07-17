#ifndef DEAUTH_EVENT_H
#define DEAUTH_EVENT_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Modelo compartido del evento de deautenticacion (F4c-1). C puro (C99), portable y
 * seguro para consumidores C y C++ (extern "C"). NO usa FreeRTOS, atomicos ni hardware:
 * define el "formulario" (POD), la profundidad de cola y el parser de BSSID. La cola
 * FreeRTOS, la tarea worker y el contador de descartes (protegido con seccion critica
 * portMUX_TYPE) se agregan en F4c-2.
 */

/* Profundidad de la cola de eventos (centralizada, ajustable). F4c-1 NO crea colas. */
#define DEAUTH_QUEUE_DEPTH 16

/* Evento POD que viajara por la cola: SOLO uint8_t -> alineacion 1, sin padding. */
typedef struct {
    uint8_t bssid[6];    /* = frame.addr2 (mapeo DT-24) */
    uint8_t src[6];      /* = frame.addr3               */
    uint8_t dst[6];      /* = frame.addr1               */
    uint8_t channel;     /* rx_ctrl.channel             */
    uint8_t subtype;     /* 0x0C                        */
} deauth_event_t;

/* Asercion de tamano == 20 B, portable: C++ / C11 / fallback C99. */
#if defined(__cplusplus)
    static_assert(sizeof(deauth_event_t) == 20, "deauth_event_t debe ocupar 20 bytes");
#elif defined(__STDC_VERSION__) && (__STDC_VERSION__ >= 201112L)
    _Static_assert(sizeof(deauth_event_t) == 20, "deauth_event_t debe ocupar 20 bytes");
#else
    /* C99 (o anterior): arreglo de tamano negativo si la condicion es falsa. */
    typedef char deauth_event_size_is_20[(sizeof(deauth_event_t) == 20) ? 1 : -1];
#endif

/*
 * Parsea un BSSID canonico "AA:BB:CC:DD:EE:FF" a 6 bytes.
 *   str : exactamente 17 caracteres; ':' en 2/5/8/11/14; hex mayus o minus.
 *   out : 6 bytes. Si out != NULL se pone COMPLETO en cero antes de retornar; ante
 *         CUALQUIER fallo queda en cero (nunca parcial).
 * Retorna 1 en exito, 0 en fallo (NULL, longitud, separador o hex invalido).
 */
int deauth_parse_bssid(const char *str, uint8_t out[6]);

#ifdef __cplusplus
}
#endif

#endif /* DEAUTH_EVENT_H */
