#!/usr/bin/env bash
# gen_config.sh — genera un config.h SINTETICO (valores ficticios; NUNCA reales)
# para el gate de compilacion de CI. No se versiona (config.h esta gitignored).
# Reduce duplicacion: lo usan los 3 jobs (Arduino, ESP-IDF, PlatformIO).
# Uso: gen_config.sh <ruta/al/config.h>
set -euo pipefail

dest="${1:?Uso: gen_config.sh <ruta/config.h>}"
mkdir -p "$(dirname "$dest")"

cat > "$dest" <<'EOF'
// config.h SINTETICO generado por CI (valores ficticios; NO reales). No versionar.
#ifndef CONFIG_H
#define CONFIG_H
#define TARGET_BSSID "AA:BB:CC:DD:EE:FF"
#define SERVICE_UUID "12345678-1234-1234-1234-1234567890ab"
#define CHARACTERISTIC_UUID "abcdef01-1234-1234-1234-1234567890ab"
#endif
EOF

echo "config.h sintetico generado en: $dest"
