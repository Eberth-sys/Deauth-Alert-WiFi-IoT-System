#include "deauth_ratelimit.h"
#include <string.h>

void deauth_ratelimit_init(deauth_rate_limiter_t *rl)
{
    unsigned i;
    if (rl == NULL) {
        return;
    }
    for (i = 0; i < DEAUTH_RL_SLOTS; ++i) {
        memset(rl->slots[i].dst, 0, 6);
        rl->slots[i].subtype   = 0;
        rl->slots[i].last_tick = 0;
        rl->slots[i].used      = false;
    }
}

deauth_rl_result_t deauth_ratelimit_check(deauth_rate_limiter_t *rl,
                                          const uint8_t dst[6], uint8_t subtype,
                                          uint32_t now_tick, uint32_t window_ticks)
{
    unsigned i;
    int free_slot = -1;
    int expired_slot = -1;
    int slot;

    if (rl == NULL || dst == NULL) {
        return DEAUTH_RL_ALLOW_FULL;   /* fail-open defensivo: mejor emitir que perder */
    }

    for (i = 0; i < DEAUTH_RL_SLOTS; ++i) {
        if (rl->slots[i].used &&
            rl->slots[i].subtype == subtype &&
            memcmp(rl->slots[i].dst, dst, 6) == 0) {
            /* Clave existente: suprimir si sigue DENTRO de la ventana. */
            if ((uint32_t)(now_tick - rl->slots[i].last_tick) < window_ticks) {
                return DEAUTH_RL_SUPPRESS;         /* NO renueva last_tick */
            }
            rl->slots[i].last_tick = now_tick;     /* ventana vencida: permitir y renovar */
            return DEAUTH_RL_ALLOW;
        }
        if (!rl->slots[i].used) {
            if (free_slot < 0) {
                free_slot = (int)i;
            }
        } else if ((uint32_t)(now_tick - rl->slots[i].last_tick) >= window_ticks) {
            if (expired_slot < 0) {
                expired_slot = (int)i;
            }
        }
    }

    /* Clave nueva: reclamar PRIMERO un slot libre; si no hay, reutilizar uno expirado. */
    slot = (free_slot >= 0) ? free_slot : expired_slot;
    if (slot >= 0) {
        memcpy(rl->slots[slot].dst, dst, 6);
        rl->slots[slot].subtype   = subtype;
        rl->slots[slot].last_tick = now_tick;
        rl->slots[slot].used      = true;
        return DEAUTH_RL_ALLOW;
    }

    /* Ninguna entrada libre ni expirada: 8 claves activas -> fail-open (emitir, no registrar). */
    return DEAUTH_RL_ALLOW_FULL;
}
