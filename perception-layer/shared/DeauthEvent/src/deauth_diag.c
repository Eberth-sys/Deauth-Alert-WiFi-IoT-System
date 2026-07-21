#include "deauth_diag.h"

/*
 * Todo el cuerpo -incluidos los literales y el formato "[DIAG]"- vive dentro de
 * #if DEAUTH_DIAG. Con DEAUTH_DIAG=0 esta unidad de traduccion queda vacia a
 * proposito: no emite simbolos ni cadenas, sin depender de que el enlazador
 * recolecte secciones (las cadenas mergeables .rodata.str* NO se recolectan en
 * las cadenas basadas en el core Arduino).
 */
#if DEAUTH_DIAG

#include <inttypes.h>
#include <stdio.h>

/* Suma saturada de un delta de 32 bits sobre un total de 64 bits. */
static void diag_sat_add(uint64_t *acc, uint32_t delta)
{
    if (*acc > UINT64_MAX - (uint64_t)delta) {
        *acc = UINT64_MAX;
    } else {
        *acc += (uint64_t)delta;
    }
}

/* node_id valido: 1..DEAUTH_DIAG_MAX_NODE_LEN caracteres de [A-Za-z0-9_-]. */
static bool diag_node_id_valido(const char *node_id)
{
    size_t i;
    if (node_id == NULL || node_id[0] == '\0') {
        return false;
    }
    /* Se mide acotado (sin strnlen, C99): si supera el tope, es invalido. */
    for (i = 0; i <= (size_t)DEAUTH_DIAG_MAX_NODE_LEN; ++i) {
        char c = node_id[i];
        if (c == '\0') {
            return true;
        }
        if (i == (size_t)DEAUTH_DIAG_MAX_NODE_LEN) {
            return false;   /* no termino dentro del tope */
        }
        if (!((c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') ||
              (c >= '0' && c <= '9') || c == '_' || c == '-')) {
            return false;
        }
    }
    return false;
}

void deauth_diag_init(deauth_diag_state_t *st)
{
    if (st == NULL) {
        return;
    }
    st->stack_min_free_bytes = UINT32_MAX;   /* sin dato observado */
    st->heap_min_free_bytes  = UINT32_MAX;   /* sin dato observado */
    st->queue_max_depth      = 0;
    st->mtu_negotiated       = 0;
    st->total_dropped_events = 0;
    st->total_dropped_mtu    = 0;
    st->total_rate_limited_suppressed = 0;
    st->total_rate_limit_fail_open    = 0;
}

void deauth_diag_observe_stack_free(deauth_diag_state_t *st, uint32_t free_bytes)
{
    if (st != NULL && free_bytes < st->stack_min_free_bytes) {
        st->stack_min_free_bytes = free_bytes;
    }
}

void deauth_diag_observe_heap_free(deauth_diag_state_t *st, uint32_t free_bytes)
{
    if (st != NULL && free_bytes < st->heap_min_free_bytes) {
        st->heap_min_free_bytes = free_bytes;
    }
}

void deauth_diag_observe_queue_depth(deauth_diag_state_t *st, uint16_t depth)
{
    if (st != NULL && depth > st->queue_max_depth) {
        st->queue_max_depth = depth;
    }
}

void deauth_diag_set_mtu(deauth_diag_state_t *st, uint16_t mtu)
{
    if (st != NULL) {
        st->mtu_negotiated = mtu;
    }
}

void deauth_diag_accumulate(deauth_diag_state_t *st, const deauth_diag_delta_t *d)
{
    if (st == NULL || d == NULL) {
        return;
    }
    diag_sat_add(&st->total_dropped_events, d->dropped_events);
    diag_sat_add(&st->total_dropped_mtu, d->dropped_mtu);
    diag_sat_add(&st->total_rate_limited_suppressed, d->rate_limited_suppressed);
    diag_sat_add(&st->total_rate_limit_fail_open, d->rate_limit_fail_open);
}

int deauth_diag_format(const deauth_diag_state_t *snapshot,
                       const deauth_diag_delta_t *delta,
                       const char *node_id,
                       uint64_t uptime_ms,
                       char *out, size_t out_size)
{
    int n;

    if (out == NULL || out_size == 0u) {
        return -1;
    }
    out[0] = '\0';   /* salida vacia ante cualquier error o truncamiento */

    if (snapshot == NULL || delta == NULL || !diag_node_id_valido(node_id)) {
        return -1;
    }

    /* Orden de claves FIJO; el peor caso exacto es DEAUTH_DIAG_MAX_PAYLOAD_LEN. */
    n = snprintf(out, out_size,
                 "[DIAG] {\"diag_v\":%u,\"n\":\"%s\",\"up_ms\":%" PRIu64
                 ",\"stack_min_free_bytes\":%" PRIu32
                 ",\"queue_max_depth\":%u"
                 ",\"heap_min_free_bytes\":%" PRIu32
                 ",\"mtu_negotiated\":%u"
                 ",\"d_dropped_events\":%" PRIu32
                 ",\"d_dropped_mtu\":%" PRIu32
                 ",\"d_rl_suppressed\":%" PRIu32
                 ",\"d_rl_fail_open\":%" PRIu32
                 ",\"t_dropped_events\":%" PRIu64
                 ",\"t_dropped_mtu\":%" PRIu64
                 ",\"t_rl_suppressed\":%" PRIu64
                 ",\"t_rl_fail_open\":%" PRIu64 "}",
                 (unsigned)DEAUTH_DIAG_V, node_id, uptime_ms,
                 snapshot->stack_min_free_bytes,
                 (unsigned)snapshot->queue_max_depth,
                 snapshot->heap_min_free_bytes,
                 (unsigned)snapshot->mtu_negotiated,
                 delta->dropped_events,
                 delta->dropped_mtu,
                 delta->rate_limited_suppressed,
                 delta->rate_limit_fail_open,
                 snapshot->total_dropped_events,
                 snapshot->total_dropped_mtu,
                 snapshot->total_rate_limited_suppressed,
                 snapshot->total_rate_limit_fail_open);

    if (n < 0 || (size_t)n >= out_size) {
        out[0] = '\0';   /* fallo o truncamiento: no se emite nada parcial */
    }
    return n;
}

#else  /* !DEAUTH_DIAG */

/* Unidad vacia deliberada: evita el diagnostico "ISO C forbids an empty
   translation unit" sin emitir simbolos ni cadenas. */
typedef int diag_tu_not_empty_t;

#endif /* DEAUTH_DIAG */
