#ifndef DEAUTH_RATELIMIT_H
#define DEAUTH_RATELIMIT_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Rate-limit compartido de alertas (F5-3, DT-08/DT-09). Modulo C puro: SIN FreeRTOS,
 * SIN heap y SIN estado global oculto. El caller declara una instancia
 * deauth_rate_limiter_t (una por firmware), la inicializa con deauth_ratelimit_init()
 * y pasa el tick actual + el ancho de ventana en cada consulta. Corre SOLO en la tarea
 * worker (nunca en el callback del driver Wi-Fi).
 *
 * Clave = (dst, subtype). Dentro de la ventana medida desde el ULTIMO evento PERMITIDO
 * de esa clave, los duplicados se SUPRIMEN; una supresion NO renueva la ventana (asi un
 * ataque continuo emite como maximo una alerta por ventana, no se silencia para siempre).
 * En el limite exacto (elapsed == window) el evento se PERMITE.
 */

#define DEAUTH_RL_SLOTS 8u

typedef struct {
    struct {
        uint8_t  dst[6];
        uint8_t  subtype;
        uint32_t last_tick;   /* tick del ULTIMO evento PERMITIDO de esta clave */
        bool     used;
    } slots[DEAUTH_RL_SLOTS];
} deauth_rate_limiter_t;

typedef enum {
    DEAUTH_RL_ALLOW      = 0,  /* permitido: clave nueva, o ventana vencida (renueva last_tick) */
    DEAUTH_RL_SUPPRESS   = 1,  /* suprimido: misma clave dentro de la ventana (NO toca last_tick) */
    DEAUTH_RL_ALLOW_FULL = 2   /* permitido por tabla llena (fail-open): 8 entradas activas */
} deauth_rl_result_t;

/* Inicializa (o reinicia) el limitador: todas las entradas quedan libres. */
void deauth_ratelimit_init(deauth_rate_limiter_t *rl);

/*
 * Decide si emitir la alerta de (dst, subtype) en now_tick con ventana window_ticks:
 *   - DEAUTH_RL_ALLOW      clave nueva (reclama un slot libre o uno expirado), o ventana
 *                          vencida de una clave existente (renueva last_tick = now_tick).
 *   - DEAUTH_RL_SUPPRESS   misma clave dentro de la ventana; NO actualiza last_tick.
 *   - DEAUTH_RL_ALLOW_FULL clave nueva y las 8 entradas siguen activas (fail-open): se
 *                          emite igual, pero la clave NO se registra esta vez.
 * Reutiliza PRIMERO un slot libre y, si no hay, uno expirado; solo devuelve fail-open si
 * ninguna entrada esta libre ni expirada. Aritmetica de tick wrap-safe: (uint32_t)(now-last).
 * Si rl o dst es NULL, retorna DEAUTH_RL_ALLOW_FULL (fail-open defensivo). No usa heap.
 */
deauth_rl_result_t deauth_ratelimit_check(deauth_rate_limiter_t *rl,
                                          const uint8_t dst[6], uint8_t subtype,
                                          uint32_t now_tick, uint32_t window_ticks);

#ifdef __cplusplus
}
#endif

#endif /* DEAUTH_RATELIMIT_H */
