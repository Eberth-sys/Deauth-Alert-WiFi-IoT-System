> 🌐 **English** · **[Español](SECURITY.md)**

# Security Policy

## ⚠️ Authorized use

This project detects 802.11 deauthentication attacks by putting Wi-Fi interfaces in **promiscuous mode**. Its use is permitted **only on networks you own or where you have explicit written authorization**. Monitoring third-party network traffic without authorization may be a crime under applicable law. Use of this tool is the sole responsibility of whoever runs it.

## Project status

This is an **academic prototype** (thesis work), **not production-ready**. The backend applies authentication controls: JWT on user endpoints, admin-only access to logs and administrative routes, machine-to-machine service authentication for processing-layer ingestion, and JWT validation on the WebSocket channel before accepting the connection.

Even so, before exposing it in a production environment, review the deployment configuration: HTTPS/WSS, CORS and allowed origins, secret rotation, environment variables, certificates, monitoring, backup policies and operating-system hardening.

See the project status in the [README](README.en.md#project-status).

## Supported Versions

As an academic prototype, only a single active line is maintained: security fixes are applied to the latest published release.

| Version | Supported |
| --- | --- |
| `1.0.x` (latest / `main`) | ✅ |
| Older versions | ❌ |

## Reporting a vulnerability

If you find a security vulnerability, please **do not disclose it in a public issue**. Instead:

1. Use GitHub's **private security advisories** feature (*Security Advisories*), or
2. Contact the author privately through the [LinkedIn](https://www.linkedin.com/in/eberthalarcon90) profile linked in the README.

If possible, include: a description of the problem, steps to reproduce it, potential impact and any suggested mitigation. The report will be reviewed as soon as possible.

## Handling secrets

- Files with sensitive data (`.env`, certificates, node `config.h`, `devices.yaml`) are **not versioned**; templates are provided instead (`.env.example`, `*_template.h`, `*.yaml.example`).
- Do not include real credentials, tokens, keys or identifiers (BSSID/MAC) in commits, issues or pull requests. Always use example or synthetic values.

## Deployment best practices

- Run the system in an isolated lab environment until security hardening is complete.
- Rotate any credential that may have been exposed during development.
- Keep dependencies up to date.
