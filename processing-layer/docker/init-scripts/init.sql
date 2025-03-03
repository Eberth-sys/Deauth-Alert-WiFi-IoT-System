-- init.sql

CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,               -- Identificador unico de cada evento
    nodo_iot TEXT NOT NULL,              -- Primero el dispositivo que detectó el ataque
    spoofed_bssid VARCHAR(17) NOT NULL,  -- BSSID suplantado
    target_mac VARCHAR(17) NOT NULL,     -- MAC de destino del ataque
    bssid VARCHAR(17) NOT NULL,          -- BSSID original
    canal INT NOT NULL,                  -- Canal en el que se detectó el ataque
    timestamp TIMESTAMP DEFAULT NOW()    -- Momento del evento
);
