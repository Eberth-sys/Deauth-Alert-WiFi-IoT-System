//perception-layer\ESP32_03_Deauth_Detector_CH_11\main\main.c

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

// Etiquetas únicas para este nodo (canal 11)
#define TAG "ESP32_03_CH11"  // Para logs específicos de este nodo
#define DEVICE_NAME "ESP32_03_Deauth_Detector_CH_11"  // Nombre visible en BLE

// Canal de escaneo: se fija al canal 11
static uint8_t current_channel = 11;

// Variables de estado de la conexión BLE
static bool device_connected = false;
static uint16_t conn_id = 0;
static esp_gatt_if_t gatts_if = ESP_GATT_IF_NONE;
static uint16_t char_handle;

// Definiciones para el servicio BLE
static esp_gatt_srvc_id_t service_id;
static esp_bt_uuid_t char_uuid = { .len = ESP_UUID_LEN_128 };

// Configuración de parámetros de publicidad BLE
static esp_ble_adv_params_t adv_params = {
    .adv_int_min = 0x20,  // Intervalo mínimo de advertising
    .adv_int_max = 0x40,  // Intervalo máximo de advertising
    .adv_type = ADV_TYPE_IND,  // Publicidad general
    .own_addr_type = BLE_ADDR_TYPE_PUBLIC,
    .channel_map = ADV_CHNL_ALL,
    .adv_filter_policy = ADV_FILTER_ALLOW_SCAN_ANY_CON_ANY,
};

// Convierte un UUID en cadena a su representación binaria de 128 bits
static void string_to_uuid(const char* uuid_str, uint8_t* uuid128) {
    char hex_str[33];
    int j = 0;
    for (int i = 0; i < strlen(uuid_str); i++) {
        if (uuid_str[i] != '-') {
            hex_str[j++] = uuid_str[i];
        }
    }
    hex_str[j] = '\0';

    for (int i = 0; i < 16; i++) {
        char byte_str[3] = { hex_str[30 - i*2], hex_str[31 - i*2], '\0' };
        uuid128[i] = (uint8_t)strtol(byte_str, NULL, 16);
    }
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

// Envia una alerta por BLE si se detecta un ataque de desautenticación
static void send_alert(const char* src_mac, const char* dest_mac, const char* bssid) {
    char alert_msg[256];
    wifi_second_chan_t second_chan;
    esp_wifi_get_channel(&current_channel, &second_chan);

    // Construcción del mensaje de alerta
    snprintf(alert_msg, sizeof(alert_msg),
             "[ALERT] Ataque de Deauthentication detectado | Origen: %s | Destino: %s | BSSID: %s | Canal: %d",
             src_mac, dest_mac, bssid, current_channel);

    // Log en consola
    printf("%s\n", alert_msg);
    ESP_LOGI(TAG, "%s", alert_msg);

    // Envío BLE si hay conexión activa
    if (device_connected) {
        esp_ble_gatts_send_indicate(gatts_if, conn_id, char_handle,
                                    strlen(alert_msg), (uint8_t*)alert_msg, false);
    }
}

// Función de callback llamada por cada paquete Wi-Fi recibido
static void wifi_sniffer_callback(void* buf, wifi_promiscuous_pkt_type_t type) {
    wifi_promiscuous_pkt_t* pkt = (wifi_promiscuous_pkt_t*)buf;
    uint8_t* data = pkt->payload;

    // Extracción del BSSID del paquete
    char bssid[18];
    snprintf(bssid, sizeof(bssid), "%02X:%02X:%02X:%02X:%02X:%02X",
             data[10], data[11], data[12], data[13], data[14], data[15]);

    // Comparación con el BSSID objetivo
    if (strcmp(bssid, TARGET_BSSID) == 0) {
        // Verifica si es un paquete de desautenticación
        uint8_t pkt_type = (data[0] & 0x0C) >> 2;
        uint8_t pkt_subtype = (data[0] & 0xF0) >> 4;

        if (pkt_type == 0 && pkt_subtype == 0x0C) {
            char src_mac[18], dst_mac[18];
            snprintf(src_mac, sizeof(src_mac), "%02X:%02X:%02X:%02X:%02X:%02X",
                     data[16], data[17], data[18], data[19], data[20], data[21]);
            snprintf(dst_mac, sizeof(dst_mac), "%02X:%02X:%02X:%02X:%02X:%02X",
                     data[4], data[5], data[6], data[7], data[8], data[9]);

            send_alert(src_mac, dst_mac, bssid); // Enviar alerta
        }
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
            string_to_uuid(SERVICE_UUID, service_id.id.uuid.uuid.uuid128);
            esp_ble_gatts_create_service(gatt_if, &service_id, 4);
            break;

        case ESP_GATTS_CREATE_EVT:
            ESP_LOGI(TAG, "Servicio creado");
            esp_ble_gatts_start_service(param->create.service_handle);
            string_to_uuid(CHARACTERISTIC_UUID, char_uuid.uuid.uuid128);
            esp_ble_gatts_add_char(param->create.service_handle, &char_uuid,
                                   ESP_GATT_PERM_READ,
                                   ESP_GATT_CHAR_PROP_BIT_READ | ESP_GATT_CHAR_PROP_BIT_NOTIFY,
                                   NULL, NULL);
            break;

        case ESP_GATTS_ADD_CHAR_EVT:
            char_handle = param->add_char.attr_handle;
            ESP_LOGI(TAG, "Característica BLE creada. Handle: %d", char_handle);
            break;

        case ESP_GATTS_CONNECT_EVT:
            device_connected = true;
            conn_id = param->connect.conn_id;
            gatts_if = gatt_if;
            ESP_LOGI(TAG, "Dispositivo conectado por BLE");
            break;

        case ESP_GATTS_DISCONNECT_EVT:
            device_connected = false;
            ESP_LOGI(TAG, "Dispositivo desconectado por BLE");
            esp_ble_gap_start_advertising(&adv_params);
            break;

        default:
            break;
    }
}

// Función principal del programa (punto de entrada)
void app_main() {
    // Inicialización de almacenamiento no volátil y sistema de eventos
    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    // Configuración del Wi-Fi en modo promiscuo
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_start());
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous(true));
    ESP_ERROR_CHECK(esp_wifi_set_promiscuous_rx_cb(wifi_sniffer_callback));
    ESP_ERROR_CHECK(esp_wifi_set_channel(current_channel, WIFI_SECOND_CHAN_NONE));

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
