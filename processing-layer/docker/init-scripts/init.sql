-- init.sql

CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,               -- Identificador único de cada evento
    nodo_iot TEXT NOT NULL,              -- Primero el dispositivo que detectó el ataque
    spoofed_bssid VARCHAR(17) NOT NULL,  -- BSSID suplantado
    target_mac VARCHAR(17) NOT NULL,     -- MAC de destino del ataque
    bssid VARCHAR(17) NOT NULL,          -- BSSID original
    canal INT NOT NULL,                  -- Canal en el que se detectó el ataque
    event_type VARCHAR(16) NOT NULL DEFAULT 'deauth'
        CHECK (event_type IN ('deauth', 'disassoc')),  -- Tipo de evento 802.11 (F1, DEC-0003): deauth (0x0C) / disassoc (0x0A)
    timestamp TIMESTAMP DEFAULT NOW()    -- Momento del evento
);

-- Crear tabla para almacenar el estado de los ESP32
CREATE TABLE IF NOT EXISTS esp32_status (
    id SERIAL PRIMARY KEY,
    device_name TEXT UNIQUE NOT NULL,    -- Nombre único del ESP32
    mac_address VARCHAR(17) NOT NULL,    -- Dirección MAC del ESP32
    status TEXT CHECK (status IN ('connected', 'disconnected')) NOT NULL,  -- Estado actual
    last_update TIMESTAMP DEFAULT NOW()  -- Última actualización del estado
);

-- Crear un disparador para actualizar `last_update` automáticamente
CREATE OR REPLACE FUNCTION update_last_update_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_update = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_last_update
BEFORE UPDATE ON esp32_status
FOR EACH ROW
EXECUTE FUNCTION update_last_update_column();

-- Índices para mejorar la consulta rápida por nombre y MAC
CREATE INDEX IF NOT EXISTS idx_esp32_status_name ON esp32_status (device_name);
CREATE INDEX IF NOT EXISTS idx_esp32_status_mac ON esp32_status (mac_address);