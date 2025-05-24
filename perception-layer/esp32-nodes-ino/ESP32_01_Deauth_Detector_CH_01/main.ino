//perception-layer\esp32-nodes-ino\ESP32_01_Deauth_Detector_CH_01\main.ino

#include "WiFi.h"
#include "esp_wifi.h"
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLESecurity.h>

// Carga la configuración personalizada del nodo (BSSID objetivo y UUIDs de BLE)
// Este archivo debe ser creado a partir de 'config_template.h'
#include "config.h"


BLECharacteristic *pCharacteristic; // Característica BLE para enviar notificaciones
BLEServer *pServer;
bool deviceConnected = false;

// Variable global para el canal actual
uint8_t currentChannel;

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
    const wifi_promiscuous_pkt_t *ppkt = (wifi_promiscuous_pkt_t *)buf;
    const uint8_t *data = ppkt->payload;

    // Extraer el BSSID del paquete
    char bssid[18];
    snprintf(bssid, sizeof(bssid), "%02X:%02X:%02X:%02X:%02X:%02X",
             data[10], data[11], data[12], data[13], data[14], data[15]);

    // Filtrar solo paquetes relacionados con el BSSID objetivo
    if (strcmp(bssid, TARGET_BSSID) == 0) {
        // Identificar tipo de paquete
        String packetType = getPacketType(data);

        // Mostrar solo paquetes de Deauthentication
        if (packetType == "Deauthentication") {
            // Extraer direcciones MAC de origen y destino
            char srcMac[18], destMac[18];
            snprintf(srcMac, sizeof(srcMac), "%02X:%02X:%02X:%02X:%02X:%02X",
                     data[16], data[17], data[18], data[19], data[20], data[21]);
            snprintf(destMac, sizeof(destMac), "%02X:%02X:%02X:%02X:%02X:%02X",
                     data[4], data[5], data[6], data[7], data[8], data[9]);

            // Obtener el canal actual
            wifi_second_chan_t secondChannel;
            esp_wifi_get_channel(&currentChannel, &secondChannel);

            // Preparar el mensaje con etiquetas mejoradas
            String mensaje = "[ALERT] Ataque de Deauthentication detectado | Origen: " + String(srcMac) +
                             " | Destino: " + String(destMac) + 
                             " | BSSID: " + String(bssid) +
                             " | Canal: " + String(currentChannel);
            Serial.println(mensaje);

            // Enviar el mensaje como notificación BLE si hay un cliente conectado
            if (deviceConnected) {
                pCharacteristic->setValue(mensaje.c_str());
                pCharacteristic->notify();
            }
        }
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
    
    // Inicializar el canal actual
    currentChannel = 1; //canal 1 

    // Configurar Wi-Fi en modo STA
    WiFi.mode(WIFI_MODE_STA);

    // Activar modo promiscuo
    esp_wifi_set_promiscuous(true);
    esp_wifi_set_promiscuous_rx_cb(sniffer_callback);

    // Configurar el ESP32 para escuchar en el canal inicial
    esp_wifi_set_channel(currentChannel, WIFI_SECOND_CHAN_NONE);

    // Mensaje de inicio
    Serial.println(" ");
    Serial.printf("[INFO] Modo promiscuo activo | Canal: %d | Target BSSID: %s | Servidor BLE iniciado\n", currentChannel, TARGET_BSSID);
    Serial.println(" ");

    // Configuración de BLE
    BLEDevice::init("ESP32_01_Deauth_Detector_CH_01");
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
