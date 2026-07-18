/*
 * Harness de fuzzing (libFuzzer) para deauth_json_serialize. Construye un evento y un
 * node_id arbitrario a partir de la entrada; el subtype y el canal se fuerzan a rangos
 * validos para ejercitar a fondo el manejo del node_id (la parte propensa a OOB) y la
 * serializacion. Para NINGUNA entrada debe haber OOB (ASAN/UBSAN); ademas VERIFICA los
 * invariantes de contrato: en exito el JSON esta bien delimitado y strlen == retorno;
 * ante error o truncamiento la salida queda vacia. Si se viola, aborta (__builtin_trap).
 */
#include "deauth_json.h"
#include <string.h>

static void check_invariants(const char *out, size_t out_size, int n)
{
    if (n < 0) {
        if (out[0] != '\0') __builtin_trap();                 /* error -> salida vacia */
    } else if ((size_t)n >= out_size) {
        if (out[0] != '\0') __builtin_trap();                 /* truncamiento -> salida vacia */
    } else {
        if (strlen(out) != (size_t)n) __builtin_trap();       /* longitud consistente */
        if (n < 2 || out[0] != '{' || out[n - 1] != '}') __builtin_trap();
    }
}

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)
{
    deauth_event_t ev;
    char node[80];       /* node_id arbitrario, terminado en '\0' */
    char out[DEAUTH_JSON_BUFFER_SIZE];
    char small[16];      /* fuerza el camino de truncamiento sin OOB */
    size_t nlen, i;

    memset(&ev, 0, sizeof(ev));
    /* subtype y canal SIEMPRE validos -> se ejercita el node_id y el snprintf. */
    ev.subtype = (size >= 1 && (data[0] & 1)) ? 12 : 10;
    ev.channel = (uint8_t)((size >= 2 ? (data[1] % 14) : 0) + 1);   /* [1, 14] */
    for (i = 0; i < 6; ++i) {
        ev.src[i]   = (size > 2 + i)  ? data[2 + i]  : 0;
        ev.dst[i]   = (size > 8 + i)  ? data[8 + i]  : 0;
        ev.bssid[i] = (size > 14 + i) ? data[14 + i] : 0;
    }
    nlen = (size > 20) ? (size - 20) : 0;
    if (nlen > sizeof(node) - 1) nlen = sizeof(node) - 1;
    for (i = 0; i < nlen; ++i) {
        node[i] = (char)data[20 + i];
    }
    node[nlen] = '\0';

    check_invariants(out, sizeof(out), deauth_json_serialize(&ev, node, out, sizeof(out)));
    check_invariants(small, sizeof(small), deauth_json_serialize(&ev, node, small, sizeof(small)));
    return 0;
}
