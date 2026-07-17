/*
 * Harness de fuzzing (libFuzzer) para deauth_parse_bssid. La entrada arbitraria se
 * copia a un buffer de STACK terminado en '\0' (el parser espera una cadena C), de
 * modo que para NINGUNA entrada haya OOB read/write ni UB (ASAN/UBSAN lo detectan).
 * Ademas VERIFICA la garantia de contrato: si el parser falla (retorna 0), out debe
 * quedar COMPLETAMENTE en cero; si se viola, aborta (__builtin_trap) para que el
 * fuzzer lo marque como crash.
 */
#include "deauth_event.h"

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)
{
    char    buf[65];   /* buffer de stack: hasta 64 bytes + terminador '\0' */
    uint8_t out[6];
    size_t  n = (size > 64) ? 64 : size;   /* limitar a un tamano razonable */
    size_t  i;
    int     rc;

    for (i = 0; i < n; ++i) {
        buf[i] = (char)data[i];
    }
    buf[n] = '\0';

    for (i = 0; i < 6; ++i) {
        out[i] = 0xA5;   /* prefill: detecta escrituras parciales */
    }

    rc = deauth_parse_bssid(buf, out);

    if (rc == 0) {
        /* Garantia: ante cualquier fallo, out queda completamente en cero. */
        for (i = 0; i < 6; ++i) {
            if (out[i] != 0) {
                __builtin_trap();
            }
        }
    }

    return 0;
}
