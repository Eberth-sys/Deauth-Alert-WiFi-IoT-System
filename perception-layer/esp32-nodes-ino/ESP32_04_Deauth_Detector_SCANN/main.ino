//perception-layer\esp32-nodes-ino\ESP32_04_Deauth_Detector_SCANN\main.ino

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
#include <deauth_json.h>      // Serializador del contrato JSON v1 (biblioteca compartida, F5-1)
#include <deauth_ratelimit.h> // Rate-limit compartido de alertas (biblioteca compartida, F5-3)
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"

// (F4d-1) Identidad canonica del nodo para el contrato de datos. Es DISTINTA del nombre BLE
// anunciado y de las etiquetas de log: debe coincidir con device['name'] de
// processing-layer/config/devices.yaml, que es la identidad operativa autoritativa (ligada a
// la MAC BLE de la conexion). F5 la emitira como campo "n" del JSON; ante discrepancia, la
// RPi conserva su identidad autoritativa y registra el desvio (ya implementado en F3).
#define NODE_ID "ESP32_4_SCANN"
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

// Configuración de canales Wi-Fi
#define FIRST_CHANNEL 1
#define LAST_CHANNEL 13
#define DWELL_TIME_MS 2000 // Tiempo de permanencia en cada canal (ms)

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

// --- F4d-2: MTU BLE por conexion + descartes por MTU ---
#define DEAUTH_LOCAL_MTU 247   // MTU local maximo a solicitar (<= 517)
// negotiatedMtu y activeConnId son estado protegido por bleMux (junto con deviceConnected). El worker
// solo copia deviceConnected + negotiatedMtu; activeConnId se usa para correlacionar los callbacks.
static uint16_t      negotiatedMtu = 23;   // MTU efectivo; arranca en el default hasta negociar
static uint16_t      activeConnId  = 0;
// Descartes por payload > capacidad del MTU: contador SEPARADO de droppedEvents, con su PROPIA
// seccion critica (nunca anidar con bleMux ni con droppedMux).
static portMUX_TYPE  mtuMux = portMUX_INITIALIZER_UNLOCKED;
static uint32_t      droppedMtu = 0;
static uint16_t      droppedMtuLast = 0;   // MTU vigente en el ultimo descarte (para el reporte)

// (F5-3) Rate-limit de alertas por (dst, subtype): instancia + contadores WORKER-ONLY (sin portMUX;
// solo la tarea worker los toca). rateLimitedSuppressed = duplicados; rateLimitFailOpen = tabla llena.
static deauth_rate_limiter_t rateLimiter;
static uint32_t      rateLimitedSuppressed = 0;
static uint32_t      rateLimitFailOpen = 0;

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
    if (frame.frame_subtype != 0x0C && frame.frame_subtype != 0x0A) return;   // deauth (0x0C) y disassoc (0x0A)

    // BSSID objetivo: comparacion binaria de 6 bytes (sin snprintf/strcmp en el callback).
    if (memcmp(frame.addr2, targetBssid, 6) != 0) return;

    // Copiar el evento (mapeo DT-24: BSSID=addr2, src=addr3, dst=addr1) y encolar sin bloquear.
    deauth_event_t e;
    memcpy(e.bssid, frame.addr2, 6);
    memcpy(e.src,   frame.addr3, 6);
    memcpy(e.dst,   frame.addr1, 6);
    e.channel = ppkt->rx_ctrl.channel;   // (C) canal desde los metadatos de recepcion
    e.subtype = frame.frame_subtype;     // 0x0C (deauth) o 0x0A (disassoc)

    if (xQueueSend(eventQueue, &e, 0) != pdTRUE) {
        // Cola llena: incrementar el contador de descartes en seccion critica minima.
        portENTER_CRITICAL(&droppedMux);
        droppedEvents++;
        portEXIT_CRITICAL(&droppedMux);
    }
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

// (F4d-2) Reporte rate-limited (>= 5 s, wrap-safe) de descartes por MTU insuficiente. Mismo patron
// que reportDropped; sin logs por evento. Incluye cantidad, MTU y capacidad util.
static void reportMtuDropped(TickType_t* lastTick) {
    TickType_t now = xTaskGetTickCount();
    if ((TickType_t)(now - *lastTick) < pdMS_TO_TICKS(5000)) return;
    *lastTick = now;
    uint32_t d;
    uint16_t m;
    portENTER_CRITICAL(&mtuMux);
    d = droppedMtu;
    m = droppedMtuLast;
    droppedMtu = 0;
    portEXIT_CRITICAL(&mtuMux);
    if (d) {
        uint16_t cap = (m >= 3) ? (uint16_t)(m - 3) : 0;
        Serial.printf("[WARN] Alertas descartadas por MTU insuficiente en los ultimos 5 s: %u (MTU=%u, capacidad util=%u B)\n",
                      (unsigned)d, (unsigned)m, (unsigned)cap);
    }
}

