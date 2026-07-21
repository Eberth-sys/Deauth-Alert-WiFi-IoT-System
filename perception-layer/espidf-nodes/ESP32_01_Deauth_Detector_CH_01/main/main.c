//perception-layer\espidf-nodes\ESP32_01_Deauth_Detector_CH_01\main\main.c

// Inclusión de librerías del framework ESP-IDF necesarias para Wi-Fi, BLE, sistema de eventos y logs.
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "esp_bt.h"
#include "esp_bt_main.h"
#include "esp_gap_ble_api.h"
#include "esp_gatts_api.h"
#include "esp_bt_defs.h"
#include "string.h"
#include "esp_gatt_common_api.h"

// Inclusión de la configuración específica del dispositivo (UUIDs y BSSID objetivo)
#include "../../config/config.h"
#include "wifi_mgmt_parser.h"   // Parser portable de la cabecera 802.11 (biblioteca compartida, F4b)
#include "deauth_event.h"       // Modelo de evento POD + parser de BSSID (biblioteca compartida, F4c-1)
#include "deauth_json.h"        // Serializador del contrato JSON v1 (biblioteca compartida, F5-1)
#include "deauth_ratelimit.h"   // Rate-limit compartido de alertas (biblioteca compartida, F5-3)

// (F6a-1) Instrumentacion diagnostica: DESACTIVADA por defecto. Se habilita con
// -DDEAUTH_DIAG=1 (variable CMake cacheada). Con 0 no se compila nada de este bloque.
#ifndef DEAUTH_DIAG
#define DEAUTH_DIAG 0
#endif
#if DEAUTH_DIAG
#include "esp_system.h"         // esp_get_minimum_free_heap_size()
#include "esp_timer.h"          // uptime de 64 bits (sin wrap) para la linea [DIAG]
#include "deauth_diag.h"        // Helper portable de instrumentacion (F6a-1)
#endif
#include "freertos/queue.h"     // Cola FreeRTOS estatica (F4c-2)

// Definiciones para identificación del nodo
#define TAG "ESP32_01_CH01" // Etiqueta de logs
#define DEVICE_NAME "ESP32_01_Deauth_Detector_CH_01" // Nombre BLE del dispositivo

// (F4d-1) Identidad canonica del nodo para el contrato de datos. Es DISTINTA del nombre BLE
// anunciado y de las etiquetas de log: debe coincidir con device['name'] de
// processing-layer/config/devices.yaml, que es la identidad operativa autoritativa (ligada a
// la MAC BLE de la conexion). F5 la emitira como campo "n" del JSON; ante discrepancia, la
// RPi conserva su identidad autoritativa y registra el desvio (ya implementado en F3).
#define NODE_ID "ESP32_1_CH_01"
// ble_manager.py rechaza un "n" vacio o de mas de _MAX_NODE_LEN (64) caracteres.
_Static_assert(sizeof(NODE_ID) > 1,
               "F4d-1: NODE_ID no puede estar vacio");
_Static_assert(sizeof(NODE_ID) - 1 <= 64,
               "F4d-1: NODE_ID excede _MAX_NODE_LEN (64) de ble_manager.py");

// Canal de Wi-Fi en el que este ESP32 operará (canal 1)
static uint8_t current_channel = 1;

// Variables de estado BLE
static bool device_connected = false;
static uint16_t conn_id = 0;
static esp_gatt_if_t gatts_if = ESP_GATT_IF_NONE;
static uint16_t char_handle;

// (F4d-2) MTU ATT negociado con el central (bajo ble_mux, mismo grupo que el estado BLE).
// Arranca en el default (23) y solo cambia con ESP_GATTS_MTU_EVT del conn_id activo.
static uint16_t negotiated_mtu = ESP_GATT_DEF_BLE_MTU_SIZE;
#define DEAUTH_LOCAL_MTU 247   // (F4d-2) MTU local maximo a solicitar (<= ESP_GATT_MAX_MTU_SIZE=517)

// --- F4c-2: BSSID pre-parseado + cola estatica + worker + contador de descartes ---
static uint8_t target_bssid[6];

