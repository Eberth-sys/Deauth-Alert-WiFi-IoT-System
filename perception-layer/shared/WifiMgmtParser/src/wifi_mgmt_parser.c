#include "wifi_mgmt_parser.h"

wifi_mgmt_status_t wifi_mgmt_parse(const uint8_t *buf, size_t frame_len,
                                   wifi_mgmt_frame_t *out)
{
    uint8_t frame_type;
    uint8_t frame_subtype;
    size_t  i;

    /* Inicializacion determinista: si out es valido queda TODO en cero antes de
     * cualquier retorno, de modo que ningun error deje datos parciales. */
    if (out != NULL) {
        out->frame_type = 0;
        out->frame_subtype = 0;
        for (i = 0; i < 6; ++i) {
            out->addr1[i] = 0;
            out->addr2[i] = 0;
            out->addr3[i] = 0;
        }
    }

    if (buf == NULL || out == NULL) {
        return WIFI_MGMT_ERR_NULL;
    }
    if (frame_len < 24) {
        return WIFI_MGMT_ERR_TOO_SHORT;
    }

    /* Tipo/subtipo en variables LOCALES; no se copian a out hasta validar el tipo,
     * para que un frame no-management deje out completamente en cero. */
    frame_type    = (uint8_t)((buf[0] >> 2) & 0x03);
    frame_subtype = (uint8_t)((buf[0] >> 4) & 0x0F);

    if (frame_type != 0) {
        return WIFI_MGMT_ERR_NOT_MGMT;   /* out permanece completamente en cero */
    }

    out->frame_type = frame_type;
    out->frame_subtype = frame_subtype;
    for (i = 0; i < 6; ++i) {
        out->addr1[i] = buf[4  + i];
        out->addr2[i] = buf[10 + i];
        out->addr3[i] = buf[16 + i];
    }

    return WIFI_MGMT_OK;
}
