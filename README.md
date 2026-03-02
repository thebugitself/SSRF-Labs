# SSRF Labs

A progressive Server-Side Request Forgery (SSRF) training lab with three difficulty levels, built with FastAPI and orchestrated via Docker Compose.

> **Disclaimer:** This lab is intended for **educational and authorized testing purposes only**. Do not use the techniques demonstrated here against systems you do not own or have explicit permission to test.

---

## Architecture

```
+-----------------+       +----------------------------------+
|   Your Browser  | ----> |  Docker Container  :8000         |
+-----------------+       |                                  |
                          |  web-app (FastAPI)               |
                          |    listening on 0.0.0.0:8000     |
                          |                                  |
                          |  internal-service (FastAPI)      |
                          |    listening on 127.0.0.1:80     |
                          |    /flag   /secret-data          |
                          +----------------------------------+
```

Both services run inside a **single container**. The internal admin service binds to `127.0.0.1:80`, making it completely unreachable from the host -- only the web application (running in the same container) can reach it via SSRF.

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) (v20+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2+)

---

## Quick Start

```bash
# Clone and enter the project
cd SSRF-Labs

# Build and start the lab
docker compose up --build -d

# Open the lab in your browser
# http://localhost:8000
```

To stop the lab:

```bash
docker compose down
```

---

## Project Structure

```
SSRF-Labs/
|-- app/
|   |-- Dockerfile
|   |-- main.py              # FastAPI vulnerable web application
|   |-- internal_app.py      # Internal admin service (SSRF target)
|   |-- start.sh             # Starts both services in one container
|   |-- requirements.txt
|   |-- templates/
|       |-- base.html         # Shared layout (Tailwind dark theme)
|       |-- index.html        # Landing page
|       |-- level.html        # Level page template
|
|-- internal/                 # Standalone version (not used in compose)
|   |-- Dockerfile
|   |-- main.py
|   |-- requirements.txt
|
|-- docker-compose.yml        # Single-container orchestration
|-- .dockerignore
|-- README.md                 # This file
|-- SOLUTION.md               # Detailed solutions for each level
```

---

## Challenge Overview

| Level | Difficulty | Protection | Goal |
|-------|-----------|-----------|------|
| 1 | Easy | None | Fetch `http://127.0.0.1/flag` directly |
| 2 | Medium | Keyword blacklist | Bypass the blacklist using alternative IP encodings |
| 3 | Hard | URL prefix whitelist | Abuse URL parser quirks to redirect to 127.0.0.1 |

---

## Troubleshooting

**Containers fail to start:**
```bash
docker compose logs -f
```

**Port 8000 already in use:**
```bash
docker compose down
# Change the port mapping in docker-compose.yml (e.g., "9000:8000")
docker compose up --build -d
```

**Rebuild from scratch:**
```bash
docker compose down --rmi all --volumes
docker compose up --build -d
```

---

## License

This project is provided as-is for educational purposes. No warranty is implied.
