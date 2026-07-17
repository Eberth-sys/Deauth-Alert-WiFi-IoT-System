//perception-layer\esp32-nodes-ino\ESP32_02_Deauth_Detector_CH_06\main.ino

// ------------------------------------------------------
// LIBRERÍAS NECESARIAS PARA CONECTIVIDAD Y SEGURIDAD
// ------------------------------------------------------

#include "WiFi.h"            // Funciones básicas de conexión Wi-Fi.
#include "esp_wifi.h"        // Acceso a funciones avanzadas (modo promiscuo, canal).
#include <BLEDevice.h>       // Inicializa el dispositivo BLE.
#include <BLEServer.h>       // Configura el servidor BLE.
#include <BLEUtils.h>        // Utilidades BLE (UUIDs, callbacks).
#include <BLESecurity.h>     // Configuración de seguridad BLE.
#include <wifi_mgmt_parser.h> // Parser portable de la cabecera 802.11 (biblioteca compartida, F4b)
#include <deauth_event.h>     // Modelo de evento POD + parser de BSSID (biblioteca compartida, F4c-1)
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"

// (F4d-1) Identidad canonica del nodo para el contrato de datos. Es DISTINTA del nombre BLE
// anunciado y de las etiquetas de log: debe coincidir con device['name'] de
// processing-layer/config/devices.yaml, que es la identidad operativa autoritativa (ligada a
// la MAC BLE de la conexion). F5 la emitira como campo "n" del JSON; ante discrepancia, la
// RPi conserva su identidad autoritativa y registra el desvio (ya implementado en F3).
#define NODE_ID "ESP32_2_CH_06"
// ble_manager.py rechaza un "n" vacio o de mas de _MAX_NODE_LEN (64) caracteres.
static_assert(sizeof(NODE_ID) > 1,
               "F4d-1: NODE_ID no puede estar vacio");
static_assert(sizeof(NODE_ID) - 1 <= 64,
               "F4d-1: NODE_ID excede _MAX_NODE_LEN (64) de ble_manager.py");


// ------------------------------------------------------
// 💡 CONFIGURACIÓN DEL ENTORNO DE DESARROLLO
// ------------------------------------------------------

/*
  📌 Si utilizas **Visual Studio Code con PlatformIO**:
  - Asegúrate de contar con el archivo `config.h`, donde debes definir el BSSID y los UUIDs reales.
  - Puedes usar el archivo `config_template.h` como referencia para crear `config.h`.

  📌 Si utilizas el **Arduino IDE**:
  - Comenta la línea `#include "config.h"`.
  - Descomenta las definiciones bajo el apartado "CONFIGURACIÓN MANUAL" y reemplaza con tus datos.
*/

// 📁 Carga de configuración desde archivo externo (solo para PlatformIO o VSCode con ESP-IDF):
#include "config.h"  // ❗⚠️ Comenta esta línea si estás usando Arduino IDE ⚠️ ❗

// ------------------------------------------------------
// 🛠️ CONFIGURACIÓN MANUAL PARA USUARIOS DEL ARDUINO IDE
// ------------------------------------------------------

/*
   🔧 Descomenta las siguientes líneas y completa los valores si usas Arduino IDE.
   ⚠️⚠️(Recuerda comentar `#include "config.h"` para evitar errores de compilación) ⚠️⚠️
*/

// #define TARGET_BSSID "XX:XX:XX:XX:XX:XX"              
// #define SERVICE_UUID "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  
// #define CHARACTERISTIC_UUID "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

// ------------------------------------------------------
//  INICIO DEL PROGRAMA
// ------------------------------------------------------

BLECharacteristic *pCharacteristic; // Característica BLE para enviar notificaciones
BLEServer *pServer;
bool deviceConnected = false;

// --- F4c-2: BSSID pre-parseado + cola estatica + worker + contador de descartes ---
static uint8_t targetBssid[6];

#define DEAUTH_WORKER_STACK_BYTES 4096
// Los toolchains fijados (ESP-IDF 5.1 / Arduino Core 3.2.0, Xtensa) definen StackType_t como
// uint8_t (1 byte); por eso sizeof(workerStack) == bytes de stack. Si cambiara, detener aqui.
static_assert(sizeof(StackType_t) == 1,
              "F4c-2 asume StackType_t de 1 byte; sizeof(workerStack) debe equivaler a los bytes de stack");

static uint8_t       queueStorage[DEAUTH_QUEUE_DEPTH * sizeof(deauth_event_t)];   // 16*20 = 320 B
static StaticQueue_t queueStatic;
static QueueHandle_t eventQueue = NULL;

static StackType_t   workerStack[DEAUTH_WORKER_STACK_BYTES / sizeof(StackType_t)];
static StaticTask_t  workerTcb;

// Contador de descartes: protegido con seccion critica portMUX (nunca solo volatile).
static portMUX_TYPE  droppedMux = portMUX_INITIALIZER_UNLOCKED;
static uint32_t      droppedEvents = 0;

