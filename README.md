# ElizaSOC — Intelligent Security Operations Platform

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)]()
[![Architecture](https://img.shields.io/badge/architecture-clean-green.svg)]()
[![Status](https://img.shields.io/badge/status-in%20development-yellow.svg)]()
[![Tests](https://img.shields.io/badge/tested%20with-pytest-orange.svg)]()

> 🇧🇷 **Versão em Português**: [README.pt-BR.md](README.pt-BR.md)

---

## Overview

**ElizaSOC** is an intelligent **Security Operations Center (SOC)** platform designed to detect, correlate, and respond to cybersecurity threats in real time. The system unifies **SIEM** (Security Information and Event Management) and **SOAR** (Security Orchestration, Automation, and Response) concepts into a single modular and extensible architecture.

The project is engineered with **Clean Architecture**, **SOLID principles**, and **Test-Driven Development (TDD)** to demonstrate production-grade software engineering practices applied to cybersecurity automation.

> ⚠️ **Project Status**: ElizaSOC is under **active development**. Core modules are functional, but persistence, authentication, and advanced integrations are part of the roadmap. See [Current Limitations](#current-limitations) and [Roadmap](#roadmap).

---

## Table of Contents

- [Demo](#demo)
- [Screenshots](#screenshots)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Technical Decisions](#technical-decisions)
- [System Workflow](#system-workflow)
- [Example Use Case](#example-use-case)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Module Status](#module-status)
- [Current Limitations](#current-limitations)
- [Roadmap](#roadmap)
- [Author](#author)
- [License](#license)

---

## Demo

[![ElizaSOC — Threat Detection and Response System](https://img.youtube.com/vi/fmdgvTvZxDI/0.jpg)](https://www.youtube.com/watch?v=fmdgvTvZxDI)

▶️ **Watch the demo**: [https://www.youtube.com/watch?v=fmdgvTvZxDI](https://www.youtube.com/watch?v=fmdgvTvZxDI)

---

## Screenshots

### Main Dashboard
![Main Dashboard](public/img/Captura%20de%20tela%20de%202025-11-04%2000-34-43.png)

### Real-Time Monitor
![Real-Time Monitor](public/img/Captura%20de%20tela%20de%202025-11-04%2000-38-07.png)

### Alerts and Metrics
![Alerts and Metrics](public/img/Captura%20de%20tela%20de%202025-11-04%2000-40-13.png)

### Protocol Analysis
![Protocol Analysis](public/img/Captura%20de%20tela%20de%202025-11-04%2000-41-46.png)

### Service Control
![Service Control](public/img/Captura%20de%20tela%20de%202025-11-04%2000-43-24.png)

### Interactive Charts
![Interactive Charts](public/img/Captura%20de%20tela%20de%202025-11-04%2000-45-18.png)

### Real-Time Logs
![Real-Time Logs](public/img/Captura%20de%20tela%20de%202025-11-04%2000-46-31.png)

### System Metrics
![System Metrics](public/img/Captura%20de%20tela%20de%202025-11-04%2000-47-53.png)

### Overview
![Overview](public/img/Captura%20de%20tela%20de%202025-11-04%2000-48-55.png)

---

## Key Features

### Real-Time Threat Detection
- Malware scanning via **ClamAV** integration
- Phishing and intrusion detection
- IOC (Indicators of Compromise) validation
- SHA-256 hash-based file identification

### Event Correlation (SIEM)
- Multi-event correlation by IP, domain, and hash
- Coordinated campaign detection
- Configurable time-window analysis
- Correlated alert generation

### Threat Intelligence Engine
- IOC enrichment and normalization
- Domain and URL canonicalization
- Extensible foundation for external feeds

### Behavioral Analysis
- Frequency-based anomaly detection
- Suspicious pattern recognition
- Optional ML-based detection via **Isolation Forest** (scikit-learn)
- Zero-day detection heuristics

### Automated Response (SOAR)
- IP blocking through **iptables**
- Domain blocking via `/etc/hosts`
- Automatic file quarantine
- Endpoint isolation hooks (extensible)

### Real-Time Monitoring Dashboard
- Live metrics with multi-line charts (Chart.js)
- Three concurrent metric streams: Alerts, Network, System
- 30-second refresh cycle
- Service controls for ClamAV and IDS
- Server-Sent Events (SSE) for live log streaming

### REST API
- Complete endpoints for alerts, scans, and system metrics
- Filtering, pagination, and statistics
- Real-time log streaming

---

## Architecture

ElizaSOC follows **Clean Architecture**, enforcing the **Dependency Rule**: dependencies always point inward, isolating the domain from frameworks, databases, and UI concerns.

```
┌─────────────────────────────────────────┐
│        Presentation Layer               │
│   (Controllers, REST API, Dashboard)    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│        Application Layer                │
│      (Use Cases, Orchestration)         │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Domain Layer (Core)             │
│      (Entities, Ports/Interfaces)       │
└──────────────▲──────────────────────────┘
               │
┌──────────────┴──────────────────────────┐
│       Infrastructure Layer              │
│   (Adapters, Concrete Implementations)  │
└─────────────────────────────────────────┘
```

### Layer Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Alerts     │  │    Files     │  │  Dashboard   │      │
│  │  Controller  │  │  Controller  │  │  Controller  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼───────────────┘
          │                 │                 │
┌─────────▼─────────────────▼─────────────────▼───────────────┐
│                    Application Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  ScanFile    │  │  Correlate   │  │   Analyze    │      │
│  │   UseCase    │  │   Events     │  │   Threat     │      │
│  │              │  │   UseCase    │  │   UseCase    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼───────────────┘
          │                 │                 │
┌─────────▼─────────────────▼─────────────────▼───────────────┐
│                      Domain Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Alert     │  │   FileScan   │  │   Security   │      │
│  │    Entity    │  │    Entity    │  │    Event     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Alert     │  │   FileScan   │  │    Event     │      │
│  │  Repository  │  │  Repository  │  │  Repository  │      │
│  │    (Port)    │  │    (Port)    │  │    (Port)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
          ▲                 ▲                 ▲
┌─────────┼─────────────────┼─────────────────┼───────────────┐
│                   Infrastructure Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   InMemory   │  │   InMemory   │  │    ClamAV    │      │
│  │    Alert     │  │   FileScan   │  │   Scanner    │      │
│  │  Repository  │  │  Repository  │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Event     │  │    Threat    │  │  Behavioral  │      │
│  │  Correlator  │  │ Intelligence │  │   Analyzer   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Entity-Relationship Model

```
┌──────────────┐
│    Alert     │
├──────────────┤
│ id (PK)      │
│ timestamp    │
│ signature    │
│ category     │
│ severity     │
│ src_ip       │
│ dest_ip      │
│ protocol     │
│ metadata     │
│ correlated   │
│ processed    │
└──────┬───────┘
       │ 1:N
┌──────▼──────────────┐
│   SecurityEvent     │
├─────────────────────┤
│ id (PK)             │
│ event_type          │
│ timestamp           │
│ source              │
│ data                │
│ related_events[]    │
│ processed           │
└──────┬──────────────┘
       │ N:1
┌──────▼──────────────┐
│  FileScanResult     │
├─────────────────────┤
│ id (PK)             │
│ filepath            │
│ filename            │
│ file_hash           │
│ file_size           │
│ status              │
│ threat_name         │
│ scanner             │
│ scan_time           │
│ quarantined         │
│ quarantine_path     │
└──────┬──────────────┘
       │ N:1
┌──────▼──────────────┐
│        IOC          │
├─────────────────────┤
│ id (PK)             │
│ ioc_type            │
│ value               │
│ source              │
│ threat_type         │
│ confidence          │
│ first_seen          │
│ last_seen           │
│ active              │
└─────────────────────┘
```

---

## Technical Decisions

This section documents the **engineering rationale** behind the project, useful for technical reviews and architectural discussions.

| Decision | Rationale |
|---------|-----------|
| **Clean Architecture** | Decouples business rules from frameworks (Flask, ClamAV, ML libraries), enabling independent evolution and easier testing. |
| **Ports & Adapters (Hexagonal)** | The domain defines interfaces (ports); infrastructure provides implementations. Swapping ClamAV for VirusTotal, for example, requires no changes to use cases. |
| **Test-Driven Development (TDD)** | Tests are written before implementation, guaranteeing high coverage and a domain that is testable by design. |
| **SOLID Principles** | Applied throughout: single-responsibility use cases, open/closed extension via new adapters, interface segregation across repositories. |
| **In-Memory Repositories (initial)** | Allow rapid prototyping and validation of the domain model without coupling to a specific database. Will be replaced with PostgreSQL/Elasticsearch adapters without touching the domain. |
| **Flask over Django** | Lightweight micro-framework fits the API-first approach; the project does not need Django's batteries (ORM, admin, templates) since persistence lives in the infrastructure layer. |
| **Server-Sent Events (SSE)** | Chosen over WebSockets for log streaming because the flow is unidirectional (server → client), simpler to implement, and works through standard HTTP infrastructure. |
| **Isolation Forest for anomalies** | Unsupervised algorithm well-suited for security data, where labeled examples are scarce and outliers are precisely what needs to be detected. |
| **ClamAV integration** | Mature, open-source, and broadly recognized engine; integration occurs via subprocess in the infrastructure layer, keeping the domain agnostic. |
| **iptables / `/etc/hosts` for response** | Native Linux mechanisms that require no additional services. The `ResponseService` interface allows future replacement with cloud firewalls or EDRs. |

---

## System Workflow

```
[Data Sources]
     ↓
[Event Ingestion]
     ↓
[Correlation Engine] ──→ [Threat Intelligence]
     ↓                          ↓
[Behavioral Analysis] ←─────────┘
     ↓
[Decision Engine]
     ↓
[Automated Response]
     ↓
[Dashboard & API]
```

---

## Example Use Case

**Brute-force attack detection and automated mitigation**

1. Multiple failed authentication events arrive from the same source IP.
2. The **Correlation Engine** groups these events within a configurable time window.
3. The **Threat Intelligence** module checks the IP against the IOC base.
4. The **Behavioral Analyzer** confirms the frequency anomaly.
5. The **Decision Engine** classifies the activity as malicious.
6. The **Response Service** automatically:
   - Blocks the IP via `iptables`
   - Generates a correlated alert
   - Logs the action for audit purposes
7. The **Dashboard** updates in real time via SSE.

---

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Backend** | Python 3.10+, Flask 3.0+ |
| **Security** | ClamAV, iptables |
| **Machine Learning** | scikit-learn (Isolation Forest) |
| **Frontend** | HTML5, JavaScript, Chart.js |
| **Streaming** | Server-Sent Events (SSE) |
| **Testing** | pytest, pytest-cov |
| **Production** | Gunicorn |

---

## Project Structure

```
ElizaSOC/
├── src/                          # Source code (Clean Architecture)
│   ├── domain/                   # Domain layer
│   │   ├── entities/             # Business entities
│   │   ├── ports/                # Interfaces (ports)
│   │   ├── repositories/         # Repository interfaces
│   │   └── services/             # Service interfaces
│   ├── application/              # Application layer
│   │   └── use_cases/            # Use cases
│   ├── infrastructure/           # Infrastructure layer
│   │   ├── scanners/             # ClamAV adapter
│   │   ├── repositories/         # Repository implementations
│   │   └── services/             # Service implementations
│   └── presentation/             # Presentation layer
│       └── api/                  # REST controllers
├── tests/                        # Automated tests
│   ├── domain/                   # Domain tests
│   ├── infrastructure/           # Infrastructure tests
│   └── integration/              # Integration tests
├── docs/                         # Full documentation
├── scripts/                      # Helper scripts
├── templates/                    # HTML templates
├── static/                       # Static assets (CSS, JS)
├── public/img/                   # Project screenshots
├── app.py                        # Application entry point
├── start.sh                      # Startup script
└── requirements.txt              # Python dependencies
```

---

## Installation

### Requirements
- Python 3.10+
- Linux (Ubuntu/Debian recommended)
- ClamAV (optional, for file scanning)
- scikit-learn (optional, for ML-based behavioral analysis)

### Quick Start

```bash
# 1. Clone the repository
git clone <repository-url> ElizaSOC
cd ElizaSOC

# 2. Install system dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv clamav

# 3. Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Update virus database (optional)
sudo freshclam

# 6. Start the system
./start.sh
```

The API will be available at: **http://localhost:5000**

### Running Modes

```bash
# Development
export FLASK_ENV=development
python3 app.py

# Production
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## API Reference

Base URL: `http://localhost:5000/api`

### System Status

#### `GET /api/status`
Returns system status.

```bash
curl http://localhost:5000/api/status
```

### Alerts

#### `GET /api/alerts`
List alerts with optional filters.

**Query parameters**:
- `limit` (int, default: 100) — maximum number of alerts
- `offset` (int, default: 0) — pagination
- `category` (string) — filter by category (`phishing`, `malware`, etc.)
- `severity` (int) — filter by severity (1–4)

```bash
curl "http://localhost:5000/api/alerts?limit=50&category=phishing"
```

#### `GET /api/alerts/{id}`
Retrieve a specific alert by ID.

#### `GET /api/alerts/stats`
Alert statistics.

```json
{
  "total": 1000,
  "phishing": 150,
  "malware": 50,
  "critical": 10,
  "timestamp": "2025-11-02T10:30:00"
}
```

#### `GET /api/alerts/phishing`
List phishing-only alerts.

#### `GET /api/alerts/recent`
List recent alerts.

### Files

#### `GET /api/files/scanned`
List scanned files (supports `limit` and `offset`).

#### `GET /api/files/infected`
List infected files only.

#### `POST /api/files/scan`
Scan a file.

**Body**:
```json
{
  "filepath": "/path/to/file.exe",
  "quarantine": true
}
```

**Response**:
```json
{
  "id": "scan-123",
  "filepath": "/tmp/suspicious.exe",
  "filename": "suspicious.exe",
  "status": "infected",
  "threat_name": "Trojan.Generic.123",
  "quarantined": true,
  "scan_time": "2025-11-02T10:30:00"
}
```

#### `GET /api/files/{scan_id}`
Retrieve scan result by ID.

### Dashboard

#### `GET /api/stats`
General system statistics.

#### `GET /api/phishing`
Phishing alerts for dashboard.

#### `GET /api/logs/stream`
Real-time log stream (Server-Sent Events).

#### `GET /api/protocols/{protocol}`
Statistics for a specific protocol (e.g., TCP, UDP).

### Web Dashboard

#### `GET /`
Web dashboard interface — open `http://localhost:5000` in a browser.

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test suites
pytest tests/domain/
pytest tests/integration/
```

The test suite is organized by architectural layer, reinforcing the project's adherence to Clean Architecture.

---

## Module Status

| Module | Status |
|--------|--------|
| File Analysis (ClamAV) | ✅ Complete |
| SIEM / Event Correlation | ✅ Complete |
| Threat Intelligence | 🟡 Functional (basic) |
| Behavioral Analysis | ✅ Complete |
| Automated Response | ✅ Complete |
| REST API | ✅ Complete |
| Web Dashboard | ✅ Complete |
| Persistent Storage | 🔴 Pending |
| Authentication / RBAC | 🔴 Pending |
| External Threat Feeds | 🔴 Pending |

---

## Current Limitations

This project is **under active development**. Known limitations include:

- **In-memory storage**: Repositories are non-persistent — data is lost between restarts. Persistent adapters are part of the roadmap.
- **No authentication**: The API and dashboard do not yet implement authentication or authorization. **Do not expose to public networks.**
- **Limited threat feeds**: Threat Intelligence works on local IOC bases; integration with external feeds (AbuseIPDB, VirusTotal, MISP) is planned.
- **Simplified ML models**: Behavioral analysis uses pre-trained models without a continuous training pipeline.
- **System-level operations**: Automated response interacts with `iptables` and `/etc/hosts`. Use with caution and review permissions before production deployment.

---

## Roadmap

- [ ] Persistent storage with **PostgreSQL** and **Elasticsearch**
- [ ] **JWT** authentication and **RBAC**
- [ ] Real-time ingestion from **Suricata** / **Zeek**
- [ ] Message broker (**RabbitMQ** / **Kafka**) for async processing
- [ ] External threat intelligence feeds (**AbuseIPDB**, **VirusTotal**, **MISP**)
- [ ] **Sandbox** for dynamic analysis
- [ ] **Honeypots**
- [ ] Containerization with **Docker** and orchestration with **Kubernetes**
- [ ] CI/CD pipeline with **GitHub Actions**
- [ ] Continuous training pipeline for ML models

---

## Documentation

Full documentation is available in the [`docs/`](docs/) folder:

- [`docs/README.md`](docs/README.md) — documentation index
- [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md) — system architecture
- [`docs/INSTALACAO.md`](docs/INSTALACAO.md) — detailed installation
- [`docs/USO.md`](docs/USO.md) — usage guide
- [`docs/QUICK_START.md`](docs/QUICK_START.md) — quick start
- [`docs/SECURITY.md`](docs/SECURITY.md) — security guidelines

---

## Contributing

This is a personal project under active development. Suggestions, code reviews, and architectural feedback are welcome via issues or pull requests.

---

## Author

**Wilker Junio Coelho Pimenta**

- 🔗 GitHub: [github.com/wilkernel](https://github.com/wilkernel)
- 💼 LinkedIn: [linkedin.com/in/wil-j-c-pimenta](https://linkedin.com/in/wil-j-c-pimenta)

---

## License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Built with ❤️ applying Clean Architecture, SOLID, and TDD.
</p>
