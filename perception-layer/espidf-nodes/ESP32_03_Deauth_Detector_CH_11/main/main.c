//perception-layer\espidf-nodes\ESP32_03_Deauth_Detector_CH_11\main\main.c

// Inclusión de librerías del framework ESP-IDF necesarias para Wi-Fi, BLE, eventos y sistema base
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

// Archivo de configuración local, contiene UUIDs BLE y BSSID objetivo
#include "../../config/config.h"
#include "wifi_mgmt_parser.h"   // Parser portable de la cabecera 802.11 (biblioteca compartida, F4b)
#include "deauth_event.h"       // Modelo de evento POD + parser de BSSID (biblioteca compartida, F4c-1)
#include "freertos/queue.h"     // Cola FreeRTOS estatica (F4c-2)

// Etiquetas únicas para este nodo (canal 11)
#define TAG "ESP32_03_CH11"  // Para logs específicos de este nodo
#define DEVICE_NAME "ESP32_03_Deauth_Detector_CH_11"  // Nombre visible en BLE

// (F4d-1) Identidad canonica del nodo para el contrato de datos. Es DISTINTA del nombre BLE
// anunciado y de las etiquetas de log: debe coincidir con device['name'] de
// processing-layer/config/devices.yaml, que es la identidad operativa autoritativa (ligada a
// la MAC BLE de la conexion). F5 la emitira como campo "n" del JSON; ante discrepancia, la
// RPi conserva su identidad autoritativa y registra el desvio (ya implementado en F3).
#define NODE_ID "ESP32_3_CH_11"
// ble_manager.py rechaza un "n" vacio o de mas de _MAX_NODE_LEN (64) caracteres.
_Static_assert(sizeof(NODE_ID) > 1,
               "F4d-1: NODE_ID no puede estar vacio");
_Static_assert(sizeof(NODE_ID) - 1 <= 64,
               "F4d-1: NODE_ID excede _MAX_NODE_LEN (64) de ble_manager.py");

// Canal de escaneo: se fija al canal 11
static uint8_t current_channel = 11;

// Variables de estado de la conexión BLE
static bool device_connected = false;
static uint16_t conn_id = 0;
static esp_gatt_if_t gatts_if = ESP_GATT_IF_NONE;
static uint16_t char_handle;

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

// Estado BLE compartido (gatts handler <-> worker): device_connected/conn_id/gatts_if/char_handle.
static portMUX_TYPE  ble_mux = portMUX_INITIALIZER_UNLOCKED;

// Definiciones para el servicio BLE
static esp_gatt_srvc_id_t service_id;
static esp_bt_uuid_t char_uuid = { .len = ESP_UUID_LEN_128 };

// UUID de servicio/caracteristica ya convertidos y validados en app_main (F4a).
static uint8_t g_service_uuid128[16];
static uint8_t g_char_uuid128[16];