// Estado BLE compartido (callbacks BLE <-> worker): deviceConnected.
static portMUX_TYPE  bleMux = portMUX_INITIALIZER_UNLOCKED;

// Variable global para el canal actual
const uint8_t MONITOR_CHANNEL = 6;

// El parseo/clasificacion de la cabecera 802.11 vive en la biblioteca compartida
// WifiMgmtParser (F4b, DT-04); ver wifi_mgmt_parse().

// Callback para manejar paquetes capturados
void sniffer_callback(void *buf, wifi_promiscuous_pkt_type_t type) {
    // (B) Solo tramas de management, antes de interpretar buf.
    if (type != WIFI_PKT_MGMT) return;

    const wifi_promiscuous_pkt_t *ppkt = (const wifi_promiscuous_pkt_t *)buf;

    // (A) Longitud real de la trama, descontando el FCS de 4 bytes.
    uint16_t sig_len = ppkt->rx_ctrl.sig_len;
    if (sig_len < 4) return;
    size_t frame_len = (size_t)sig_len - 4;
    if (frame_len < 24) return;   // cabecera MAC de management (data[0..23])

    // (orden seguro) Parseo portable de la cabecera; no se accede a data[] directamente.
    wifi_mgmt_frame_t frame;
    if (wifi_mgmt_parse(ppkt->payload, frame_len, &frame) != WIFI_MGMT_OK) return;
    if (frame.frame_subtype != 0x0C) return;   // solo deauth (0x0C); 0x0A queda reconocido sin alertar

    // BSSID objetivo: comparacion binaria de 6 bytes (sin snprintf/strcmp en el callback).
    if (memcmp(frame.addr2, targetBssid, 6) != 0) return;

    // Copiar el evento (mapeo DT-24: BSSID=addr2, src=addr3, dst=addr1) y encolar sin bloquear.
    deauth_event_t e;
    memcpy(e.bssid, frame.addr2, 6);
    memcpy(e.src,   frame.addr3, 6);
    memcpy(e.dst,   frame.addr1, 6);
    e.channel = ppkt->rx_ctrl.channel;   // (C) canal desde los metadatos de recepcion
    e.subtype = frame.frame_subtype;     // 0x0C

    if (xQueueSend(eventQueue, &e, 0) != pdTRUE) {
        // Cola llena: incrementar el contador de descartes en seccion critica minima.
        portENTER_CRITICAL(&droppedMux);
        droppedEvents++;
        portEXIT_CRITICAL(&droppedMux);
    }
}

// Formatea una MAC de 6 bytes a "XX:XX:XX:XX:XX:XX".
static void macToStr(const uint8_t mac[6], char out[18]) {
    snprintf(out, 18, "%02X:%02X:%02X:%02X:%02X:%02X",
             mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
}

// Reporte rate-limited (>= 5 s, wrap-safe) de descartes; lee+resetea en la misma seccion critica.
static void reportDropped(TickType_t* lastTick) {
    TickType_t now = xTaskGetTickCount();
    if ((TickType_t)(now - *lastTick) < pdMS_TO_TICKS(5000)) return;
    *lastTick = now;
    uint32_t d;
    portENTER_CRITICAL(&droppedMux);
    d = droppedEvents;
    droppedEvents = 0;
    portEXIT_CRITICAL(&droppedMux);
    if (d) Serial.printf("[WARN] Eventos descartados por cola llena en los ultimos 5 s: %u\n", (unsigned)d);
}

// Tarea worker: drena la cola y hace el trabajo lento (formateo, Serial, BLE). Conserva el texto actual.
static void deauthWorker(void* arg) {
    (void)arg;
    deauth_event_t e;
    TickType_t lastReport = xTaskGetTickCount();
    for (;;) {
        if (xQueueReceive(eventQueue, &e, pdMS_TO_TICKS(1000)) == pdTRUE) {
            char bssid[18], srcMac[18], destMac[18];
            macToStr(e.bssid, bssid);
            macToStr(e.src, srcMac);
            macToStr(e.dst, destMac);
            char mensaje[256];
            int n = snprintf(mensaje, sizeof(mensaje),
                             "[ALERT] Ataque de Deauthentication detectado | Origen: %s | Destino: %s | BSSID: %s | Canal: %d",
                             srcMac, destMac, bssid, e.channel);
            if (n < 0 || (size_t)n >= sizeof(mensaje)) {
                Serial.println("[WARN] no se pudo formatear la alerta");
            } else {
                Serial.println(mensaje);

                // Snapshot protegido de deviceConnected; el lock se libera ANTES de setValue/notify.
                bool conn;
                portENTER_CRITICAL(&bleMux);
                conn = deviceConnected;
                portEXIT_CRITICAL(&bleMux);

                if (conn) {
                    pCharacteristic->setValue(reinterpret_cast<uint8_t*>(mensaje), static_cast<size_t>(n));
                    pCharacteristic->notify();
                }
            }
        }
        reportDropped(&lastReport);
    }
}

// Clase para manejar eventos de conexión y desconexión BLE
class MyServerCallbacks : public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) override {
        portENTER_CRITICAL(&bleMux);
        deviceConnected = true;
        portEXIT_CRITICAL(&bleMux);
        Serial.println("[CONNECTED] Cliente BLE conectado.");
    }

    void onDisconnect(BLEServer* pServer) override {
        portENTER_CRITICAL(&bleMux);
        deviceConnected = false;
        portEXIT_CRITICAL(&bleMux);
        Serial.println("[DISCONNECTED] Cliente BLE desconectado.");
        BLEDevice::startAdvertising();  // Volver a anunciar el servidor BLE
    }
};

