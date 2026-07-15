/*
 * Smoke test de enlace C/C++. Verifica que wifi_mgmt_parse (compilado como C)
 * se enlaza correctamente desde una unidad de traduccion C++ gracias a las guardas
 * extern "C" del header. Si faltaran, g++ aplicaria name mangling al simbolo y el
 * enlace contra el objeto C (simbolo sin mangling) fallaria con "undefined reference".
 * Se compila como C++ (g++) y se enlaza con wifi_mgmt_parser.c compilado como C.
 */
#include "wifi_mgmt_parser.h"
#include <cstdio>
#include <cstring>

int main()
{
    uint8_t frame[24];
    std::memset(frame, 0, sizeof(frame));
    frame[0] = static_cast<uint8_t>(0x0C << 4);   /* mgmt, subtype deauth 0x0C */

    wifi_mgmt_frame_t out;
    wifi_mgmt_status_t st = wifi_mgmt_parse(frame, sizeof(frame), &out);

    if (st != WIFI_MGMT_OK) {
        std::printf("FAIL: status inesperado %d\n", static_cast<int>(st));
        return 1;
    }
    if (out.frame_subtype != 0x0C) {
        std::printf("FAIL: subtype 0x%02X != 0x0C\n", out.frame_subtype);
        return 1;
    }
    std::printf("OK: enlace C/C++ (extern \"C\") verificado\n");
    return 0;
}
