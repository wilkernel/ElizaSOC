# Plano de Desenvolvimento - ElizaSOC

**Documento baseado em**: `Prompt.txt`  
**Data de criação**: 2025-11-02  
**Status**: Em progresso

## 📋 Visão Geral

Este documento detalha o plano de desenvolvimento do ElizaSOC seguindo:
- ✅ Clean Architecture
- ✅ Princípios SOLID
- ✅ Test-Driven Development (TDD)

## 🎯 Objetivos do Sprint

1. ✅ Limpar e organizar o repositório (.gitignore definitivo, remover artefatos)
2. ⏳ Reorganizar código em camadas (Clean Architecture)
3. ⏳ Adotar TDD e atingir cobertura mínima em módulos críticos
4. ⏳ Configurar CI/CD, Docker e scripts de ambiente
5. ⏳ Melhorar logs, observabilidade e segurança
6. ⏳ Planejar integração futura com Wazuh, MISP, RabbitMQ e Sandbox

---

## ✅ FASE 0 — PREPARAÇÃO E LIMPEZA

### Status: **COMPLETO**

#### Tarefa 0.1 — Criar branch de limpeza ✅
- [x] `git checkout -b feat/cleanup-repo`
- [x] Commit inicial com .gitignore atualizado

#### Tarefa 0.2 — Limpeza automática ✅
- [x] Criar `scripts/clean_project.sh`
- [x] Remover `__pycache__`, `.pyc`, venvs, htmlcov, logs temporários
- [x] Testar script e validar limpeza

**Critério atendido**: `git status` limpo sem caches nem arquivos grandes

#### Tarefa 0.3 — Validar dependências ✅
- [x] Consolidar `requirements.txt` e `requirements-dev.txt`
- [ ] Testar instalação limpa (próximo passo)
- [ ] Gerar `requirements.lock.txt`

**Próximo passo**: Validar instalação em ambiente limpo

---

## ⏳ FASE 1 — ARQUITETURA E ORGANIZAÇÃO

### Status: **PENDENTE**

#### Tarefa 1.1 — Estrutura de pastas (Clean Architecture)

**Estrutura alvo**:
```
src/
  domain/           # entidades, value objects, exceptions
  application/      # use-cases (ScanFileUseCase, CorrelateEventsUseCase)
  infrastructure/   # scanners, repos, integrações (clamav, suricata, es)
  presentation/     # Flask app, controllers, rotas
  common/           # utils, config, logging, dtos
```

**Ações**:
- [ ] Criar `src/common/` se não existir
- [ ] Mover `clamav_scanner.py` → `src/infrastructure/scanners/`
- [ ] Revisar dependências entre camadas

**Critério**: Nenhuma dependência circular; cada camada depende apenas da inferior.

#### Tarefa 1.2 — Adapters e Ports

**Ações**:
- [ ] Criar `src/domain/ports/`
- [ ] Criar `ScannerPort` (interface)
- [ ] Criar `RepositoryPort` (interface)
- [ ] Criar `ThreatIntelligencePort` (interface)
- [ ] Atualizar use-cases para depender de interfaces

**Exemplo**:
```python
from abc import ABC, abstractmethod

class ScannerPort(ABC):
    @abstractmethod
    def scan(self, filepath: str) -> dict:
        ...
```

**Critério**: Use-cases dependem apenas de interfaces.

#### Tarefa 1.3 — Unificar entrypoint

**Ações**:
- [ ] Manter `app_refactored.py` como ponto de entrada principal
- [ ] `app.py` deve redirecionar para `app_refactored.py` ou servir como legacy wrapper
- [ ] Validar que `python -m src.presentation.app` executa API corretamente

**Critério**: `python -m src.presentation.app` executa API corretamente.

---

## ⏳ FASE 2 — QUALIDADE DE CÓDIGO E LINT

### Status: **PENDENTE**

#### Tarefa 2.1 — Linters e formatadores

**Ferramentas**: black, ruff, isort

**Ações**:
- [ ] Criar `pyproject.toml` com configurações
- [ ] Configurar black (line-length = 88)
- [ ] Configurar isort (profile = "black")
- [ ] Executar `black .` e `ruff check src tests`

**pyproject.toml**:
```toml
[tool.black]
line-length = 88

[tool.isort]
profile = "black"
```

**Critério**: `black .`, `ruff check src tests` sem erros.

#### Tarefa 2.2 — Refatorar funções longas

**Ações**:
- [ ] Identificar funções > 80 linhas
- [ ] Dividir funções longas
- [ ] Reduzir complexidade ciclomática (usar `radon` ou `ruff metrics`)

**Critério**: Funções < 80 linhas, complexidade ciclomática baixa.

---

## ⏳ FASE 3 — TESTES (TDD)

### Status: **PENDENTE**

#### Tarefa 3.1 — Configurar pytest e fixtures

**Ações**:
- [ ] Validar `pytest.ini` existente
- [ ] Criar fixtures para `clamav_scanner` (mock)
- [ ] Criar fixtures para suricata logs
- [ ] Adicionar smoke tests

**Critério**: `pytest` roda com smoke tests bem-sucedidos.

#### Tarefa 3.2 — Cobertura mínima