// (F5-3) Reporte rate-limited (>= 5 s, wrap-safe) de duplicados suprimidos y de fail-open por tabla
// llena. Contadores WORKER-ONLY (sin seccion critica). Sin logs por evento; solo si el contador > 0.
static void reportRateLimited(TickType_t* lastTick) {
    TickType_t now = xTaskGetTickCount();
    if ((TickType_t)(now - *lastTick) < pdMS_TO_TICKS(5000)) return;
    *lastTick = now;
    if (rateLimitedSuppressed) {
        Serial.printf("[WARN] Alertas duplicadas suprimidas por rate-limit en los ultimos 5 s: %u\n",
                      (unsigned)rateLimitedSuppressed);
        rateLimitedSuppressed = 0;
    }
    if (rateLimitFailOpen) {
        Serial.printf("[WARN] Fail-open del rate-limit (tabla llena) en los ultimos 5 s: %u\n",
                      (unsigned)rateLimitFailOpen);
        rateLimitFailOpen = 0;
    }
}

// Tarea worker: drena la cola y hace el trabajo lento (formateo, Serial, BLE). Conserva el texto actual.
static void deauthWorker(void* arg) {
    (void)arg;
    deauth_event_t e;
    TickType_t lastReport = xTaskGetTickCount();
    TickType_t lastMtuReport = lastReport;
    TickType_t lastRlReport = lastReport;
    deauth_ratelimit_init(&rateLimiter);   // (F5-3) instancia explicita, sin estado global oculto
    for (;;) {
        if (xQueueReceive(eventQueue, &e, pdMS_TO_TICKS(1000)) == pdTRUE) {
            // (F5-3) Rate-limit por (dst, subtype) ANTES de serializar/emitir. if(allow) (no continue):
            // los reportes periodicos de abajo (fuera de xQueueReceive) corren siempre, aun al suprimir.
            deauth_rl_result_t rlRes = deauth_ratelimit_check(&rateLimiter, e.dst, e.subtype,
                                                              (uint32_t)xTaskGetTickCount(), pdMS_TO_TICKS(1000));
            if (rlRes == DEAUTH_RL_SUPPRESS) {
                rateLimitedSuppressed++;   // duplicado dentro de la ventana: no serializa ni emite
            } else {
                if (rlRes == DEAUTH_RL_ALLOW_FULL) rateLimitFailOpen++;   // tabla llena: fail-open observable
                char mensaje[DEAUTH_JSON_BUFFER_SIZE];
                int n = deauth_json_serialize(&e, NODE_ID, mensaje, sizeof(mensaje));
                if (n < 0 || (size_t)n >= sizeof(mensaje)) {
                    Serial.println("[WARN] no se pudo serializar la alerta JSON");
                } else {
                    Serial.println(mensaje);   // (F5) diagnostico: el MISMO JSON v1 que se envia por BLE

                    // Snapshot protegido de deviceConnected y MTU; el lock se libera ANTES de setValue/notify.
                    bool conn;
                    uint16_t mtu;
                    portENTER_CRITICAL(&bleMux);
                    conn = deviceConnected;
                    mtu  = negotiatedMtu;
                    portEXIT_CRITICAL(&bleMux);

                    if (conn) {
                        // (F4d-2) Capacidad util de una notificacion = MTU negociado - 3 (cabecera ATT).
                        size_t capacity = (mtu >= 3) ? (size_t)(mtu - 3) : 0;
                        if ((size_t)n > capacity) {
                            // No cabe: NO truncar, NO enviar. Contar en seccion critica independiente
                            // (bleMux ya liberado; nunca anidar con bleMux/droppedMux).
                            portENTER_CRITICAL(&mtuMux);
                            droppedMtu++;
                            droppedMtuLast = mtu;
                            portEXIT_CRITICAL(&mtuMux);
                        } else {
                            pCharacteristic->setValue(reinterpret_cast<uint8_t*>(mensaje), static_cast<size_t>(n));
                            pCharacteristic->notify();
                        }
                    }
                }
            }
        }
        reportDropped(&lastReport);
        reportMtuDropped(&lastMtuReport);
        reportRateLimited(&lastRlReport);
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

    // (F4d-2) Overloads de 2 argumentos: traen esp_ble_gatts_cb_param_t (conn_id / MTU). El core
    // invoca ambos overloads; los de 1 argumento de arriba mantienen deviceConnected/advertising.
    void onConnect(BLEServer* pServer, esp_ble_gatts_cb_param_t* param) override {
        portENTER_CRITICAL(&bleMux);
        activeConnId  = param->connect.conn_id;
        negotiatedMtu = 23;                 // MTU efectivo arranca en el default hasta negociar
        portEXIT_CRITICAL(&bleMux);
    }

    void onDisconnect(BLEServer* pServer, esp_ble_gatts_cb_param_t* param) override {
        portENTER_CRITICAL(&bleMux);
        // Restablecer a 23 con la misma condicion de conn_id que la actualizacion.
        if (param->disconnect.conn_id == activeConnId) {
            negotiatedMtu = 23;
        }
        portEXIT_CRITICAL(&bleMux);
    }

    void onMtuChanged(BLEServer* pServer, esp_ble_gatts_cb_param_t* param) override {
        bool mtuAccepted;
        portENTER_CRITICAL(&bleMux);
        // Actualizar solo si el evento corresponde a la conexion activa.
        mtuAccepted = (deviceConnected && param->mtu.conn_id == activeConnId);
        if (mtuAccepted) {
            negotiatedMtu = param->mtu.mtu;
        }
        portEXIT_CRITICAL(&bleMux);
        if (mtuAccepted) {
            // Observabilidad (una sola linea, FUERA del lock): evidencia de la negociacion real.
            uint16_t cap = (param->mtu.mtu >= 3) ? (uint16_t)(param->mtu.mtu - 3) : 0;
            Serial.printf("[INFO] ble_mtu_negotiated=%u conn_id=%u capacity=%u\n",
                          (unsigned)param->mtu.mtu, (unsigned)param->mtu.conn_id, (unsigned)cap);
        }
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
    err = esp_wifi_set_channel(FIRST_CHANNEL, WIFI_SECOND_CHAN_NONE);   // canal inicial ANTES de habilitar
    if (err != ESP_OK) { Serial.printf("[ERROR] esp_wifi_set_channel fallo (%d); se aborta setup\n", err); return; }
    err = esp_wifi_set_promiscuous(true);                       // habilitar al final
    if (err != ESP_OK) { Serial.printf("[ERROR] esp_wifi_set_promiscuous fallo (%d); se aborta setup\n", err); return; }

    // Mostrar mensaje inicial con canales configurados y BSSID objetivo
    Serial.printf("[INFO] Modo promiscuo activo | Canales: 2, 3, 4, 5, 7, 8, 9, 10, 12, 13 | Target BSSID: %s | Servidor BLE iniciado\n", TARGET_BSSID);

    // Configuración de BLE
    BLEDevice::init("ESP32_Channel_Scanner");
    // (F4d-2) Solicitar el MTU local maximo acordable (247), tras BLEDevice::init y antes de crear
    // el servidor/advertising. Solo declara nuestro maximo; el efectivo lo fija la negociacion.
    {
        esp_err_t mtuErr = BLEDevice::setMTU(DEAUTH_LOCAL_MTU);
        if (mtuErr != ESP_OK) {
            Serial.printf("[WARN] BLEDevice::setMTU(%u) fallo (%d); el MTU efectivo puede quedar en 23\n",
                          (unsigned)DEAUTH_LOCAL_MTU, mtuErr);
        }
    }
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
    // Iterar por los canales Wi-Fi, excluyendo los canales 1, 6 y 11
    for (int channel = FIRST_CHANNEL; channel <= LAST_CHANNEL; channel++) {
        if (channel == 1 || channel == 6 || channel == 11) {
            continue; // Saltar estos canales
        }

        // Configurar el ESP32 para escuchar en el canal actual
        esp_wifi_set_channel(channel, WIFI_SECOND_CHAN_NONE);

        // Mostrar canal actual en la salida serie
        Serial.printf("[SCANNING] Escuchando en canal: %d\n", channel);

        // Esperar un tiempo en este canal para capturar paquetes
        delay(DWELL_TIME_MS);
    }
}
