# processing-layer\src\utils\telegram_alert.py

# -------------------- Importaciones --------------------
import os                                # Para interactuar con el sistema operativo y acceder a variables de entorno
import requests                          # Para realizar peticiones HTTP
from dotenv import load_dotenv           # Para cargar variables de entorno desde un archivo .env

# Carga de variables de entorno desde un archivo .env
load_dotenv()

# -------------------- Carga de configuración desde el entorno --------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # Token del bot de Telegram, obtenido desde las variables de entorno
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # ID del chat de Telegram donde se enviarán los mensajes

# -------------------- Función para enviar mensajes a Telegram --------------------
def enviar_mensaje_telegram(mensaje: str):
    """Envía un mensaje de texto a Telegram usando la API del bot de Telegram."""
    
    # Verificación de que las configuraciones esenciales están presentes
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[ERROR] ❌ Faltan configuraciones de Telegram.")  # Mensaje de error si falta el token o chat ID
        return

    # Construcción de la URL para la API de Telegram
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    # Definición de los parámetros del mensaje
    data = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje  # El contenido del mensaje que será enviado
    }

    try:
        # Realiza una solicitud POST a la API de Telegram para enviar el mensaje
        response = requests.post(url, data=data)
        
        # Verificación de respuesta exitosa
        if response.status_code != 200:
            print(f"[ERROR] No se pudo enviar el mensaje: {response.text}")
    except Exception as e:
        # En caso de cualquier excepción durante la solicitud, se captura y muestra el error
        print(f"[ERROR] Fallo al enviar mensaje a Telegram: {e}")