**Módulos prioritários**:
- [ ] ClamAVScanner
- [ ] SimpleEventCorrelator
- [ ] SimpleThreatIntelligenceService
- [ ] API endpoints

**Exemplo de teste**:
```python
def test_scan_file_infected(monkeypatch):
    class FakeScanner:
        def scan(self, filepath):
            return {"status": "infected", "signature": "EICAR-Test"}
    scanner = FakeScanner()
    usecase = ScanFileUseCase(scanner, InMemoryRepo())
    result = usecase.execute("/tmp/eicar")
    assert result["status"] == "infected"
```

**Critério**: Cobertura > 60% em `application` e `infrastructure`.

---

## ⏳ FASE 4 — API E OBSERVABILIDADE

### Status: **PENDENTE**

#### Tarefa 4.1 — Endpoint de Healthcheck

**Ações**:
- [ ] Criar `/api/health` endpoint
- [ ] Retornar status dos serviços (clamav, es, suricata)
- [ ] Formato: `{"status": "ok", "services": {"clamav": "ok", "es": "ok"}}`

#### Tarefa 4.2 — Logs estruturados

**Ações**:
- [ ] Criar `src/common/logging.py`
- [ ] Substituir `print` por logging estruturado
- [ ] Usar JSONFormatter ou structlog
- [ ] Configurar níveis de log apropriados

#### Tarefa 4.3 — Métricas

**Ações**:
- [ ] Criar `/metrics` endpoint
- [ ] Expor métricas em formato Prometheus
- [ ] Métricas básicas: `alerts_count`, `scans_total`
- [ ] Integrar com sistema de métricas (opcional)

---

## ⏳ FASE 5 — INFRA E DEVOPS

### Status: **PENDENTE**

#### Tarefa 5.1 — Docker e docker-compose

**Ações**:
- [ ] Criar `Dockerfile` para aplicação
- [ ] Criar `docker-compose.yml`
- [ ] Incluir: app + elasticsearch + kibana + rabbitmq (opcional)
- [ ] Testar `docker-compose up`

**Critério**: `docker-compose up` levanta todo o ambiente.

#### Tarefa 5.2 — CI/CD

**Ações**:
- [ ] Criar `.github/workflows/ci.yml`
- [ ] Configurar: checkout, setup-python, install deps
- [ ] Adicionar: lint, test, coverage
- [ ] Configurar branch protection rules

**Critério**: PRs bloqueados se CI falhar.

---

## ⏳ FASE 6 — SEGURANÇA E HARDENING

### Status: **PENDENTE**

#### Tarefa 6.1 — Secrets & Env

**Ações**:
- [ ] Validar que `.env` não está sendo commitado
- [ ] Criar `.env.example`
- [ ] Usar `python-dotenv` (dev)
- [ ] Planejar secrets manager (prod)

#### Tarefa 6.2 — Auditoria de dependências

**Ações**:
- [ ] Rodar `safety check` ou `pip-audit`
- [ ] Corrigir vulnerabilidades críticas
- [ ] Justificar vulnerabilidades baixas (se necessário)

#### Tarefa 6.3 — Autenticação e rate-limiting

**Ações**:
- [ ] Implementar JWT ou OAuth
- [ ] Adicionar rate-limiting para endpoints sensíveis
- [ ] Documentar políticas de autenticação

---

## ⏳ FASE 7 — FUNCIONALIDADES AVANÇADAS

### Status: **FUTURO**

#### Tarefa 7.1 — Threat Intelligence (TI)

**Ações**:
- [ ] Integrar MISP, OTX ou AbuseIPDB via adapters
- [ ] Criar `infrastructure/tintel/` para integrações
- [ ] Agendar atualização de IOCs via RabbitMQ/Kafka

#### Tarefa 7.2 — Sandbox dinâmico

**Ações**:
- [ ] Integrar sandbox (Cuckoo, CAPE, etc.)
- [ ] Enviar arquivos suspeitos para análise
- [ ] Anexar resultados aos alertas

#### Tarefa 7.3 — Honeypot Integration

**Ações**:
- [ ] Receber logs do honeypot
- [ ] Correlacionar com eventos Suricata
- [ ] Criar adapters para honeypots comuns

---

## 📝 Checklist de PR

Cada PR deve conter:

- [ ] Descrição clara e issue vinculada
- [ ] Testes unitários novos/atualizados
- [ ] Código formatado (black/isort)
- [ ] CI verde
- [ ] Atualização de docs

---

## 📚 Documentação a Atualizar

- [ ] `README.md` — quickstart e links
- [ ] `docs/DEVELOPER_GUIDE.md` — setup local e testes
- [ ] `docs/ARQUITETURA.md` — diagramas e rationale
- [ ] `docs/CI_CD.md` — pipelines e variáveis de ambiente

---

## 🚀 Próximos Passos

1. **Validar instalação limpa** (Fase 0.3)
2. **Iniciar Fase 1** — Reorganizar código em camadas
3. **Mover clamav_scanner.py** → `src/infrastructure/scanners/`
4. **Criar interfaces (Ports)** em `src/domain/ports/`

---

**Última atualização**: 2025-11-02  
**Branch atual**: `feat/cleanup-repo`