// Configuración de seguridad BLE
void setupSecurity() {
    BLESecurity *pSecurity = new BLESecurity();
    pSecurity->setAuthenticationMode(ESP_LE_AUTH_REQ_SC_MITM); // Secure Connections + MITM Protection
    pSecurity->setCapability(ESP_IO_CAP_NONE); // No requiere entrada manual de usuario
    pSecurity->setInitEncryptionKey(ESP_BLE_ENC_KEY_MASK | ESP_BLE_ID_KEY_MASK);
}

void setup() {
    Serial.begin(115200);
    Serial.printf("[INFO] node_id=%s\n", NODE_ID);   // (F4d-1) identidad canonica; ver devices.yaml
    
    // Configurar Wi-Fi en modo STA
    WiFi.mode(WIFI_MODE_STA);

    // (D) Configurar el filtro de management ANTES de habilitar el modo promiscuo.
    wifi_promiscuous_filter_t filter = {0};
    filter.filter_mask = WIFI_PROMIS_FILTER_MASK_MGMT;
    esp_err_t err = esp_wifi_set_promiscuous_filter(&filter);
    if (err != ESP_OK) { Serial.printf("[ERROR] esp_wifi_set_promiscuous_filter fallo (%d); se aborta setup\n", err); return; }
    // (F4c-2) Validar TARGET_BSSID, crear cola y worker ANTES de registrar el callback y
    // habilitar el modo promiscuo. Cualquier fallo impide activar la captura (sin fallback dinamico).
    if (!deauth_parse_bssid(TARGET_BSSID, targetBssid)) {
        Serial.println("[ERROR] TARGET_BSSID invalido; no se habilita la captura");
        return;
    }
    eventQueue = xQueueCreateStatic(DEAUTH_QUEUE_DEPTH, sizeof(deauth_event_t), queueStorage, &queueStatic);
    if (eventQueue == NULL) {
        Serial.println("[ERROR] xQueueCreateStatic fallo; no se habilita la captura");
        return;
    }
    if (xTaskCreateStatic(deauthWorker, "deauth_worker", sizeof(workerStack), NULL,
                          tskIDLE_PRIORITY + 1, workerStack, &workerTcb) == NULL) {
        Serial.println("[ERROR] xTaskCreateStatic fallo; no se habilita la captura");
        return;
    }

    err = esp_wifi_set_promiscuous_rx_cb(sniffer_callback);
    if (err != ESP_OK) { Serial.printf("[ERROR] esp_wifi_set_promiscuous_rx_cb fallo (%d); se aborta setup\n", err); return; }
    err = esp_wifi_set_channel(MONITOR_CHANNEL, WIFI_SECOND_CHAN_NONE);   // canal ANTES de habilitar
    if (err != ESP_OK) { Serial.printf("[ERROR] esp_wifi_set_channel fallo (%d); se aborta setup\n", err); return; }
    err = esp_wifi_set_promiscuous(true);                       // habilitar al final
    if (err != ESP_OK) { Serial.printf("[ERROR] esp_wifi_set_promiscuous fallo (%d); se aborta setup\n", err); return; }

    // Mensaje de inicio
    Serial.println(" ");
    Serial.printf("[INFO] Modo promiscuo activo | Canal: %d | Target BSSID: %s | Servidor BLE iniciado\n", MONITOR_CHANNEL, TARGET_BSSID);
    Serial.println(" ");

    // Configuración de BLE
    BLEDevice::init("ESP32_02_Deauth_Detector_CH_06");
    pServer = BLEDevice::createServer();
    pServer->setCallbacks(new MyServerCallbacks());

    // Crear servicio BLE
    BLEService *pService = pServer->createService(SERVICE_UUID);

    // Crear característica BLE
    pCharacteristic = pService->createCharacteristic(
        CHARACTERISTIC_UUID,
        BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_NOTIFY
    );

    // Configurar seguridad BLE
    setupSecurity();

    // Iniciar el servicio BLE
    pService->start();

    // Iniciar advertising BLE
    BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
    pAdvertising->start();

    Serial.println("[SECURE] BLE Seguro Iniciado. Esperando conexión...");
}

void loop() {
    // El análisis ocurre automáticamente en el callback sniffer_callback
}
