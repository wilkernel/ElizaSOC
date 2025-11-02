#  Guia de Uso - ElizaSOC v2.0

**Versão**: 2.0.0  
**Data**: 2025-11-02

## Índice

1. [API REST](#api-rest)
2. [Casos de Uso Programáticos](#casos-de-uso-programáticos)
3. [Exemplos Práticos](#exemplos-práticos)
4. [Configuração Avançada](#configuração-avançada)

## API REST

### Endpoints Disponíveis

#### Alertas

##### GET `/api/alerts`
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

##### GET `/api/alerts/<id>`
Busca alerta específico por ID.

**Exemplo**:
```bash
curl "http://localhost:5000/api/alerts/alert-123"
```

##### GET `/api/alerts/stats`
Estatísticas de alertas.

**Exemplo**:
```bash
curl "http://localhost:5000/api/alerts/stats"
```

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

##### GET `/api/alerts/phishing`
Lista apenas alertas de phishing.

**Exemplo**:
```bash
curl "http://localhost:5000/api/alerts/phishing?limit=20"
```

#### Arquivos

##### GET `/api/files/scanned`
Lista arquivos escaneados.

**Parâmetros**:
- `limit` (int, padrão: 100)
- `offset` (int, padrão: 0)

**Exemplo**:
```bash
curl "http://localhost:5000/api/files/scanned?limit=50"
```

##### GET `/api/files/infected`
Lista apenas arquivos infectados.

**Exemplo**:
```bash
curl "http://localhost:5000/api/files/infected"
```

##### POST `/api/files/scan`
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

##### GET `/api/files/<scan_id>`
Busca resultado de escaneamento por ID.

**Exemplo**:
```bash
curl "http://localhost:5000/api/files/scan-123"
```

#### Status

##### GET `/api/status`
Status do sistema.

**Exemplo**:
```bash
curl "http://localhost:5000/api/status"
```

## Casos de Uso Programáticos

### Escaneamento de Arquivo

```python
from src.infrastructure.scanners.clamav_scanner import ClamAVScanner
from src.infrastructure.repositories.in_memory_file_scan_repository import InMemoryFileScanRepository
from src.application.use_cases.scan_file_use_case import ScanFileUseCase

# Criar dependências
scanner = ClamAVScanner(quarantine_dir="/tmp/quarantine")
repository = InMemoryFileScanRepository()
use_case = ScanFileUseCase(scanner, repository)

# Escanear arquivo
result = use_case.execute("/path/to/file.exe", quarantine=True)

# Verificar resultado
if result.is_infected():
    print(f"Arquivo infectado: {result.threat_name}")
    print(f"Quarentenado: {result.quarantined}")
else:
    print("Arquivo limpo")
```

### Correlação de Eventos

```python
from src.infrastructure.services.event_correlator import SimpleEventCorrelator
from src.infrastructure.repositories.in_memory_event_repository import InMemoryEventRepository
from src.infrastructure.repositories.in_memory_alert_repository import InMemoryAlertRepository
from src.application.use_cases.correlate_events_use_case import CorrelateEventsUseCase
from src.domain.entities.event import SecurityEvent, EventType
from datetime import datetime

# Criar dependências
event_repo = InMemoryEventRepository()
alert_repo = InMemoryAlertRepository()
correlator = SimpleEventCorrelator(event_repo)
use_case = CorrelateEventsUseCase(correlator, event_repo, alert_repo)

# Criar eventos
events = [
    SecurityEvent(
        id="e1",
        event_type=EventType.DNS,
        timestamp=datetime.utcnow(),
        source="Suricata",
        data={"src_ip": "192.168.1.100", "query": "suspicious.com"},
    ),
    SecurityEvent(
        id="e2",
        event_type=EventType.HTTP,
        timestamp=datetime.utcnow(),
        source="Suricata",
        data={"src_ip": "192.168.1.100", "host": "suspicious.com"},
    ),
]

# Correlacionar
alerts = use_case.execute(events)
print(f"Alertas gerados: {len(alerts)}")
```

### Análise Comportamental

```python
from src.infrastructure.services.behavioral_analyzer import SimpleBehavioralAnalyzer
from src.infrastructure.repositories.in_memory_event_repository import InMemoryEventRepository
from src.application.use_cases.behavioral_analysis_use_case import BehavioralAnalysisUseCase

# Criar dependências
event_repo = InMemoryEventRepository()
analyzer = SimpleBehavioralAnalyzer(event_repo)
use_case = BehavioralAnalysisUseCase(analyzer, event_repo, alert_repo)

# Analisar eventos
alerts = use_case.execute(events)
print(f"Anomalias detectadas: {len(alerts)}")
```

### Resposta Automatizada

```python
from src.infrastructure.services.response_automation import SimpleResponseAutomation
from src.application.use_cases.response_automation_use_case import ResponseAutomationUseCase
from src.domain.entities.alert import Alert, AlertSeverity, AlertCategory
from datetime import datetime

# Criar serviço
response = SimpleResponseAutomation()
use_case = ResponseAutomationUseCase(response)

# Criar alerta crítico
alert = Alert(
    id="alert-1",
    timestamp=datetime.utcnow(),
    signature="CRITICAL MALWARE",
    category=AlertCategory.MALWARE,
    severity=AlertSeverity.CRITICAL,
    src_ip="192.0.2.1",
)

# Processar resposta
result = use_case.execute_for_alert(alert)
print(f"Ações realizadas: {result['actions_taken']}")
```

## Exemplos Práticos

### Monitoramento Contínuo

```python
import time
from pathlib import Path

# Monitorar diretório
watch_dir = Path("/tmp/downloads")
scanner = ClamAVScanner()
repo = InMemoryFileScanRepository()

while True:
    for file in watch_dir.glob("*"):
        if file.is_file():
            result = scanner.scan_file(str(file), quarantine=True)
            if result.is_infected():
                print(f"  Malware detectado: {file.name}")
                # Notificar, logar, etc.
    time.sleep(60)  # Verificar a cada minuto
```

### Processamento de Eventos do Suricata

```python
import json
from src.infrastructure.services.event_correlator import SimpleEventCorrelator
from src.domain.entities.event import SecurityEvent, EventType

# Ler eventos do eve.json
def process_suricata_events(eve_file):
    correlator = SimpleEventCorrelator(event_repo)
    events = []
    
    with open(eve_file) as f:
        for line in f:
            data = json.loads(line)
            event = SecurityEvent(
                id=data.get("event_id"),
                event_type=EventType.ALERT,
                timestamp=parse_timestamp(data["timestamp"]),
                source="Suricata",
                data=data,
            )
            events.append(event)
    
    # Correlacionar
    alerts = correlator.correlate_events(events)
    return alerts
```

## Configuração Avançada

### Usar Repositórios Persistentes

```python
# Exemplo: PostgreSQL (implementar seguindo interface)
from src.domain.repositories.alert_repository import AlertRepository

class PostgreSQLAlertRepository(AlertRepository):
    def __init__(self, connection):
        self.conn = connection
    
    def save(self, alert):
        # Implementar salvamento em PostgreSQL
        pass
    
    # Implementar outros métodos...
```

### Configurar ML para Análise Comportamental

```python
from src.infrastructure.services.behavioral_analyzer import SimpleBehavioralAnalyzer

analyzer = SimpleBehavioralAnalyzer(event_repo)

# Treinar modelo
training_data = [
    {"feature1": 1.0, "feature2": 2.0, "label": "normal"},
    {"feature1": 10.0, "feature2": 20.0, "label": "anomaly"},
]
analyzer.train_model(training_data)

# Usar para análise
alerts = analyzer.analyze_events(events)
```

### Integração com Threat Intelligence

```python
from src.infrastructure.services.threat_intelligence_service import SimpleThreatIntelligenceService

ti_service = SimpleThreatIntelligenceService(ioc_repo)

# Verificar IP
ioc = ti_service.check_ip("192.0.2.1")
if ioc:
    print(f"IP malicioso detectado: {ioc.threat_type}")

# Enriquecer alerta
enriched = ti_service.enrich_alert_with_ioc(alert_data)
```

## Boas Práticas

1. **Sempre use casos de uso**: Não acesse serviços/repositórios diretamente
2. **Trate erros**: Capture exceções adequadamente
3. **Log de ações**: Registre ações importantes
4. **Teste primeiro**: Use TDD para novas funcionalidades
5. **Valide dados**: Valide entradas antes de processar

## Troubleshooting

Ver `docs/INSTALACAO.md` seção Troubleshooting.

