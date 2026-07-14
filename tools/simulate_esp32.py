#!/usr/bin/env python3
"""
simulate_esp32.py - Simulador / validador de nodos ESP32 para Deauth-Alert.

Permite probar el sistema de punta a punta SIN el hardware fisico (nodos ESP32
+ Raspberry Pi). Reproduce lo que hace la capa de procesamiento cuando un nodo
ESP32 real detecta un ataque de desautenticacion: inserta la alerta en la tabla
`alerts` de PostgreSQL con las mismas columnas que
processing-layer/src/data_processor.py (funcion `guardar_alerta`). Ademas marca
los cuatro nodos como conectados en la tabla `esp32_status`.

Es una simulacion (mock) para demostracion y desarrollo: NO ejecuta un ataque
real ni emula el firmware ESP32 ni el transporte BLE; inyecta las alertas
directamente en la capa de datos. La deteccion frente a ataques reales de
desautenticacion se valido en laboratorio con hardware fisico.

Las direcciones MAC generadas son de EJEMPLO (prefijos DE:AD:BE:EF y 02:00:00);
no corresponden a hardware real.

Requisitos:
    - El web-stack de Docker levantado (ver la Opcion A del README principal).
    - psycopg2 disponible (pip install psycopg2-binary).

Configuracion de la base de datos por variables de entorno (las mismas que usa
la capa de procesamiento):
    PG_HOST (localhost)  PG_PORT (5432)  PG_DB (deauth_alerts)
    PG_USER              PG_PASSWORD

Uso (desde la raiz del repositorio):
    export PG_HOST=localhost PG_PORT=5432 PG_DB=deauth_alerts \\
           PG_USER=<usuario> PG_PASSWORD=<contrasena>
    python tools/simulate_esp32.py --count 10 --interval 2

Luego inicia sesion en el panel (http://localhost:8080) para ver las alertas.
"""
import argparse
import os
import random
import sys
import time

try:
    import psycopg2
except ImportError:
    sys.exit("[SIM] Falta psycopg2. Instala con: pip install psycopg2-binary")

# Nodos reales del sistema y el/los canal(es) Wi-Fi que vigila cada uno.
NODES = [
    ("ESP32_1_CH_01", [1]),
    ("ESP32_2_CH_06", [6]),
    ("ESP32_3_CH_11", [11]),
    ("ESP32_4_SCANN", [2, 3, 4, 5, 7, 8, 9, 10, 12, 13]),
]


def fake_ap_bssid():
    """BSSID de un punto de acceso de ejemplo (prefijo DE:AD:BE:EF, ficticio)."""
    return "DE:AD:BE:EF:%02X:%02X" % (random.randint(0, 255), random.randint(0, 255))


def fake_client_mac():
    """MAC de cliente de ejemplo (prefijo local 02:00:00, ficticia)."""
    return "02:00:00:%02X:%02X:%02X" % (
        random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def connect():
    """Abre la conexion a PostgreSQL usando las variables PG_* del entorno."""
    return psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=int(os.getenv("PG_PORT", "5432")),
        dbname=os.getenv("PG_DB", "deauth_alerts"),
        user=os.getenv("PG_USER", "postgres"),
        password=os.getenv("PG_PASSWORD", ""),
    )


def mark_nodes_connected(cur):
    """Marca los cuatro nodos como 'connected' para que el panel los muestre activos."""
    for name, _channels in NODES:
        cur.execute(
            """
            INSERT INTO esp32_status (device_name, mac_address, status, last_update)
            VALUES (%s, %s, 'connected', NOW())
            ON CONFLICT (device_name)
            DO UPDATE SET status = 'connected', last_update = NOW()
            """,
            (name, fake_client_mac()),
        )


def insert_alert(cur, ratio):
    """Inserta un evento de ejemplo. `ratio` = fraccion de disassoc (0.0-1.0).
    Devuelve sus datos, incluyendo event_type."""
    node, channels = random.choice(NODES)
    canal = random.choice(channels)
    bssid = fake_ap_bssid()            # BSSID legitimo del AP atacado
    spoofed_bssid = bssid              # el atacante suplanta ese mismo BSSID
    # ~70% broadcast (a todos los clientes), ~30% a un cliente concreto.
    target_mac = "FF:FF:FF:FF:FF:FF" if random.random() < 0.7 else fake_client_mac()
    # Tipo de evento 802.11 (F1, DEC-0003): ratio=0.0 => solo deauth; ratio=1.0 => solo disassoc.
    # random() devuelve [0.0, 1.0): con 0.0 nunca es disassoc; con 1.0 siempre es disassoc.
    event_type = "disassoc" if random.random() < ratio else "deauth"
    cur.execute(
        """
        INSERT INTO alerts (nodo_iot, spoofed_bssid, bssid, target_mac, canal, event_type, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """,
        (node, spoofed_bssid, bssid, target_mac, canal, event_type),
    )
    return node, canal, bssid, target_mac, event_type


def ratio_arg(value):
    """Valida --disassoc-ratio: numero flotante en el rango [0.0, 1.0]."""
    try:
        f = float(value)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError(
            "--disassoc-ratio debe ser un numero entre 0.0 y 1.0 (recibido: %r)" % value)
    if not 0.0 <= f <= 1.0:
        raise argparse.ArgumentTypeError(
            "--disassoc-ratio debe estar entre 0.0 y 1.0 (recibido: %s)" % f)
    return f


def main():
    parser = argparse.ArgumentParser(
        description="Simulador de nodos ESP32 para probar Deauth-Alert sin hardware.")
    parser.add_argument("--count", type=int, default=6,
                        help="numero de alertas a enviar (por defecto 6)")
    parser.add_argument("--interval", type=float, default=2.0,
                        help="segundos entre alertas (por defecto 2.0)")
    parser.add_argument("--disassoc-ratio", type=ratio_arg, default=0.2,
                        help="fraccion de eventos disassoc, 0.0-1.0 "
                             "(0.0=solo deauth, 1.0=solo disassoc; por defecto 0.2)")
    args = parser.parse_args()

    try:
        conn = connect()
    except psycopg2.OperationalError as exc:
        sys.exit("[SIM] No se pudo conectar a PostgreSQL: %s\n"
                 "      Revisa PG_HOST/PG_PORT/PG_DB/PG_USER/PG_PASSWORD." % exc)

    conn.autocommit = True
    cur = conn.cursor()

    mark_nodes_connected(cur)
    print("[SIM] %d nodos marcados como 'connected'." % len(NODES))
    print("[SIM] Enviando %d eventos (cada %ss, disassoc-ratio=%.2f)..."
          % (args.count, args.interval, args.disassoc_ratio))

    for i in range(1, args.count + 1):
        node, canal, bssid, target, ev = insert_alert(cur, args.disassoc_ratio)
        print("[SIM] %d/%d  nodo=%s  canal=%s  tipo=%s  BSSID=%s  destino=%s"
              % (i, args.count, node, canal, ev, bssid, target))
        if i < args.count:
            time.sleep(args.interval)

    cur.close()
    conn.close()
    print("[SIM] Listo. Abre el panel en http://localhost:8080 (o refrescalo).")


if __name__ == "__main__":
    main()
