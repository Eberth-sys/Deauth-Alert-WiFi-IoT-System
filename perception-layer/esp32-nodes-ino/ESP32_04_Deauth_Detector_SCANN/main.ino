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

// Función para identificar el tipo de paquete
String getPacketType(const uint8_t *data) {
    uint8_t type = (data[0] & 0x0C) >> 2; // Bits 2-3 para el tipo de paquete
    uint8_t subtype = (data[0] & 0xF0) >> 4; // Bits 4-7 para el subtipo

    if (type == 0) { // Paquetes de gestión
        switch (subtype) {
            case 0x0C: return "Deauthentication"; // Paquete de desautenticación
            default: return "Gestión (Otro)";
        }
    }
    return "Desconocido";
}

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

    const uint8_t *data = ppkt->payload;

    // (orden seguro) Verificar tipo/subtipo antes de leer direcciones.
    if (getPacketType(data) != "Deauthentication") return;   // solo deauth (0x0C)

    // BSSID objetivo (data[10..15]); tipo y longitud ya validados.
    char bssid[18];
    snprintf(bssid, sizeof(bssid), "%02X:%02X:%02X:%02X:%02X:%02X",
             data[10], data[11], data[12], data[13], data[14], data[15]);
    if (strcmp(bssid, TARGET_BSSID) != 0) return;

    char srcMac[18], destMac[18];
    snprintf(srcMac, sizeof(srcMac), "%02X:%02X:%02X:%02X:%02X:%02X",
             data[16], data[17], data[18], data[19], data[20], data[21]);
    snprintf(destMac, sizeof(destMac), "%02X:%02X:%02X:%02X:%02X:%02X",
             data[4], data[5], data[6], data[7], data[8], data[9]);

    // (C) Canal desde los metadatos de recepcion.
    String mensaje = "[ALERT] Ataque de Deauthentication detectado | Origen: " + String(srcMac) +
                     " | Destino: " + String(destMac) +
                     " | BSSID: " + String(bssid) +
                     " | Canal: " + String(ppkt->rx_ctrl.channel);
    Serial.println(mensaje);

    if (deviceConnected) {
        pCharacteristic->setValue(mensaje.c_str());
        pCharacteristic->notify();
    }
}

// Clase para manejar eventos de conexión y desconexión BLE
class MyServerCallbacks : public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) override {
        deviceConnected = true;
        Serial.println("[CONNECTED] Cliente BLE conectado.");
    }

    void onDisconnect(BLEServer* pServer) override {
        deviceConnected = false;
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

    // Configurar Wi-Fi en modo STA
    WiFi.mode(WIFI_MODE_STA);

    // (D) Configurar el filtro de management ANTES de habilitar el modo promiscuo.
    wifi_promiscuous_filter_t filter = {0};
    filter.filter_mask = WIFI_PROMIS_FILTER_MASK_MGMT;
    esp_err_t err = esp_wifi_set_promiscuous_filter(&filter);
    if (err != ESP_OK) { Serial.printf("[ERROR] esp_wifi_set_promiscuous_filter fallo (%d); se aborta setup\n", err); return; }
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
