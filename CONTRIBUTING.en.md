> 🌐 **English** · **[Español](CONTRIBUTING.md)**

# Contributing guide

Thanks for your interest in **Deauth-Alert**! This project is an **academic prototype**
(final project of the IoT Specialization, FIUBA / UBA) released under the
**[Apache 2.0](LICENSE)** license. This guide explains how to contribute in an orderly and
responsible way.

## Purpose

To guide external contributions: which ones are accepted, how to propose them and which
workflow to follow, so the repository stays clear, secure and consistent with its
**educational and defensive** purpose.

## Welcome contributions

* 📖 **Documentation**: fixes, clarifications and translations (ES/EN).
* 🐞 **Bugs**: reproducible reports and their fixes.
* ⚙️ **Technical improvements**: refactors, performance and code quality.
* ✅ **Tests**: automated tests and edge cases.
* 🛰️ **Simulator**: improvements to the node simulator in `tools/` for validation without hardware.
* 🐳 **Deployment**: Docker / Compose, configuration and reproducibility.
* 🛡️ **Defensive security**: detection, hardening and robustness against invalid input.

## Contributions NOT accepted

Deauth-Alert is a **defensive and academic** project. Contributions that promote offensive,
illegal or unauthorized use of the tool will not be accepted.

Contributions will be rejected if they include:

* ❌ Exploitation of networks or systems without authorization.
* ❌ Instructions aimed at attacking third-party networks.
* ❌ Code, automation or *payloads* meant to run real attacks outside a controlled environment.
* ❌ Circumvention or *bypass* of security controls.
* ❌ Offensive or illegal content, or content that violates the privacy of others.

**Defensive testing** carried out on your own, authorized or lab environments **is accepted**
when clearly justified, as long as its purpose is to validate detection, improve security or
document the system's behavior.

Testing with auditing tools, such as those used in the project's **academic validation**, must
be presented only as controlled lab scenarios and never as guides for attacking third-party
networks.

## Workflow

The `main` branch is **protected**: all changes go through a *Pull Request*.

1. **Open an issue** that describes the bug or improvement (or outline the proposed change)
   before investing time in code.
2. **Fork** the repository and **create a descriptive branch** (`fix/…`, `docs/…`, `feat/…`, `chore/…`).
3. **Implement** the change following the style of the existing code.
4. **Validate locally** (see below).
5. **Open a PR** to `main` with a clear description (what, why and how you tested it) and link
   the issue.

This project uses **Conventional Commits** (`feat:`, `fix:`, `docs:`, `chore:`…).

## Recommended validations

Before opening the PR, validate according to what you changed:

**Frontend** (`frontend/`)

```bash
cd frontend
npm ci
npm run lint      # 0 errors
npm audit
npm run build
```

**Docker** (if you change images or `docker-compose.yml`)

```bash
docker compose build
```

**Backend / processing layer** (`backend/`, `processing-layer/`)

* Make sure the code compiles and respect the documented pinned versions (for example `bleak`
  and `paho-mqtt` in `processing-layer/requirements.txt`, which lock the API used with the
  ESP32 nodes and AWS IoT).
* You can validate without physical hardware using the **node simulator** in `tools/`.

## Reporting vulnerabilities

**Do not** report vulnerabilities in public issues. Follow the private process described in
[SECURITY.md](SECURITY.md#reportar-una-vulnerabilidad) (GitHub *Security Advisories* or private
contact with the author).

## Responsible use

Deauth-Alert puts Wi-Fi interfaces in promiscuous mode to **detect** attacks, not to run them.
By contributing, you agree that the project is used **only for legitimate, educational and
defensive purposes**, on your own or authorized networks. Responsibility for its use lies
solely with whoever runs it.

## License

By contributing, you agree that your contribution is distributed under the project's
**[Apache 2.0](LICENSE)** license.