#define DEAUTH_WORKER_STACK_BYTES 4096
// Los toolchains fijados (ESP-IDF 5.1 / Arduino Core 3.2.0, Xtensa) definen StackType_t como
// uint8_t (1 byte); por eso sizeof(worker_stack) == bytes de stack. Si cambiara, detener aqui.
_Static_assert(sizeof(StackType_t) == 1,
               "F4c-2 asume StackType_t de 1 byte; sizeof(worker_stack) debe equivaler a los bytes de stack");

static uint8_t       queue_storage[DEAUTH_QUEUE_DEPTH * sizeof(deauth_event_t)];   // 16*20 = 320 B
static StaticQueue_t queue_static;
static QueueHandle_t event_queue = NULL;

static StackType_t   worker_stack[DEAUTH_WORKER_STACK_BYTES / sizeof(StackType_t)];
static StaticTask_t  worker_tcb;

// Contador de descartes: protegido con seccion critica portMUX (nunca solo volatile).
static portMUX_TYPE  dropped_mux = portMUX_INITIALIZER_UNLOCKED;
static uint32_t      dropped_events = 0;

// (F4d-2) Descartes por payload > capacidad del MTU: contador SEPARADO de dropped_events, con su
// PROPIA seccion critica (nunca anidar con ble_mux ni con dropped_mux).
static portMUX_TYPE  mtu_mux = portMUX_INITIALIZER_UNLOCKED;
static uint32_t      dropped_mtu = 0;
static uint16_t      dropped_mtu_last = 0;   // MTU vigente en el ultimo descarte (para el reporte)

// (F5-3) Rate-limit de alertas por (dst, subtype): instancia + contadores WORKER-ONLY (sin portMUX;
// solo la tarea worker los toca). rate_limited_suppressed = duplicados; rate_limit_fail_open = tabla llena.
static deauth_rate_limiter_t rate_limiter;
static uint32_t      rate_limited_suppressed = 0;
static uint32_t      rate_limit_fail_open = 0;

#if DEAUTH_DIAG
// (F6a-1) Estado diagnostico compartido callback<->worker con mux DEDICADO: nunca se
// anida con dropped_mux, mtu_mux ni ble_mux. El buffer es ESTATICO (no vive en el stack
// del worker) para no perturbar el watermark que se esta midiendo.
static deauth_diag_state_t diag_state;
static portMUX_TYPE        diag_mux = portMUX_INITIALIZER_UNLOCKED;
static char                diag_line[DEAUTH_DIAG_BUFFER_SIZE];
#endif

// Estado BLE compartido (gatts handler <-> worker): device_connected/conn_id/gatts_if/char_handle.
static portMUX_TYPE  ble_mux = portMUX_INITIALIZER_UNLOCKED;

// Definiciones del servicio BLE
static esp_gatt_srvc_id_t service_id;
static esp_bt_uuid_t char_uuid = { .len = ESP_UUID_LEN_128 };

// UUID de servicio/caracteristica ya convertidos y validados en app_main (F4a).
static uint8_t g_service_uuid128[16];
static uint8_t g_char_uuid128[16];

// Parámetros para la publicidad BLE
static esp_ble_adv_params_t adv_params = {
    .adv_int_min = 0x20,  // Intervalo mínimo de advertising
    .adv_int_max = 0x40,  // Intervalo máximo de advertising
    .adv_type = ADV_TYPE_IND,  // Advertising general
    .own_addr_type = BLE_ADDR_TYPE_PUBLIC,
    .channel_map = ADV_CHNL_ALL,
    .adv_filter_policy = ADV_FILTER_ALLOW_SCAN_ANY_CON_ANY,
};