// Configuración de parámetros de publicidad BLE
static esp_ble_adv_params_t adv_params = {
    .adv_int_min = 0x20,  // Intervalo mínimo de advertising
    .adv_int_max = 0x40,  // Intervalo máximo de advertising
    .adv_type = ADV_TYPE_IND,  // Publicidad general
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

// Configuración de seguridad para las conexiones BLE
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

// Formatea una MAC de 6 bytes a "XX:XX:XX:XX:XX:XX".
static void mac_to_str(const uint8_t mac[6], char out[18]) {
    snprintf(out, 18, "%02X:%02X:%02X:%02X:%02X:%02X",
             mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
}

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

// Tarea worker: drena la cola y hace el trabajo lento (formateo, log, BLE). Conserva printf + ESP_LOGI.
static void deauth_worker(void* arg) {
    (void)arg;
    deauth_event_t e;
    TickType_t last_report = xTaskGetTickCount();
    for (;;) {
        if (xQueueReceive(event_queue, &e, pdMS_TO_TICKS(1000)) == pdTRUE) {
            char bssid[18], src_mac[18], dst_mac[18], alert_msg[256];
            mac_to_str(e.bssid, bssid);
            mac_to_str(e.src, src_mac);
            mac_to_str(e.dst, dst_mac);
            int n = snprintf(alert_msg, sizeof(alert_msg),
                             "[ALERT] Ataque de Deauthentication detectado | Origen: %s | Destino: %s | BSSID: %s | Canal: %d",
                             src_mac, dst_mac, bssid, e.channel);
            if (n < 0 || (size_t)n >= sizeof(alert_msg)) {
                ESP_LOGW(TAG, "no se pudo formatear la alerta");
            } else {
                printf("%s\n", alert_msg);
                ESP_LOGI(TAG, "%s", alert_msg);

                // Snapshot consistente del estado BLE bajo lock; el lock se libera ANTES de enviar.
                bool          conn;
                uint16_t      cid, chdl;
                esp_gatt_if_t gif;
                portENTER_CRITICAL(&ble_mux);
                conn = device_connected;
                cid  = conn_id;
                gif  = gatts_if;
                chdl = char_handle;
                portEXIT_CRITICAL(&ble_mux);

                if (conn) {
                    esp_err_t r = esp_ble_gatts_send_indicate(gif, cid, chdl,
                                                              (size_t)n, (uint8_t*)alert_msg, false);
                    if (r != ESP_OK) {
                        // Una desconexion posterior al snapshot da un error controlado, nunca acceso invalido.
                        ESP_LOGW(TAG, "esp_ble_gatts_send_indicate fallo (%d)", r);
                    }
                }
            }
        }
        report_dropped(&last_report);
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
    if (frame.frame_subtype != 0x0C) return;   // solo deauth (0x0C); 0x0A queda reconocido sin alertar

    // BSSID objetivo: comparacion binaria de 6 bytes (sin snprintf/strcmp en el callback).
    if (memcmp(frame.addr2, target_bssid, 6) != 0) return;

    // Copiar el evento (mapeo DT-24: BSSID=addr2, src=addr3, dst=addr1) y encolar sin bloquear.
    deauth_event_t e;
    memcpy(e.bssid, frame.addr2, 6);
    memcpy(e.src,   frame.addr3, 6);
    memcpy(e.dst,   frame.addr1, 6);
    e.channel = pkt->rx_ctrl.channel;   // (C) canal desde los metadatos de recepcion
    e.subtype = frame.frame_subtype;    // 0x0C

    if (xQueueSend(event_queue, &e, 0) != pdTRUE) {
        // Cola llena: incrementar el contador de descartes en seccion critica minima.
        portENTER_CRITICAL(&dropped_mux);
        dropped_events++;
        portEXIT_CRITICAL(&dropped_mux);
    }
}

// Manejador de eventos GAP de BLE (maneja advertising)
static void gap_event_handler(esp_gap_ble_cb_event_t event, esp_ble_gap_cb_param_t* param) {
    switch (event) {
        case ESP_GAP_BLE_ADV_DATA_SET_COMPLETE_EVT:
            ESP_LOGI(TAG, "Configuración de advertising completada");
            break;
        default:
            break;
    }
}

// Manejador de eventos del servidor GATT BLE
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
            portEXIT_CRITICAL(&ble_mux);
            ESP_LOGI(TAG, "Dispositivo conectado por BLE");
            break;

        case ESP_GATTS_DISCONNECT_EVT:
            portENTER_CRITICAL(&ble_mux);
            device_connected = false;
            portEXIT_CRITICAL(&ble_mux);
            ESP_LOGI(TAG, "Dispositivo desconectado por BLE");
            esp_ble_gap_start_advertising(&adv_params);
            break;

        default:
            break;
    }
}

// Función principal del programa (punto de entrada)
void app_main() {
    ESP_LOGI(TAG, "node_id=%s", NODE_ID);   // (F4d-1) identidad canonica; ver devices.yaml
    // (F4a) Validar SERVICE_UUID y CHARACTERISTIC_UUID ANTES de toda inicializacion
    // (evita dejar un servicio BLE parcialmente creado con un UUID invalido).
    if (!string_to_uuid(SERVICE_UUID, g_service_uuid128) ||
        !string_to_uuid(CHARACTERISTIC_UUID, g_char_uuid128)) {
        ESP_LOGE(TAG, "SERVICE_UUID o CHARACTERISTIC_UUID invalido; se aborta la inicializacion");
        return;
    }

    // Inicialización de almacenamiento no volátil y sistema de eventos
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    // Configuración del Wi-Fi en modo promiscuo
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
    if (xTaskCreateStatic(deauth_worker, "deauth_worker", sizeof(worker_stack), NULL,
                          tskIDLE_PRIORITY + 1, worker_stack, &worker_tcb) == NULL) {
        ESP_LOGE(TAG, "xTaskCreateStatic fallo; no se habilita la captura");
        return;
    }

    ESP_ERROR_CHECK(esp_wifi_set_promiscuous_rx_cb(wifi_sniffer_callback));
    ESP_ERROR_CHECK(esp_wifi_set_channel(current_channel, WIFI_SECOND_CHAN_NONE));   // canal ANTES de habilitar
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous(true));                                  // habilitar al final

    ESP_LOGI(TAG, "Modo promiscuo activo | Canal: %d | Target BSSID: %s", current_channel, TARGET_BSSID);

    // Inicialización del stack Bluetooth BLE
    esp_bt_controller_config_t bt_cfg = BT_CONTROLLER_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_bt_controller_init(&bt_cfg));
    ESP_ERROR_CHECK(esp_bt_controller_enable(ESP_BT_MODE_BLE));
    ESP_ERROR_CHECK(esp_bluedroid_init());
    ESP_ERROR_CHECK(esp_bluedroid_enable());

    // Configura seguridad BLE
    setup_ble_security();

    // Registro de eventos BLE
    esp_ble_gap_register_callback(gap_event_handler);
    esp_ble_gatts_register_callback(gatts_event_handler);
    esp_ble_gatts_app_register(0);

    // Configuración de la publicidad BLE
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

    esp_ble_gap_config_adv_data(&adv_data);
    esp_ble_gap_start_advertising(&adv_params);

    // Bucle principal de espera
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000)); // Espera 1 segundo
    }
}
