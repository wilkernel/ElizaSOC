# ElizaSOC - Sistema de Detecção e Resposta a Ameaças

**Versão**: 2.0.0  
**Arquitetura**: Clean Architecture + SOLID + TDD
**Licença**: MIT

## Sobre

ElizaSOC é um sistema completo de monitoramento, detecção e resposta automatizada a ameaças de segurança cibernética. Desenvolvido seguindo os princípios de Clean Architecture, SOLID e Test-Driven Development (TDD), oferece uma plataforma modular e extensível para Security Operations Center (SOC).

## Propósito

O ElizaSOC foi projetado para:

- **Detecção de Ameaças**: Identificar malwares, phishing, intrusões e outras ameaças em tempo real
- **Correlação de Eventos**: Correlacionar eventos de segurança para identificar campanhas e ataques coordenados
- **Threat Intelligence**: Verificar indicadores de comprometimento (IOCs) contra bases de conhecimento
- **Análise Comportamental**: Detectar anomalias usando Machine Learning
- **Resposta Automatizada**: Bloquear IPs maliciosos, isolar endpoints e colocar arquivos em quarentena
- **Visualização**: Dashboard web para monitoramento em tempo real

## Arquitetura

O sistema segue Clean Architecture com quatro camadas principais:

```
┌─────────────────────────────────────────┐
│     Presentation Layer                  │
│  (Controllers, API REST, Dashboard)    │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│     Application Layer                   │
│  (Use Cases, Business Logic)            │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│     Domain Layer (Core)                 │
│  (Entities, Interfaces/Ports)          │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│     Infrastructure Layer                │
│  (Adapters, Implementations)            │
└─────────────────────────────────────────┘
```

### Princípios Aplicados

- **Clean Architecture**: Separação clara de responsabilidades, independência de frameworks
- **SOLID**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **TDD**: Desenvolvimento orientado a testes
- **Dependency Rule**: Dependências apontam para dentro (Domain é independente)

## O Que Está Implementado

### Módulos Core

1. **Análise de Arquivos**
   - Escaneamento com ClamAV
   - Quarentena automática de arquivos infectados
   - Hash SHA256 para identificação
   - Categorização de ameaças

2. **SIEM/Correlação de Eventos**
   - Correlação por IP, domínio, hash
   - Detecção de campanhas
   - Alertas correlacionados
   - Janelas de tempo configuráveis

3. **Threat Intelligence**
   - Verificação de IOCs (IPs, domínios, hashes, URLs)
   - Enriquecimento de alertas
   - Normalização de domínios/URLs
   - Base para integração com feeds externos

4. **Análise Comportamental**
   - Detecção de anomalias de frequência
   - Detecção de padrões suspeitos
   - Isolation Forest (ML opcional)
   - Detecção de zero-day

5. **Resposta Automatizada**
   - Bloqueio de IPs (iptables)
   - Bloqueio de domínios (/etc/hosts)
   - Quarentena de arquivos
   - Isolamento de endpoints

6. **API REST**
   - Endpoints completos para alertas, arquivos e sistema
   - Filtros e paginação
   - Estatísticas em tempo real
   - Streaming de logs (Server-Sent Events)

7. **Dashboard Web**
   - Monitor em tempo real estilo "crypto trading"
   - Gráficos multi-linha com Chart.js
   - Três métricas simultâneas: Alertas, Rede, Sistema
   - Atualização dinâmica a cada 30 segundos
   - Controle de serviços (Suricata, ClamAV)
   - Análise de protocolos monitorados

## Endpoints da API

### Status

#### `GET /api/status`
Retorna o status do sistema.

**Exemplo**:
```bash
curl http://localhost:5000/api/status
```

### Alertas

#### `GET /api/alerts`
Lista alertas com filtros opcionais.

**Parâmetros**:
- `limit` (int, padrão: 100) - Número máximo de alertas
- `offset` (int, padrão: 0) - Paginação
- `category` (string) - Filtrar por categoria (phishing, malware, etc)
- `severity` (int) - Filtrar por severidade (1-4)

**Exemplo**:
```bash
curl "http://localhost:5000/api/alerts?limit=50&category=phishing"
```

#### `GET /api/alerts/<id>`
Busca alerta específico por ID.

**Exemplo**:
```bash
curl "http://localhost:5000/api/alerts/alert-123"
```

#### `GET /api/alerts/stats`
Estatísticas de alertas.

**Resposta**:
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

**Exemplo**:
```bash
curl "http://localhost:5000/api/alerts/phishing?limit=20"
```

#### `GET /api/alerts/recent`
Lista alertas recentes.

**Exemplo**:
```bash
curl "http://localhost:5000/api/alerts/recent"
```