// Convierte un UUID canonico (36 chars: 32 hex + 4 guiones) a binario de 128 bits.
// Devuelve false si el UUID es invalido (no continuar con UUID parcial).
static bool string_to_uuid(const char* uuid_str, uint8_t* uuid128) {
    if (uuid_str == NULL) return false;
    if (strlen(uuid_str) != 36) return false;                 // longitud canonica

    char hex_str[33];
    int j = 0;
    for (int i = 0; uuid_str[i] != '\0'; i++) {
        char c = uuid_str[i];
        if (c == '-') {
            if (i != 8 && i != 13 && i != 18 && i != 23) return false;  // guiones canonicos
            continue;
        }
        bool is_hex = (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F');
        if (!is_hex) return false;                            // solo hexadecimal
        if (j >= (int)sizeof(hex_str) - 1) return false;      // limite del buffer
        hex_str[j++] = c;
    }
    if (j != 32) return false;                                // exactamente 32 hex
    hex_str[j] = '\0';

    for (int i = 0; i < 16; i++) {
        char byte_str[3] = { hex_str[30 - i*2], hex_str[31 - i*2], '\0' };
        uuid128[i] = (uint8_t)strtol(byte_str, NULL, 16);
    }
    return true;
}

// Configura seguridad para las conexiones BLE (modo seguro con autenticación)
static void setup_ble_security() {
    esp_ble_auth_req_t auth_req = ESP_LE_AUTH_REQ_SC_MITM;
    esp_ble_io_cap_t iocap = ESP_IO_CAP_NONE;
    uint8_t key_size = 16;
    uint8_t init_key = ESP_BLE_ENC_KEY_MASK | ESP_BLE_ID_KEY_MASK;
    uint8_t rsp_key = ESP_BLE_ENC_KEY_MASK | ESP_BLE_ID_KEY_MASK;

    esp_ble_gap_set_security_param(ESP_BLE_SM_AUTHEN_REQ_MODE, &auth_req, sizeof(auth_req));
    esp_ble_gap_set_security_param(ESP_BLE_SM_IOCAP_MODE, &iocap, sizeof(iocap));
    esp_ble_gap_set_security_param(ESP_BLE_SM_MAX_KEY_SIZE, &key_size, sizeof(key_size));
    esp_ble_gap_set_security_param(ESP_BLE_SM_SET_INIT_KEY, &init_key, sizeof(init_key));
    esp_ble_gap_set_security_param(ESP_BLE_SM_SET_RSP_KEY, &rsp_key, sizeof(rsp_key));
}

#if !DEAUTH_DIAG
// Reporte rate-limited (>= 5 s, wrap-safe) de descartes. Lee+resetea el contador dentro
// de la MISMA seccion critica; jamas la mantiene durante el log.
static void report_dropped(TickType_t* last_tick) {
    TickType_t now = xTaskGetTickCount();
    if ((TickType_t)(now - *last_tick) < pdMS_TO_TICKS(5000)) return;
    *last_tick = now;
    uint32_t d;
    portENTER_CRITICAL(&dropped_mux);
    d = dropped_events;
    dropped_events = 0;
    portEXIT_CRITICAL(&dropped_mux);
    if (d) ESP_LOGW(TAG, "Eventos descartados por cola llena en los ultimos 5 s: %u", (unsigned)d);
}

// (F4d-2) Reporte rate-limited (>= 5 s, wrap-safe) de descartes por MTU insuficiente. Mismo patron
// que report_dropped; sin logs por evento. Incluye cantidad, MTU y capacidad util.
static void report_mtu_dropped(TickType_t* last_tick) {
    TickType_t now = xTaskGetTickCount();
    if ((TickType_t)(now - *last_tick) < pdMS_TO_TICKS(5000)) return;
    *last_tick = now;
    uint32_t d;
    uint16_t m;
    portENTER_CRITICAL(&mtu_mux);
    d = dropped_mtu;
    m = dropped_mtu_last;
    dropped_mtu = 0;
    portEXIT_CRITICAL(&mtu_mux);
    if (d) {
        uint16_t cap = (m >= 3) ? (uint16_t)(m - 3) : 0;
        ESP_LOGW(TAG, "Alertas descartadas por MTU insuficiente en los ultimos 5 s: %u (MTU=%u, capacidad util=%u B)",
                 (unsigned)d, (unsigned)m, (unsigned)cap);
    }
}

// (F5-3) Reporte rate-limited (>= 5 s, wrap-safe) de duplicados suprimidos y de fail-open por tabla
// llena. Contadores WORKER-ONLY (sin seccion critica). Sin logs por evento; solo si el contador > 0.
static void report_rate_limited(TickType_t* last_tick) {
    TickType_t now = xTaskGetTickCount();
    if ((TickType_t)(now - *last_tick) < pdMS_TO_TICKS(5000)) return;
    *last_tick = now;
    if (rate_limited_suppressed) {
        ESP_LOGW(TAG, "Alertas duplicadas suprimidas por rate-limit en los ultimos 5 s: %u",
                 (unsigned)rate_limited_suppressed);
        rate_limited_suppressed = 0;
    }
    if (rate_limit_fail_open) {
        ESP_LOGW(TAG, "Fail-open del rate-limit (tabla llena) en los ultimos 5 s: %u",
                 (unsigned)rate_limit_fail_open);
        rate_limit_fail_open = 0;
    }
}
#endif  /* !DEAUTH_DIAG */

#if DEAUTH_DIAG
// (F6a-1) Ventana unica de 5 s: UNA sola captura de los cuatro contadores, reutilizada por
// los warnings existentes (mismo texto), por los deltas y por los totales. Los locks se
// toman y liberan DE A UNO, jamas anidados; el formateo y los logs van FUERA de todo lock.
static void report_window_5s(TickType_t* last_tick) {
    TickType_t now = xTaskGetTickCount();
    if ((TickType_t)(now - *last_tick) < pdMS_TO_TICKS(5000)) return;
    *last_tick = now;

    deauth_diag_delta_t d;
    deauth_diag_state_t snap;
    uint16_t mtu_last, mtu_now;

    portENTER_CRITICAL(&dropped_mux);
    d.dropped_events = dropped_events;
    dropped_events = 0;
    portEXIT_CRITICAL(&dropped_mux);

    portENTER_CRITICAL(&mtu_mux);
    d.dropped_mtu = dropped_mtu;
    mtu_last = dropped_mtu_last;
    dropped_mtu = 0;
    portEXIT_CRITICAL(&mtu_mux);

    // Contadores worker-only: no requieren seccion critica.
    d.rate_limited_suppressed = rate_limited_suppressed;
    d.rate_limit_fail_open    = rate_limit_fail_open;
    rate_limited_suppressed = 0;
    rate_limit_fail_open    = 0;

    portENTER_CRITICAL(&ble_mux);
    mtu_now = negotiated_mtu;
    portEXIT_CRITICAL(&ble_mux);

    // Watermark convertido EXPLICITAMENTE a bytes (el _Static_assert de StackType_t vigila la unidad).
    const uint32_t stack_free = (uint32_t)uxTaskGetStackHighWaterMark(NULL) * (uint32_t)sizeof(StackType_t);
    const uint32_t heap_free  = (uint32_t)esp_get_minimum_free_heap_size();

    portENTER_CRITICAL(&diag_mux);
    deauth_diag_observe_stack_free(&diag_state, stack_free);
    deauth_diag_observe_heap_free(&diag_state, heap_free);
    deauth_diag_set_mtu(&diag_state, mtu_now);
    deauth_diag_accumulate(&diag_state, &d);
    snap = diag_state;
    portEXIT_CRITICAL(&diag_mux);

    if (d.dropped_events) ESP_LOGW(TAG, "Eventos descartados por cola llena en los ultimos 5 s: %u", (unsigned)d.dropped_events);
    if (d.dropped_mtu) {
        uint16_t cap = (mtu_last >= 3) ? (uint16_t)(mtu_last - 3) : 0;
        ESP_LOGW(TAG, "Alertas descartadas por MTU insuficiente en los ultimos 5 s: %u (MTU=%u, capacidad util=%u B)",
                 (unsigned)d.dropped_mtu, (unsigned)mtu_last, (unsigned)cap);
    }
    if (d.rate_limited_suppressed) {
        ESP_LOGW(TAG, "Alertas duplicadas suprimidas por rate-limit en los ultimos 5 s: %u",
                 (unsigned)d.rate_limited_suppressed);
    }
    if (d.rate_limit_fail_open) {
        ESP_LOGW(TAG, "Fail-open del rate-limit (tabla llena) en los ultimos 5 s: %u",
                 (unsigned)d.rate_limit_fail_open);
    }

    // Linea diagnostica: SOLO por consola serie, NUNCA por BLE (no toca el contrato JSON v1).
    {
        const uint64_t up_ms = (uint64_t)(esp_timer_get_time() / 1000);
        int n = deauth_diag_format(&snap, &d, NODE_ID, up_ms, diag_line, sizeof(diag_line));
        if (n > 0 && (size_t)n < sizeof(diag_line)) ESP_LOGI(TAG, "%s", diag_line);
    }
}
#endif  /* DEAUTH_DIAG */

// Tarea worker: drena la cola y emite la alerta como JSON v1 (serializa + ESP_LOGI + BLE).
static void deauth_worker(void* arg) {
    (void)arg;
    deauth_event_t e;
    TickType_t last_report = xTaskGetTickCount();
#if !DEAUTH_DIAG
    TickType_t last_mtu_report = last_report;
    TickType_t last_rl_report = last_report;
#endif
    deauth_ratelimit_init(&rate_limiter);   // (F5-3) instancia explicita, sin estado global oculto
    for (;;) {
        if (xQueueReceive(event_queue, &e, pdMS_TO_TICKS(1000)) == pdTRUE) {
            // (F5-3) Rate-limit por (dst, subtype) ANTES de serializar/emitir. if(allow) (no continue):
            // los reportes periodicos de abajo (fuera de xQueueReceive) corren siempre, aun al suprimir.
            deauth_rl_result_t rl_res = deauth_ratelimit_check(&rate_limiter, e.dst, e.subtype,
                                                              (uint32_t)xTaskGetTickCount(), pdMS_TO_TICKS(1000));
            if (rl_res == DEAUTH_RL_SUPPRESS) {
                rate_limited_suppressed++;   // duplicado dentro de la ventana: no serializa ni emite
            } else {
                if (rl_res == DEAUTH_RL_ALLOW_FULL) rate_limit_fail_open++;   // tabla llena: fail-open observable
                char alert_msg[DEAUTH_JSON_BUFFER_SIZE];
                int n = deauth_json_serialize(&e, NODE_ID, alert_msg, sizeof(alert_msg));
                if (n < 0 || (size_t)n >= sizeof(alert_msg)) {
                    ESP_LOGW(TAG, "no se pudo serializar la alerta JSON");
                } else {
                    ESP_LOGI(TAG, "%s", alert_msg);   // (F5) diagnostico: el MISMO JSON v1 que se envia por BLE

                    // Snapshot consistente del estado BLE y del MTU bajo lock; se libera ANTES de enviar.
                    bool          conn;
                    uint16_t      cid, chdl, mtu;
                    esp_gatt_if_t gif;
                    portENTER_CRITICAL(&ble_mux);
                    conn = device_connected;
                    cid  = conn_id;
                    gif  = gatts_if;
                    chdl = char_handle;
                    mtu  = negotiated_mtu;
                    portEXIT_CRITICAL(&ble_mux);

                    if (conn) {
                        // (F4d-2) Capacidad util de una notificacion = MTU negociado - 3 (cabecera ATT).
                        size_t capacity = (mtu >= 3) ? (size_t)(mtu - 3) : 0;
                        if ((size_t)n > capacity) {
                            // No cabe: NO truncar, NO enviar. Contar en seccion critica independiente
                            // (ble_mux ya liberado; nunca anidar con ble_mux/dropped_mux).
                            portENTER_CRITICAL(&mtu_mux);
                            dropped_mtu++;
                            dropped_mtu_last = mtu;
                            portEXIT_CRITICAL(&mtu_mux);
                        } else {
                            esp_err_t r = esp_ble_gatts_send_indicate(gif, cid, chdl,
                                                                      (size_t)n, (uint8_t*)alert_msg, false);
                            if (r != ESP_OK) {
                                // Una desconexion posterior al snapshot da un error controlado, nunca acceso invalido.
                                ESP_LOGW(TAG, "esp_ble_gatts_send_indicate fallo (%d)", r);
                            }
                        }
                    }
                }
            }
        }
#if DEAUTH_DIAG
        report_window_5s(&last_report);   // (F6a-1) captura UNICA por ventana
#else
        report_dropped(&last_report);
        report_mtu_dropped(&last_mtu_report);
        report_rate_limited(&last_rl_report);
#endif
    }
}

static void wifi_sniffer_callback(void* buf, wifi_promiscuous_pkt_type_t type) {
    // (B) Solo tramas de management, antes de interpretar buf.
    if (type != WIFI_PKT_MGMT) return;

    const wifi_promiscuous_pkt_t* pkt = (const wifi_promiscuous_pkt_t*)buf;

    // (A) Longitud real de la trama, descontando el FCS de 4 bytes.
    uint16_t sig_len = pkt->rx_ctrl.sig_len;
    if (sig_len < 4) return;
    size_t frame_len = (size_t)sig_len - 4;
    if (frame_len < 24) return;   // cabecera MAC de management (data[0..23])

    // (orden seguro) Parseo portable de la cabecera; no se accede a data[] directamente.
    wifi_mgmt_frame_t frame;
    if (wifi_mgmt_parse(pkt->payload, frame_len, &frame) != WIFI_MGMT_OK) return;
    if (frame.frame_subtype != 0x0C && frame.frame_subtype != 0x0A) return;   // deauth (0x0C) y disassoc (0x0A)

    // BSSID objetivo: comparacion binaria de 6 bytes (sin snprintf/strcmp en el callback).
    if (memcmp(frame.addr2, target_bssid, 6) != 0) return;

    // Copiar el evento (mapeo DT-24: BSSID=addr2, src=addr3, dst=addr1) y encolar sin bloquear.
    deauth_event_t e;
    memcpy(e.bssid, frame.addr2, 6);
    memcpy(e.src,   frame.addr3, 6);
    memcpy(e.dst,   frame.addr1, 6);
    e.channel = pkt->rx_ctrl.channel;   // (C) canal desde los metadatos de recepcion
    e.subtype = frame.frame_subtype;    // 0x0C (deauth) o 0x0A (disassoc)

    if (xQueueSend(event_queue, &e, 0) != pdTRUE) {
        // Cola llena: incrementar el contador de descartes en seccion critica minima.
        portENTER_CRITICAL(&dropped_mux);
        dropped_events++;
        portEXIT_CRITICAL(&dropped_mux);
    }
#if DEAUTH_DIAG
    else {
        // (F6a-1) Sonda diagnostica: profundidad OBSERVADA inmediatamente despues del encolado
        // exitoso. Es una MUESTRA, no un maximo absoluto (el worker puede consumir entre ambas
        // operaciones). Introduce una perturbacion pequena; solo existe con DEAUTH_DIAG=1.
        const UBaseType_t depth = uxQueueMessagesWaiting(event_queue);
        portENTER_CRITICAL(&diag_mux);
        deauth_diag_observe_queue_depth(&diag_state, (uint16_t)depth);
        portEXIT_CRITICAL(&diag_mux);
    }
#endif
}

// Manejador de eventos de GAP (advertising BLE)
static void gap_event_handler(esp_gap_ble_cb_event_t event, esp_ble_gap_cb_param_t* param) {
    switch (event) {
        case ESP_GAP_BLE_ADV_DATA_SET_COMPLETE_EVT:
            ESP_LOGI(TAG, "Configuración de advertising completada");
            break;
        default:
            break;
    }
}

// Manejador de eventos de GATT Server (BLE)
static void gatts_event_handler(esp_gatts_cb_event_t event, esp_gatt_if_t gatt_if,
                                esp_ble_gatts_cb_param_t* param) {
    switch (event) {
        case ESP_GATTS_REG_EVT:
            ESP_LOGI(TAG, "Servicio BLE registrado");
            esp_ble_gap_set_device_name(DEVICE_NAME);
            esp_ble_gap_config_local_privacy(true);
            memset(&service_id, 0, sizeof(service_id));
            service_id.id.inst_id = 0x00;
            service_id.is_primary = true;
            service_id.id.uuid.len = ESP_UUID_LEN_128;
            memcpy(service_id.id.uuid.uuid.uuid128, g_service_uuid128, sizeof(g_service_uuid128));
            esp_ble_gatts_create_service(gatt_if, &service_id, 4);
            break;

        case ESP_GATTS_CREATE_EVT:
            ESP_LOGI(TAG, "Servicio creado");
            esp_ble_gatts_start_service(param->create.service_handle);
            memcpy(char_uuid.uuid.uuid128, g_char_uuid128, sizeof(g_char_uuid128));
            esp_ble_gatts_add_char(param->create.service_handle, &char_uuid,
                                   ESP_GATT_PERM_READ,
                                   ESP_GATT_CHAR_PROP_BIT_READ | ESP_GATT_CHAR_PROP_BIT_NOTIFY,
                                   NULL, NULL);
            break;

        case ESP_GATTS_ADD_CHAR_EVT:
            portENTER_CRITICAL(&ble_mux);
            char_handle = param->add_char.attr_handle;
            portEXIT_CRITICAL(&ble_mux);
            ESP_LOGI(TAG, "Característica BLE creada. Handle: %d", char_handle);
            break;

        case ESP_GATTS_CONNECT_EVT:
            portENTER_CRITICAL(&ble_mux);
            device_connected = true;
            conn_id = param->connect.conn_id;
            gatts_if = gatt_if;
            negotiated_mtu = ESP_GATT_DEF_BLE_MTU_SIZE;   // (F4d-2) MTU efectivo arranca en el default
            portEXIT_CRITICAL(&ble_mux);
            ESP_LOGI(TAG, "Dispositivo conectado por BLE");
            break;

        case ESP_GATTS_MTU_EVT: {
            // (F4d-2) Actualizar el MTU negociado SOLO si el evento corresponde a la conexion activa.
            bool mtu_accepted;
            portENTER_CRITICAL(&ble_mux);
            mtu_accepted = (device_connected && param->mtu.conn_id == conn_id);
            if (mtu_accepted) {
                negotiated_mtu = param->mtu.mtu;
            }
            portEXIT_CRITICAL(&ble_mux);
            if (mtu_accepted) {
                // Observabilidad (una sola linea, FUERA del lock): evidencia de la negociacion real.
                uint16_t cap = (param->mtu.mtu >= 3) ? (uint16_t)(param->mtu.mtu - 3) : 0;
                ESP_LOGI(TAG, "ble_mtu_negotiated=%u conn_id=%u capacity=%u",
                         (unsigned)param->mtu.mtu, (unsigned)param->mtu.conn_id, (unsigned)cap);
            }
            break;
        }

        case ESP_GATTS_DISCONNECT_EVT:
            portENTER_CRITICAL(&ble_mux);
            // (F4d-2) Restablecer a 23 con la misma condicion de conn_id que la actualizacion.
            if (param->disconnect.conn_id == conn_id) {
                negotiated_mtu = ESP_GATT_DEF_BLE_MTU_SIZE;
            }
            device_connected = false;
            portEXIT_CRITICAL(&ble_mux);
            ESP_LOGI(TAG, "Dispositivo desconectado por BLE");
            esp_ble_gap_start_advertising(&adv_params);
            break;

        default:
            break;
    }
}

// Función principal de ejecución del firmware
void app_main() {
    ESP_LOGI(TAG, "node_id=%s", NODE_ID);   // (F4d-1) identidad canonica; ver devices.yaml
    // (F4a) Validar SERVICE_UUID y CHARACTERISTIC_UUID ANTES de toda inicializacion
    // (evita dejar un servicio BLE parcialmente creado con un UUID invalido).
    if (!string_to_uuid(SERVICE_UUID, g_service_uuid128) ||
        !string_to_uuid(CHARACTERISTIC_UUID, g_char_uuid128)) {
        ESP_LOGE(TAG, "SERVICE_UUID o CHARACTERISTIC_UUID invalido; se aborta la inicializacion");
        return;
    }

    // Inicialización del almacenamiento no volátil
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    // Inicialización de Wi-Fi en modo promiscuo
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_start());
    // (D) Configurar el filtro de management ANTES de habilitar el modo promiscuo.
    wifi_promiscuous_filter_t filter = {0};
    filter.filter_mask = WIFI_PROMIS_FILTER_MASK_MGMT;
    esp_err_t filt_err = esp_wifi_set_promiscuous_filter(&filter);
    if (filt_err != ESP_OK) {
        ESP_LOGE(TAG, "esp_wifi_set_promiscuous_filter fallo (%d); no se habilita el modo promiscuo", filt_err);
        return;
    }
    // (F4c-2) Validar TARGET_BSSID, crear cola y worker ANTES de registrar el callback y
    // habilitar el modo promiscuo. Cualquier fallo impide activar la captura (sin fallback dinamico).
    if (!deauth_parse_bssid(TARGET_BSSID, target_bssid)) {
        ESP_LOGE(TAG, "TARGET_BSSID invalido; no se habilita la captura");
        return;
    }
    event_queue = xQueueCreateStatic(DEAUTH_QUEUE_DEPTH, sizeof(deauth_event_t),
                                     queue_storage, &queue_static);
    if (event_queue == NULL) {
        ESP_LOGE(TAG, "xQueueCreateStatic fallo; no se habilita la captura");
        return;
    }
#if DEAUTH_DIAG
    // (F6a-1) Init ANTES de crear el worker y de habilitar el callback promiscuo: evita que una
    // primera muestra alcance un estado sin inicializar si el scheduler adelanta la tarea.
    deauth_diag_init(&diag_state);
#endif
    if (xTaskCreateStatic(deauth_worker, "deauth_worker", sizeof(worker_stack), NULL,
                          tskIDLE_PRIORITY + 1, worker_stack, &worker_tcb) == NULL) {
        ESP_LOGE(TAG, "xTaskCreateStatic fallo; no se habilita la captura");
        return;
    }

    ESP_ERROR_CHECK(esp_wifi_set_promiscuous_rx_cb(wifi_sniffer_callback));
    ESP_ERROR_CHECK(esp_wifi_set_channel(current_channel, WIFI_SECOND_CHAN_NONE));   // canal ANTES de habilitar
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous(true));                                  // habilitar al final

    ESP_LOGI(TAG, "Modo promiscuo activo | Canal: %d | Target BSSID: %s", current_channel, TARGET_BSSID);

    // Inicialización del stack BLE
    esp_bt_controller_config_t bt_cfg = BT_CONTROLLER_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_bt_controller_init(&bt_cfg));
    ESP_ERROR_CHECK(esp_bt_controller_enable(ESP_BT_MODE_BLE));
    ESP_ERROR_CHECK(esp_bluedroid_init());
    ESP_ERROR_CHECK(esp_bluedroid_enable());
    // (F4d-2) Solicitar el MTU local maximo acordable (247). Solo declara nuestro maximo; el MTU
    // efectivo lo fija la negociacion con el central. No abortar la captura si falla.
    esp_err_t mtu_err = esp_ble_gatt_set_local_mtu(DEAUTH_LOCAL_MTU);
    if (mtu_err != ESP_OK) {
        ESP_LOGW(TAG, "esp_ble_gatt_set_local_mtu(%u) fallo (%d); el MTU efectivo puede quedar en 23",
                 (unsigned)DEAUTH_LOCAL_MTU, mtu_err);
    }

    // Configura la seguridad de BLE
    setup_ble_security();

    // Registro de callbacks
    esp_ble_gap_register_callback(gap_event_handler);
    esp_ble_gatts_register_callback(gatts_event_handler);
    esp_ble_gatts_app_register(0);

    // Configuración de datos de advertising BLE
    esp_ble_adv_data_t adv_data = {
        .set_scan_rsp = false,
        .include_name = true,
        .include_txpower = true,
        .min_interval = 0x20,
        .max_interval = 0x40,
        .appearance = 0x00,
        .manufacturer_len = 0,
        .p_manufacturer_data = NULL,
        .service_data_len = 0,
        .p_service_data = NULL,
        .service_uuid_len = 16,
        .p_service_uuid = service_id.id.uuid.uuid.uuid128,
        .flag = (ESP_BLE_ADV_FLAG_GEN_DISC | ESP_BLE_ADV_FLAG_BREDR_NOT_SPT),
    };

    // Inicia la publicidad BLE
    esp_ble_gap_config_adv_data(&adv_data);
    esp_ble_gap_start_advertising(&adv_params);

    // Ciclo principal en espera
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000)); // Espera de 1 segundo
    }
}
