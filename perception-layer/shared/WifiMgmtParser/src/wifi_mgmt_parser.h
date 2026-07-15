#ifndef WIFI_MGMT_PARSER_H
#define WIFI_MGMT_PARSER_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Parser portable de tramas 802.11 management. C puro (C99), sin dependencias de
 * plataforma ni acceso a hardware. Seguro para consumidores C y C++ (extern "C").
 * Reconoce los subtipos deauth (0x0C) y disassoc (0x0A) pero NO decide alertas:
 * el consumidor actua solo sobre 0x0C hasta F5 (ver DT-24 sobre addr2/addr3).
 */

/* Estado de wifi_mgmt_parse(): es el VALOR DE RETORNO, no un campo de la struct. */
typedef enum {
    WIFI_MGMT_OK = 0,
    WIFI_MGMT_ERR_NULL,        /* buf == NULL || out == NULL           */
    WIFI_MGMT_ERR_TOO_SHORT,   /* frame_len < 24                        */
    WIFI_MGMT_ERR_NOT_MGMT     /* frame_type != 0 (no es management)    */
} wifi_mgmt_status_t;

/* Campos extraidos de una trama de management 802.11 (sin FCS). */
typedef struct {
    uint8_t frame_type;     /* (buf[0] >> 2) & 0x03 ; 0 = management            */
    uint8_t frame_subtype;  /* (buf[0] >> 4) & 0x0F ; 0x0C deauth, 0x0A disassoc */
    uint8_t addr1[6];       /* buf[4..9]                                        */
    uint8_t addr2[6];       /* buf[10..15]  (SA/transmisor por 802.11; ver DT-24) */
    uint8_t addr3[6];       /* buf[16..21]  (BSSID por 802.11; ver DT-24)         */
} wifi_mgmt_frame_t;

/*
 * Parsea una trama de management 802.11.
 *   buf       : bytes de la trama de management, SIN los 4 bytes de FCS.
 *   frame_len : bytes validos en buf (= rx_ctrl.sig_len - 4; lo calcula el caller).
 *   out       : struct de salida. Si out != NULL se inicializa COMPLETA a cero de
 *               forma determinista antes de cualquier retorno (incluso en error).
 *
 * Lee byte a byte (sin cast a struct) para evitar UB de alineacion/endianness.
 * Retorna WIFI_MGMT_OK y llena out en exito; un codigo de error en caso contrario.
 */
wifi_mgmt_status_t wifi_mgmt_parse(const uint8_t *buf, size_t frame_len,
                                   wifi_mgmt_frame_t *out);

#ifdef __cplusplus
}
#endif

#endif /* WIFI_MGMT_PARSER_H */
