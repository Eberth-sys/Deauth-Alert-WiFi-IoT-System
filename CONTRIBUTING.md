> 🌐 **[English](CONTRIBUTING.en.md)** · **Español**

# Guía de contribución

¡Gracias por tu interés en **Deauth-Alert**! Este proyecto es un **prototipo académico**
(trabajo final de la Especialización en IoT, FIUBA / UBA) publicado bajo licencia
**[Apache 2.0](LICENSE)**. Esta guía explica cómo colaborar de forma ordenada y responsable.

## Propósito

Orientar las contribuciones externas: qué aportes se aceptan, cómo proponerlos y qué flujo
seguir, para mantener el repositorio claro, seguro y coherente con su fin **educativo y
defensivo**.

## Contribuciones bienvenidas

* 📖 **Documentación**: correcciones, aclaraciones y traducciones (ES/EN).
* 🐞 **Errores**: reportes reproducibles y sus correcciones.
* ⚙️ **Mejoras técnicas**: refactorizaciones, rendimiento y calidad de código.
* ✅ **Pruebas**: automatizadas y casos de borde.
* 🛰️ **Simulador**: mejoras al simulador de nodos en `tools/` para validar sin hardware.
* 🐳 **Despliegue**: Docker / Compose, configuración y reproducibilidad.
* 🛡️ **Seguridad defensiva**: detección, endurecimiento y robustez ante entradas inválidas.

## Contribuciones NO aceptadas

Deauth-Alert es un proyecto **defensivo y académico**. No se aceptarán aportes que promuevan
el uso ofensivo, ilegal o no autorizado de la herramienta.

Se rechazarán contribuciones que incluyan:

* ❌ Explotación de redes o sistemas sin autorización.
* ❌ Instrucciones orientadas a atacar redes de terceros.
* ❌ Código, automatizaciones o *payloads* destinados a ejecutar ataques reales fuera de un
  entorno controlado.
* ❌ Evasión o *bypass* de controles de seguridad.
* ❌ Contenido ofensivo, ilegal o que vulnere la privacidad de terceros.

Sí se aceptan, cuando estén claramente justificadas, las **pruebas defensivas** realizadas en
entornos propios, autorizados o de laboratorio, siempre que su objetivo sea validar la
detección, mejorar la seguridad o documentar el comportamiento del sistema.

Las pruebas con herramientas de auditoría, como las usadas en la **validación académica** del
proyecto, deben presentarse únicamente como escenarios controlados de laboratorio y no como
guías para atacar redes ajenas.

## Flujo de trabajo

La rama `main` está **protegida**: todos los cambios entran por *Pull Request*.

1. **Abrí un issue** que describa el bug o la mejora (o comentá el cambio propuesto) antes de
   invertir tiempo en código.
2. **Hacé un fork** y **creá una rama** descriptiva (`fix/…`, `docs/…`, `feat/…`, `chore/…`).
3. **Implementá** el cambio según el estilo del código existente.
4. **Validá localmente** (ver abajo).
5. **Abrí un PR** hacia `main` con una descripción clara (qué, por qué y cómo lo probaste) y
   vinculá el issue.

Se usan **Conventional Commits** (`feat:`, `fix:`, `docs:`, `chore:`…).

## Validaciones recomendadas

Antes de abrir el PR, verificá según lo que hayas tocado:

**Frontend** (`frontend/`)

```bash
cd frontend
npm ci
npm run lint      # 0 errores
npm audit
npm run build
```

**Docker** (si modificás imágenes o `docker-compose.yml`)

```bash
docker compose build
```

**Backend / capa de procesamiento** (`backend/`, `processing-layer/`)

* Asegurate de que el código compile y respetá las versiones fijadas documentadas (por ejemplo `bleak`
  y `paho-mqtt` en `processing-layer/requirements.txt`, que fijan la API usada con los ESP32
  y AWS IoT).
* Podés validar sin hardware físico con el **simulador de nodos** de `tools/`.

## Reporte de vulnerabilidades

**No** reportes vulnerabilidades en issues públicos. Seguí el proceso privado descrito en
[SECURITY.md](SECURITY.md#reportar-una-vulnerabilidad) (GitHub *Security Advisories* o
contacto privado con el autor).

## Uso responsable

Deauth-Alert pone interfaces Wi-Fi en modo promiscuo para **detectar** ataques, no para
ejecutarlos. Al contribuir, aceptás que el proyecto se utilice **solo con fines legítimos,
educativos y defensivos**, sobre redes propias o autorizadas. La responsabilidad del uso
recae exclusivamente en quien lo ejecuta.

## Licencia

Al contribuir, aceptás que tu aporte se distribuya bajo la licencia
**[Apache 2.0](LICENSE)** del proyecto.
