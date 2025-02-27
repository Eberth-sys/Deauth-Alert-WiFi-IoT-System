# src/data_processor.py

def process_data(device_name, data, timestamp):
    log_entry = f"[{timestamp}] {device_name}: {data}\n"
    with open('logs/ble_data.log', 'a') as log_file:
        log_file.write(log_entry)
    # print(f"[SAVED] Datos guardados en el log.")
