# Política de Seguridad

## ⚠️ Uso autorizado

Este proyecto detecta ataques de deautenticación 802.11 poniendo interfaces Wi-Fi en **modo promiscuo**. Su uso está permitido **únicamente en redes de tu propiedad o donde cuentes con autorización explícita por escrito**. El monitoreo de tráfico de redes de terceros sin autorización puede constituir un delito según la legislación aplicable. El uso de esta herramienta es responsabilidad exclusiva de quien la ejecuta.

## Estado del proyecto

Este es un **prototipo académico** (trabajo de tesis), **no preparado para producción**. El backend aplica controles de autenticación: JWT en endpoints de usuario, acceso restringido a administrador para logs y rutas administrativas, autenticación de servicio mediante clave máquina a máquina para la ingesta de la capa de procesamiento, y validación JWT en el canal WebSocket antes de aceptar la conexión.

Aun así, antes de exponerlo en un entorno productivo, revise la configuración de despliegue: HTTPS/WSS, CORS y orígenes permitidos, rotación de secretos, variables de entorno, certificados, monitoreo, políticas de respaldo y endurecimiento del sistema operativo.

Ver el estado del proyecto en el [README](README.md#estado-del-proyecto).

## Reportar una vulnerabilidad

Si encontrás una vulnerabilidad de seguridad, por favor **no la publiques en un issue público**. En su lugar:

1. Usá la función de **avisos de seguridad privados** de GitHub (*Security Advisories*), o
2. Contactá al autor de forma privada a través del perfil de [LinkedIn](https://www.linkedin.com/in/eberthalarcon90) enlazado en el README.

Incluí, si es posible: descripción del problema, pasos para reproducirlo, impacto potencial y cualquier mitigación sugerida. Se responderá a la brevedad.

## Manejo de secretos

- Los archivos con datos sensibles (`.env`, certificados, `config.h` de los nodos, `devices.yaml`) **no se versionan**; se proveen plantillas (`.env.example`, `*_template.h`, `*.yaml.example`).
- No incluyas credenciales, tokens, claves ni identificadores reales (BSSID/MAC) en commits, issues o pull requests. Usá siempre valores de ejemplo o sintéticos.

## Buenas prácticas de despliegue

- Ejecutá el sistema en un entorno de laboratorio aislado hasta completar el endurecimiento de seguridad.
- Rotá cualquier credencial que haya podido quedar expuesta durante el desarrollo.
- Mantené las dependencias actualizadas.
