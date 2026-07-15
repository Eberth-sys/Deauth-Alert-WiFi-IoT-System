/*
 * Harness de fuzzing (libFuzzer) para wifi_mgmt_parse. Alimenta buffers arbitrarios
 * (cualquier tamano/contenido) al parser: para NINGUNA entrada debe haber OOB
 * read/write ni comportamiento indefinido (ASAN/UBSAN lo detectan). El parser no
 * modifica buf ni accede a hardware.
 */
#include "wifi_mgmt_parser.h"

int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size)
{
    wifi_mgmt_frame_t out;
    (void)wifi_mgmt_parse(data, size, &out);
    return 0;
}
