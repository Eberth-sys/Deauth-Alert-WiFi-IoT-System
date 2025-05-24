// perception-layer\esp32-nodes-ino\ESP32_03_Deauth_Detector_CH_11\config_template.h

#ifndef CONFIG_H
#define CONFIG_H

/*
 * ================================================
 * PLANTILLA DE CONFIGURACIÓN DEL NODO ESP32 (BLE)
 * ================================================
 * 
 * Este archivo contiene campos que deben completarse
 * antes de compilar el código en su entorno local.
 * 
 * Instrucciones:
 * 1. Copie este archivo como 'config.h' en la misma carpeta del .ino.
 * 2. Reemplace los valores de ejemplo por sus datos reales.
 * 3. NO suba 'config.h' al repositorio si contiene información sensible.
 */

// Dirección MAC (BSSID) de la red Wi-Fi que desea monitorear.
// Formato: "XX:XX:XX:XX:XX:XX"
#define TARGET_BSSID "XX:XX:XX:XX:XX:XX"

// UUID del servicio BLE del nodo.
// Formato estándar UUID: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
#define SERVICE_UUID "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

// UUID de la característica BLE.
// También debe seguir el formato UUID.
#define CHARACTERISTIC_UUID "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

#endif
