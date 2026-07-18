#ifndef DEAUTH_JSON_H
#define DEAUTH_JSON_H

#include <stddef.h>
#include "deauth_event.h"   /* deauth_event_t (POD 20 B); SOLO el header, sin funciones */

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Serializador del contrato de eventos v1 (DEC-0003), solo con snprintf sobre buffers
 * fijos (sin ArduinoJson/cJSON ni heap). La version "v":1 esta HARDCODEADA: DeauthJson
 * es EXCLUSIVO del contrato v1 y no recibe la version como parametro, para no poder
 * emitir un contrato incompatible por error.
 *
 * Formato de salida (una linea, sin espacios):
 *   {"v":1,"e":<12|10>,"n":"<node_id>","s":"<MAC>","d":"<MAC>","b":"<MAC>","c":<1..14>}
 *   - e = ev->subtype (12 = 0x0C deauth, 10 = 0x0A disassoc), entero sin comillas.
 *   - s = ev->src, d = ev->dst, b = ev->bssid (mapeo DT-24 PRESERVADO, no se corrige aqui).
 *   - MACs en "%02X:%02X:%02X:%02X:%02X:%02X" (mayuscula), aceptadas por el parser de la RPi.
 *   - c = ev->channel, entero sin comillas.
 */

/* Peor caso del payload EXCLUYENDO el terminador NUL: NODE_ID de 64 chars => 164 B.
 * Con los NODE_ID actuales (13 chars) el peor caso es 113 B. Requieren out_size >= n+1
 * (114 B y 165 B respectivamente) por el terminador. */
#define DEAUTH_JSON_MAX_PAYLOAD_LEN 164u
/* Buffer de trabajo recomendado; INCLUYE el terminador NUL con holgura. */
#define DEAUTH_JSON_BUFFER_SIZE     256u

/*
 * Serializa (*ev, node_id) como JSON del contrato v1 en out[0 .. out_size).
 *
 * Semantica de retorno (estilo snprintf):
 *   0 <= ret < out_size : EXITO. Longitud n = ret; out[n] == '\0'; strlen(out) == n.
 *   ret >= out_size     : TRUNCAMIENTO. No cabe (habria hecho falta out_size = ret + 1).
 *                         out queda VACIO (out[0] == '\0').
 *   ret < 0             : ERROR de contrato. out queda vacio cuando es posible.
 *
 * Validaciones (todas -> ret < 0):
 *   - out == NULL, o out_size == 0, o ev == NULL, o node_id == NULL.
 *   - node_id vacio, o de longitud > 64, o con algun caracter fuera de [A-Za-z0-9_-].
 *   - ev->subtype no en {10, 12}.
 *   - ev->channel no en [1, 14].
 *
 * Si out != NULL y out_size > 0, out[0] se pone a '\0' ANTES de validar; ante error o
 * truncamiento, out queda vacio. Un payload de 113 B requiere out_size >= 114; uno de
 * 164 B requiere out_size >= 165.
 */
int deauth_json_serialize(const deauth_event_t *ev, const char *node_id,
                          char *out, size_t out_size);

#ifdef __cplusplus
}
#endif

#endif /* DEAUTH_JSON_H */