### Arquivos

#### `GET /api/files/scanned`
Lista arquivos escaneados.

**Parâmetros**:
- `limit` (int, padrão: 100)
- `offset` (int, padrão: 0)

**Exemplo**:
```bash
curl "http://localhost:5000/api/files/scanned?limit=50"
```

#### `GET /api/files/infected`
Lista apenas arquivos infectados.

**Exemplo**:
```bash
curl http://localhost:5000/api/files/infected
```

#### `POST /api/files/scan`
Escaneia um arquivo.

**Body**:
```json
{
  "filepath": "/path/to/file.exe",
  "quarantine": true
}
```

**Exemplo**:
```bash
curl -X POST http://localhost:5000/api/files/scan \
  -H "Content-Type: application/json" \
  -d '{"filepath": "/tmp/suspicious.exe", "quarantine": true}'
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

#### `GET /api/files/<scan_id>`
Busca resultado de escaneamento por ID.

**Exemplo**:
```bash
curl "http://localhost:5000/api/files/scan-123"
```

### Dashboard

#### `GET /api/stats`
Estatísticas gerais do sistema.

**Exemplo**:
```bash
curl http://localhost:5000/api/stats
```

#### `GET /api/phishing`
Alertas de phishing para dashboard.

**Exemplo**:
```bash
curl http://localhost:5000/api/phishing
```

#### `GET /api/logs/stream`
Stream de logs em tempo real (Server-Sent Events).

**Exemplo**:
```bash
curl http://localhost:5000/api/logs/stream
```

#### `GET /api/protocols/<protocol>`
Estatísticas de um protocolo específico.

**Exemplo**:
```bash
curl http://localhost:5000/api/protocols/TCP
```

### Dashboard Web

#### `GET /`
Interface web do dashboard.

Acesse: `http://localhost:5000`

## Diagrama UML - Arquitetura de Camadas

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Alerts      │  │  Files       │  │  Dashboard   │      │
│  │  Controller  │  │  Controller  │  │  Controller  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
└─────────┼─────────────────┼─────────────────┼───────────────┘
          │                 │                 │
┌─────────▼─────────────────▼─────────────────▼───────────────┐
│                    Application Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ ScanFile     │  │ Correlate    │  │ Analyze      │      │
│  │ UseCase      │  │ Events       │  │ Threat       │      │
│  │              │  │ UseCase      │  │ UseCase      │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                 │               │
└─────────┼─────────────────┼─────────────────┼───────────────┘
          │                 │                 │
┌─────────▼─────────────────▼─────────────────▼───────────────┐
│                      Domain Layer                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Alert      │  │ FileScan     │  │ Security     │      │
│  │   Entity     │  │ Entity       │  │ Event       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Alert        │  │ FileScan     │  │ Event        │      │
│  │ Repository   │  │ Repository   │  │ Repository   │      │
│  │ (Port)       │  │ (Port)       │  │ (Port)       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
          ▲                 ▲                 ▲
┌─────────┼─────────────────┼─────────────────┼───────────────┐
│              Infrastructure Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ InMemory     │  │ InMemory     │  │ ClamAV       │      │
│  │ Alert        │  │ FileScan     │  │ Scanner      │      │
│  │ Repository   │  │ Repository   │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Event        │  │ Threat       │  │ Behavioral   │      │
│  │ Correlator   │  │ Intelligence │  │ Analyzer     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Modelo Entidade-Relacionamento (MER)

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
       │
       │ 1:N
       │
┌──────▼──────────────┐
│  SecurityEvent      │
├─────────────────────┤
│ id (PK)             │
│ event_type          │
│ timestamp           │
│ source              │
│ data                │
│ related_events[]    │
│ processed           │
└──────┬──────────────┘
       │
       │ N:1
       │
┌──────▼──────────────┐
│   FileScanResult    │
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
       │
       │ N:1
       │
┌──────▼──────────────┐
│      IOC            │
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

## Imagens do Sistema

### 1
![Dashboard Principal](public/img/Captura%20de%20tela%20de%202025-11-04%2000-34-43.png)

### 2
![Monitor em Tempo Real](public/img/Captura%20de%20tela%20de%202025-11-04%2000-38-07.png)

### 3
![Alertas e Métricas](public/img/Captura%20de%20tela%20de%202025-11-04%2000-40-13.png)

### 4
![Análise de Protocolos](public/img/Captura%20de%20tela%20de%202025-11-04%2000-41-46.png)

### Controle de Serviços
![Controle de Serviços](public/img/Captura%20de%20tela%20de%202025-11-04%2000-43-24.png)

### 5
![Gráficos Interativos](public/img/Captura%20de%20tela%20de%202025-11-04%2000-45-18.png)

