# ElizaSOC - Sistema Avançado de Detecção e Resposta a Ameaças

**Versão**: 2.0.0  
**Arquitetura**: Clean Architecture + SOLID + TDD

## Sobre

ElizaSOC é um sistema completo de monitoramento, detecção e resposta automatizada a ameaças de segurança. Desenvolvido seguindo princípios de Clean Architecture, SOLID e Test-Driven Development (TDD).

## Funcionalidades

### Implementado

- **Análise de Arquivos**: Escaneamento com ClamAV, quarentena automática
- **SIEM/Correlação de Eventos**: Correlação inteligente de eventos relacionados
- **Threat Intelligence**: Verificação de IOCs (IPs, domínios, hashes, URLs)
- **Análise Comportamental**: Detecção de anomalias com Machine Learning
- **Resposta Automatizada**: Bloqueio de IPs/domínios, isolamento de endpoints
- **API REST**: Interface completa para integração
- **Dashboard Web**: Visualização em tempo real com métricas e controles avançados
  - 🎯 **Monitor em tempo real** estilo "crypto trading" com gráfico multi-linha
  - 📊 **Três métricas simultâneas**: Alertas, Rede (Flows+DNS), Sistema
  - ⚡ Atualização dinâmica a cada 30 segundos
  - 🚨 Alertas com streaming SSE
  - 📈 Gráficos interativos (Chart.js)
  - 🔧 Controle de serviços (Suricata, ClamAV)
  - 📁 Análise de arquivos e logs
  - ⚙️ Métricas de sistema (CPU, memória, logs)

## Instalação Rápida

```bash
# 1. Clonar repositório
git clone <url-repositorio> ElizaSOC
cd ElizaSOC

# 2. Instalar dependências do sistema
sudo apt update
sudo apt install -y python3-pip python3-venv clamav

# 3. Criar ambiente virtual (recomendado)
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

## Uso

### Iniciar Sistema

```bash
# Script Completo (Recomendado) - Inicia todos os serviços automaticamente
bash start_complete.sh

# API Refatorada
./start.sh

# Ou especificar tipo
./start.sh refactored  # API nova (padrão)
./start.sh legacy      # API antiga (compatibilidade)
```

### Dashboard Web

Após iniciar o sistema, acesse o dashboard em:
```
http://localhost:5000
```

O dashboard oferece:
- 🎯 **Monitor Principal**: Gráfico multi-linha em tempo real (estilo "crypto trading")
- 📊 **3 Métricas Simultâneas**: Alertas, Rede, Sistema com eixo duplo
- ⚡ **Atualização Dinâmica**: Refresh automático a cada 30 segundos
- 📈 **Visualizações**: Gráficos interativos (Chart.js)
- 🔧 **Controle de Serviços**: Start/Stop/Restart Suricata e ClamAV
- 📁 **Análise**: Arquivos, logs, protocolos monitorados
- ⚙️ **Sistema**: CPU, memória, tamanho de logs
- ✅ **Validação**: Confirmação de dados reais (não mocks)

### API REST

#### Status
```bash
curl http://localhost:5000/api/status
```

#### Alertas
```bash
# Listar alertas
curl http://localhost:5000/api/alerts

# Alertas de phishing
curl http://localhost:5000/api/alerts/phishing

# Estatísticas
curl http://localhost:5000/api/alerts/stats
```

#### Arquivos
```bash
# Escanear arquivo
curl -X POST http://localhost:5000/api/files/scan \
  -H "Content-Type: application/json" \
  -d '{"filepath": "/path/to/file", "quarantine": true}'

# Listar infectados
curl http://localhost:5000/api/files/infected
```

### Uso Programático

```python
from src.presentation.api.app_factory import create_app
from src.infrastructure.scanners.clamav_scanner import ClamAVScanner
from src.infrastructure.repositories.in_memory_file_scan_repository import InMemoryFileScanRepository
from src.application.use_cases.scan_file_use_case import ScanFileUseCase

# Criar dependências
scanner = ClamAVScanner()
repo = InMemoryFileScanRepository()
use_case = ScanFileUseCase(scanner, repo)

# Escanear arquivo
result = use_case.execute("/path/to/file.exe")
print(f"Status: {result.status.value}")
print(f"Infected: {result.is_infected()}")
```

## Estrutura do Projeto

```
ElizaSOC/
├── src/                      # Código fonte (Clean Architecture)
│   ├── domain/               # Camada de domínio (entities, interfaces)
│   ├── application/         # Camada de aplicação (use cases)
│   ├── infrastructure/      # Camada de infraestrutura (implementações)
│   └── presentation/        # Camada de apresentação (API REST)
├── tests/                    # Testes automatizados
│   ├── domain/              # Testes de domínio
│   ├── infrastructure/      # Testes de infraestrutura
│   └── integration/         # Testes de integração
├── docs/                     # Documentação completa
├── scripts/                  # Scripts auxiliares
├── templates/                # Templates HTML (legacy)
├── static/                   # Arquivos estáticos (legacy)
├── app.py         # API Refatorada (recomendado)
├── app.py                    # API Legacy (compatibilidade)
├── start.sh                  # Script de inicialização
└── requirements.txt          # Dependências Python
```

## Módulos Implementados

1. **Análise de Arquivos**: ClamAVScanner refatorado
2. **SIEM/Correlação**: SimpleEventCorrelator
3. **Threat Intelligence**: SimpleThreatIntelligenceService
4. **Análise Comportamental**: SimpleBehavioralAnalyzer (ML)
5. **Resposta Automatizada**: SimpleResponseAutomation

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

## Compatibilidade

O sistema mantém compatibilidade com código antigo através de wrappers:

- `clamav_scanner.py` - Wrapper de compatibilidade
- `app.py` - API legacy (mantida para compatibilidade)

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

## Troubleshooting

### ClamAV não encontrado
```bash
sudo apt install -y clamav clamav-daemon
sudo freshclam
```

### Erro de importação
```bash
pip install -r requirements.txt --force-reinstall
```

### Porta 5000 em uso
```bash
export FLASK_RUN_PORT=5001
python3 app.py
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
| Dashboard Web | Legacy (mantido) |

## Próximos Passos

- Integração com feeds externos de Threat Intelligence
- Repositórios persistentes (PostgreSQL/Elasticsearch)
- Mensageria (RabbitMQ/Kafka)
- Honeypots
- Sandbox para análise dinâmica

## Licença

Distribuído sob a licença MIT.

## Autor

**Wilker Junio Coelho Pimenta**

---

Para mais informações, consulte a [documentação completa](docs/README.md).
