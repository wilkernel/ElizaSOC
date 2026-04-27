# ElizaSOC — Plataforma Inteligente de Operações de Segurança

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)]()
[![Architecture](https://img.shields.io/badge/architecture-clean-green.svg)]()
[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow.svg)]()
[![Tests](https://img.shields.io/badge/tested%20with-pytest-orange.svg)]()

> 🇺🇸 **English version**: [README.md](README.md)

---

## Visão Geral

O **ElizaSOC** é uma plataforma inteligente de **Security Operations Center (SOC)** projetada para detectar, correlacionar e responder a ameaças cibernéticas em tempo real. O sistema unifica conceitos de **SIEM** (Security Information and Event Management) e **SOAR** (Security Orchestration, Automation, and Response) em uma arquitetura única, modular e extensível.

O projeto é construído com **Clean Architecture**, princípios **SOLID** e **Test-Driven Development (TDD)** para demonstrar boas práticas de engenharia de software aplicadas à automação de cibersegurança.

> ⚠️ **Status do Projeto**: O ElizaSOC está em **desenvolvimento ativo**. Os módulos principais estão funcionais, mas persistência, autenticação e integrações avançadas fazem parte do roadmap. Veja [Limitações Atuais](#limitações-atuais) e [Roadmap](#roadmap).

---

## Sumário

- [Demonstração](#demonstração)
- [Capturas de Tela](#capturas-de-tela)
- [Principais Funcionalidades](#principais-funcionalidades)
- [Arquitetura](#arquitetura)
- [Decisões Técnicas](#decisões-técnicas)
- [Fluxo do Sistema](#fluxo-do-sistema)
- [Caso de Uso de Exemplo](#caso-de-uso-de-exemplo)
- [Stack Tecnológica](#stack-tecnológica)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação](#instalação)
- [Referência da API](#referência-da-api)
- [Testes](#testes)
- [Status dos Módulos](#status-dos-módulos)
- [Limitações Atuais](#limitações-atuais)
- [Roadmap](#roadmap)
- [Autor](#autor)
- [Licença](#licença)

---

## Demonstração

[![ElizaSOC — Sistema de Detecção e Resposta a Ameaças](https://img.youtube.com/vi/fmdgvTvZxDI/0.jpg)](https://www.youtube.com/watch?v=fmdgvTvZxDI)

▶️ **Assista ao vídeo**: [https://www.youtube.com/watch?v=fmdgvTvZxDI](https://www.youtube.com/watch?v=fmdgvTvZxDI)

---

## Capturas de Tela

### Dashboard Principal
![Dashboard Principal](public/img/Captura%20de%20tela%20de%202025-11-04%2000-34-43.png)

### Monitor em Tempo Real
![Monitor em Tempo Real](public/img/Captura%20de%20tela%20de%202025-11-04%2000-38-07.png)

### Alertas e Métricas
![Alertas e Métricas](public/img/Captura%20de%20tela%20de%202025-11-04%2000-40-13.png)

### Análise de Protocolos
![Análise de Protocolos](public/img/Captura%20de%20tela%20de%202025-11-04%2000-41-46.png)

### Controle de Serviços
![Controle de Serviços](public/img/Captura%20de%20tela%20de%202025-11-04%2000-43-24.png)

### Gráficos Interativos
![Gráficos Interativos](public/img/Captura%20de%20tela%20de%202025-11-04%2000-45-18.png)

### Logs em Tempo Real
![Logs em Tempo Real](public/img/Captura%20de%20tela%20de%202025-11-04%2000-46-31.png)

### Métricas do Sistema
![Métricas do Sistema](public/img/Captura%20de%20tela%20de%202025-11-04%2000-47-53.png)

### Visão Geral
![Visão Geral](public/img/Captura%20de%20tela%20de%202025-11-04%2000-48-55.png)

---

## Principais Funcionalidades

### Detecção de Ameaças em Tempo Real
- Escaneamento de malwares via integração com **ClamAV**
- Detecção de phishing e intrusões
- Validação de IOCs (Indicators of Compromise)
- Identificação de arquivos por hash SHA-256

### Correlação de Eventos (SIEM)
- Correlação multi-evento por IP, domínio e hash
- Detecção de campanhas coordenadas
- Análise de janelas de tempo configuráveis
- Geração de alertas correlacionados

### Threat Intelligence
- Enriquecimento e normalização de IOCs
- Canonicalização de domínios e URLs
- Base extensível para integração com feeds externos

### Análise Comportamental
- Detecção de anomalias por frequência
- Reconhecimento de padrões suspeitos
- Detecção opcional baseada em ML via **Isolation Forest** (scikit-learn)
- Heurísticas para detecção de zero-day

### Resposta Automatizada (SOAR)
- Bloqueio de IPs via **iptables**
- Bloqueio de domínios via `/etc/hosts`
- Quarentena automática de arquivos
- Hooks para isolamento de endpoints (extensível)

### Dashboard de Monitoramento em Tempo Real
- Métricas ao vivo com gráficos multi-linha (Chart.js)
- Três fluxos de métricas simultâneos: Alertas, Rede, Sistema
- Atualização a cada 30 segundos
- Controle de serviços para ClamAV e IDS
- Streaming de logs via Server-Sent Events (SSE)

### API REST
- Endpoints completos para alertas, escaneamentos e métricas do sistema
- Filtros, paginação e estatísticas
- Streaming de logs em tempo real

---

## Arquitetura

O ElizaSOC segue a **Clean Architecture**, aplicando a **Regra de Dependência**: as dependências sempre apontam para dentro, isolando o domínio de frameworks, bancos de dados e questões de UI.

```
┌─────────────────────────────────────────┐
│       Camada de Apresentação            │
│  (Controllers, API REST, Dashboard)     │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│        Camada de Aplicação              │
│      (Casos de Uso, Orquestração)       │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Camada de Domínio (Core)           │
│    (Entidades, Portas/Interfaces)       │
└──────────────▲──────────────────────────┘
               │
┌──────────────┴──────────────────────────┐
│      Camada de Infraestrutura           │
│  (Adaptadores, Implementações Concretas)│
└─────────────────────────────────────────┘
```

### Diagrama de Camadas

```
┌─────────────────────────────────────────────────────────────┐
│                  Camada de Apresentação                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Alerts     │  │    Files     │  │  Dashboard   │      │
│  │  Controller  │  │  Controller  │  │  Controller  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼───────────────┘
          │                 │                 │
┌─────────▼─────────────────▼─────────────────▼───────────────┐
│                   Camada de Aplicação                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  ScanFile    │  │  Correlate   │  │   Analyze    │      │
│  │   UseCase    │  │   Events     │  │   Threat     │      │
│  │              │  │   UseCase    │  │   UseCase    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼─────────────────┼─────────────────┼───────────────┘
          │                 │                 │
┌─────────▼─────────────────▼─────────────────▼───────────────┐
│                    Camada de Domínio                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Alert     │  │   FileScan   │  │   Security   │      │
│  │   Entity     │  │    Entity    │  │    Event     │      │
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
│                  Camada de Infraestrutura                    │
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

### Modelo Entidade-Relacionamento (MER)

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

## Decisões Técnicas

Esta seção documenta o **racional de engenharia** por trás do projeto, útil para revisões técnicas e discussões arquiteturais.

| Decisão | Motivação |
|---------|-----------|
| **Clean Architecture** | Desacopla as regras de negócio de frameworks (Flask, ClamAV, bibliotecas de ML), permitindo evolução independente e testabilidade. |
| **Ports & Adapters (Hexagonal)** | O domínio define interfaces (ports); a infraestrutura provê implementações. Trocar ClamAV por VirusTotal, por exemplo, não exige mudanças nos casos de uso. |
| **Test-Driven Development (TDD)** | Os testes são escritos antes da implementação, garantindo cobertura alta e um domínio testável por design. |
| **Princípios SOLID** | Aplicados em toda a base: casos de uso com responsabilidade única, extensão via novos adapters (Open/Closed), segregação de interfaces nos repositórios. |
| **Repositórios In-Memory (inicial)** | Permitem prototipagem rápida e validação do modelo de domínio sem acoplar a um banco específico. Serão substituídos por PostgreSQL/Elasticsearch sem tocar no domínio. |
| **Flask em vez de Django** | Microframework leve adequado à abordagem API-first; o projeto não precisa das "baterias" do Django (ORM, admin, templates) já que a persistência vive na infraestrutura. |
| **Server-Sent Events (SSE)** | Escolhido em vez de WebSockets para streaming de logs porque o fluxo é unidirecional (servidor → cliente), mais simples de implementar e funciona via HTTP padrão. |
| **Isolation Forest para anomalias** | Algoritmo não-supervisionado adequado para dados de segurança, onde exemplos rotulados são escassos e outliers são justamente o que se quer detectar. |
| **Integração com ClamAV** | Engine maduro, open-source e amplamente reconhecido; a integração ocorre via subprocess na camada de infraestrutura, mantendo o domínio agnóstico. |
| **iptables / `/etc/hosts` para resposta** | Mecanismos nativos do Linux que não exigem serviços adicionais. A interface `ResponseService` permite substituição futura por firewalls em nuvem ou EDRs. |

---

## Fluxo do Sistema

```
[Fontes de Dados]
        ↓
[Ingestão de Eventos]
        ↓
[Motor de Correlação] ──→ [Threat Intelligence]
        ↓                          ↓
[Análise Comportamental] ←─────────┘
        ↓
[Motor de Decisão]
        ↓
[Resposta Automatizada]
        ↓
[Dashboard & API]
```

---

## Caso de Uso de Exemplo

**Detecção e mitigação automatizada de ataque de força bruta**

1. Múltiplos eventos de falha de autenticação chegam do mesmo IP de origem.
2. O **Motor de Correlação** agrupa esses eventos dentro de uma janela de tempo configurável.
3. O módulo de **Threat Intelligence** verifica o IP contra a base de IOCs.
4. O **Analisador Comportamental** confirma a anomalia de frequência.
5. O **Motor de Decisão** classifica a atividade como maliciosa.
6. O **Serviço de Resposta** automaticamente:
   - Bloqueia o IP via `iptables`
   - Gera um alerta correlacionado
   - Registra a ação para fins de auditoria
7. O **Dashboard** é atualizado em tempo real via SSE.

---

## Stack Tecnológica

| Camada | Tecnologias |
|--------|-------------|
| **Backend** | Python 3.10+, Flask 3.0+ |
| **Segurança** | ClamAV, iptables |
| **Machine Learning** | scikit-learn (Isolation Forest) |
| **Frontend** | HTML5, JavaScript, Chart.js |
| **Streaming** | Server-Sent Events (SSE) |
| **Testes** | pytest, pytest-cov |
| **Produção** | Gunicorn |

---

## Estrutura do Projeto

```
ElizaSOC/
├── src/                          # Código fonte (Clean Architecture)
│   ├── domain/                   # Camada de domínio
│   │   ├── entities/             # Entidades de negócio
│   │   ├── ports/                # Interfaces (portas)
│   │   ├── repositories/         # Interfaces de repositórios
│   │   └── services/             # Interfaces de serviços
│   ├── application/              # Camada de aplicação
│   │   └── use_cases/            # Casos de uso
│   ├── infrastructure/           # Camada de infraestrutura
│   │   ├── scanners/             # Adapter ClamAV
│   │   ├── repositories/         # Implementações de repositórios
│   │   └── services/             # Implementações de serviços
│   └── presentation/             # Camada de apresentação
│       └── api/                  # Controllers REST
├── tests/                        # Testes automatizados
│   ├── domain/                   # Testes de domínio
│   ├── infrastructure/           # Testes de infraestrutura
│   └── integration/              # Testes de integração
├── docs/                         # Documentação completa
├── scripts/                      # Scripts auxiliares
├── templates/                    # Templates HTML
├── static/                       # Arquivos estáticos (CSS, JS)
├── public/img/                   # Capturas de tela do projeto
├── app.py                        # Ponto de entrada da aplicação
├── start.sh                      # Script de inicialização
└── requirements.txt              # Dependências Python
```

---

## Instalação

### Requisitos
- Python 3.10+
- Linux (Ubuntu/Debian recomendados)
- ClamAV (opcional, para escaneamento de arquivos)
- scikit-learn (opcional, para análise comportamental com ML)

### Início Rápido

```bash
# 1. Clonar o repositório
git clone <url-do-repositório> ElizaSOC
cd ElizaSOC

# 2. Instalar dependências do sistema
sudo apt update
sudo apt install -y python3-pip python3-venv clamav

# 3. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 4. Instalar dependências Python
pip install -r requirements.txt

# 5. Atualizar base de vírus (opcional)
sudo freshclam

# 6. Iniciar o sistema
./start.sh
```

A API estará disponível em: **http://localhost:5000**

### Modos de Execução

```bash
# Desenvolvimento
export FLASK_ENV=development
python3 app.py

# Produção
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## Referência da API

URL Base: `http://localhost:5000/api`

### Status do Sistema

#### `GET /api/status`
Retorna o status do sistema.

```bash
curl http://localhost:5000/api/status
```

### Alertas

#### `GET /api/alerts`
Lista alertas com filtros opcionais.

**Parâmetros**:
- `limit` (int, padrão: 100) — número máximo de alertas
- `offset` (int, padrão: 0) — paginação
- `category` (string) — filtrar por categoria (`phishing`, `malware`, etc.)
- `severity` (int) — filtrar por severidade (1–4)

```bash
curl "http://localhost:5000/api/alerts?limit=50&category=phishing"
```

#### `GET /api/alerts/{id}`
Busca um alerta específico por ID.

#### `GET /api/alerts/stats`
Estatísticas de alertas.

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
Lista apenas alertas de phishing.

#### `GET /api/alerts/recent`
Lista alertas recentes.

### Arquivos

#### `GET /api/files/scanned`
Lista arquivos escaneados (suporta `limit` e `offset`).

#### `GET /api/files/infected`
Lista apenas arquivos infectados.

#### `POST /api/files/scan`
Escaneia um arquivo.

**Body**:
```json
{
  "filepath": "/path/to/file.exe",
  "quarantine": true
}
```

**Resposta**:
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
Busca o resultado de um escaneamento por ID.

### Dashboard

#### `GET /api/stats`
Estatísticas gerais do sistema.

#### `GET /api/phishing`
Alertas de phishing para o dashboard.

#### `GET /api/logs/stream`
Stream de logs em tempo real (Server-Sent Events).

#### `GET /api/protocols/{protocol}`
Estatísticas de um protocolo específico (ex.: TCP, UDP).

### Dashboard Web

#### `GET /`
Interface web do dashboard — abra `http://localhost:5000` no navegador.

---

## Testes

```bash
# Executar todos os testes
pytest

# Executar com relatório de cobertura
pytest --cov=src --cov-report=html

# Executar suítes específicas
pytest tests/domain/
pytest tests/integration/
```

A suíte de testes é organizada por camada arquitetural, reforçando a aderência do projeto à Clean Architecture.

---

## Status dos Módulos

| Módulo | Status |
|--------|--------|
| Análise de Arquivos (ClamAV) | ✅ Completo |
| SIEM / Correlação de Eventos | ✅ Completo |
| Threat Intelligence | 🟡 Funcional (básico) |
| Análise Comportamental | ✅ Completo |
| Resposta Automatizada | ✅ Completo |
| API REST | ✅ Completo |
| Dashboard Web | ✅ Completo |
| Persistência de Dados | 🔴 Pendente |
| Autenticação / RBAC | 🔴 Pendente |
| Feeds Externos de TI | 🔴 Pendente |

---

## Limitações Atuais

Este projeto está em **desenvolvimento ativo**. As limitações conhecidas incluem:

- **Armazenamento em memória**: Os repositórios não são persistentes — dados são perdidos entre reinicializações. Adapters persistentes fazem parte do roadmap.
- **Sem autenticação**: A API e o dashboard ainda não implementam autenticação ou autorização. **Não exponha em redes públicas.**
- **Feeds de TI limitados**: O Threat Intelligence trabalha sobre bases locais de IOCs; a integração com feeds externos (AbuseIPDB, VirusTotal, MISP) está planejada.
- **Modelos de ML simplificados**: A análise comportamental utiliza modelos pré-treinados, sem pipeline de treinamento contínuo.
- **Operações em nível de sistema**: A resposta automatizada interage com `iptables` e `/etc/hosts`. Use com cautela e revise as permissões antes de implantar em produção.

---

## Roadmap

- [ ] Persistência com **PostgreSQL** e **Elasticsearch**
- [ ] Autenticação **JWT** e **RBAC**
- [ ] Ingestão em tempo real do **Suricata** / **Zeek**
- [ ] Message broker (**RabbitMQ** / **Kafka**) para processamento assíncrono
- [ ] Feeds externos de threat intelligence (**AbuseIPDB**, **VirusTotal**, **MISP**)
- [ ] **Sandbox** para análise dinâmica
- [ ] **Honeypots**
- [ ] Containerização com **Docker** e orquestração com **Kubernetes**
- [ ] Pipeline CI/CD com **GitHub Actions**
- [ ] Pipeline de treinamento contínuo para modelos de ML

---

## Documentação

A documentação completa está disponível na pasta [`docs/`](docs/):

- [`docs/README.md`](docs/README.md) — índice da documentação
- [`docs/ARQUITETURA.md`](docs/ARQUITETURA.md) — arquitetura do sistema
- [`docs/INSTALACAO.md`](docs/INSTALACAO.md) — instalação detalhada
- [`docs/USO.md`](docs/USO.md) — guia de uso
- [`docs/QUICK_START.md`](docs/QUICK_START.md) — início rápido
- [`docs/SECURITY.md`](docs/SECURITY.md) — diretrizes de segurança

---

## Contribuições

Este é um projeto pessoal em desenvolvimento ativo. Sugestões, code reviews e feedback arquitetural são bem-vindos via issues ou pull requests.

---

## Autor

**Wilker Junio Coelho Pimenta**

- 🔗 GitHub: [github.com/wilkernel](https://github.com/wilkernel)
- 💼 LinkedIn: [linkedin.com/in/wil-j-c-pimenta](https://linkedin.com/in/wil-j-c-pimenta)

---

## Licença

Este projeto está licenciado sob a **Licença MIT** — veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

<p align="center">
  Construído com ❤️ aplicando Clean Architecture, SOLID e TDD.
</p>