### 6
![Logs em Tempo Real](public/img/Captura%20de%20tela%20de%202025-11-04%2000-46-31.png)

### 7
![Métricas do Sistema](public/img/Captura%20de%20tela%20de%202025-11-04%2000-47-53.png)

### 8
![Visão Geral](public/img/Captura%20de%20tela%20de%202025-11-04%2000-48-55.png)

## Vídeo Demonstrativo

[![ElizaSOC - Sistema de Detecção e Resposta a Ameaças](https://img.youtube.com/vi/fmdgvTvZxDI/0.jpg)](https://www.youtube.com/watch?v=fmdgvTvZxDI)

**Assista ao vídeo**: [https://www.youtube.com/watch?v=fmdgvTvZxDI](https://www.youtube.com/watch?v=fmdgvTvZxDI)


## Instalação Rápida

```bash
# 1. Clonar repositório
git clone <url-repositorio> ElizaSOC
cd ElizaSOC

# 2. Instalar dependências do sistema
sudo apt update
sudo apt install -y python3-pip python3-venv clamav

# 3. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 4. Instalar dependências Python
pip install -r requirements.txt

# 5. Configurar ClamAV (opcional)
sudo freshclam

# 6. Iniciar sistema
./start.sh
```

A API estará disponível em: `http://localhost:5000`

## Estrutura do Projeto

```
ElizaSOC/
├── src/                      # Código fonte (Clean Architecture)
│   ├── domain/               # Camada de domínio (entities, interfaces)
│   │   ├── entities/         # Entidades de negócio
│   │   ├── ports/             # Interfaces (repositories, services)
│   │   ├── repositories/      # Interfaces de repositórios
│   │   └── services/          # Interfaces de serviços
│   ├── application/          # Camada de aplicação (use cases)
│   │   └── use_cases/         # Casos de uso
│   ├── infrastructure/        # Camada de infraestrutura (implementações)
│   │   ├── scanners/          # Scanners (ClamAV)
│   │   ├── repositories/      # Implementações de repositórios
│   │   └── services/          # Implementações de serviços
│   └── presentation/          # Camada de apresentação (API REST)
│       └── api/               # Controllers e rotas
├── tests/                     # Testes automatizados
│   ├── domain/                # Testes de domínio
│   ├── infrastructure/        # Testes de infraestrutura
│   └── integration/           # Testes de integração
├── docs/                      # Documentação completa
├── scripts/                    # Scripts auxiliares
├── templates/                   # Templates HTML
├── static/                     # Arquivos estáticos (CSS, JS)
├── app.py                      # Aplicação principal
├── start.sh                    # Script de inicialização
└── requirements.txt            # Dependências Python
```

## Testes

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=src --cov-report=html

# Testes específicos
pytest tests/domain/
pytest tests/integration/
```

## Requisitos

- Python 3.10+
- Flask 3.0+
- ClamAV (opcional, para escaneamento)
- scikit-learn (opcional, para análise comportamental ML)

## Documentação

Documentação completa disponível em `docs/`:

- [docs/README.md](docs/README.md) - Índice da documentação
- [docs/ARQUITETURA.md](docs/ARQUITETURA.md) - Arquitetura do sistema
- [docs/INSTALACAO.md](docs/INSTALACAO.md) - Instalação detalhada
- [docs/USO.md](docs/USO.md) - Guia de uso completo
- [docs/QUICK_START.md](docs/QUICK_START.md) - Início rápido
- [docs/SECURITY.md](docs/SECURITY.md) - Segurança e boas práticas

## Desenvolvimento

### Adicionar Novo Módulo

1. **Domain**: Criar entidades e interfaces
2. **Application**: Criar caso de uso
3. **Infrastructure**: Implementar serviços/repositórios
4. **Tests**: Escrever testes (TDD)
5. **Presentation**: Criar controllers se necessário

### Executar Localmente

```bash
# Desenvolvimento
export FLASK_ENV=development
python3 app.py

# Produção
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Status dos Módulos

| Módulo | Status |
|--------|--------|
| Análise de Arquivos | Completo |
| SIEM/Correlação | Completo |
| Threat Intelligence | Completo (básico) |
| Análise Comportamental | Completo |
| Resposta Automatizada | Completo |
| API REST | Completo |
| Dashboard Web | Completo |

## Próximos Passos

- Integração com feeds externos de Threat Intelligence
- Repositórios persistentes (PostgreSQL/Elasticsearch)
- Mensageria (RabbitMQ/Kafka)
- Honeypots
- Sandbox para análise dinâmica

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Autor

**Wilker Junio Coelho Pimenta**

---

Para mais informações, consulte a [documentação completa](docs/README.md).
