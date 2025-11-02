#  Arquitetura ElizaSOC - Clean Architecture + SOLID + TDD

**Versão**: 2.0.0  
**Data**: 2025-11-02  
**Status**: Implementado

## Visão Geral

O ElizaSOC foi completamente refatorado seguindo os princípios de **Clean Architecture**, **SOLID**, **TDD** (Test-Driven Development) e **Clean Code**, transformando-se em uma plataforma avançada de detecção e resposta a ameaças.

## Estrutura de Camadas

```

      Presentation Layer                 
  (Controllers, APIs REST)               

                  

      Application Layer                 
  (Use Cases, Orchestration)             

                  

      Domain Layer (Core)                 
  (Entities, Interfaces/Ports)           

                  

      Infrastructure Layer               
  (Adapters, Implementations)            

```

### Dependency Rule
- **Presentation** → **Application** → **Domain** ← **Infrastructure**
- Dependências apontam para dentro (Domain é independente)

## Camadas Detalhadas

### 1. Domain Layer (Core)

**Responsabilidade**: Regras de negócio puras, independentes de frameworks

#### Entidades (`src/domain/entities/`)
- `Alert` - Alertas de segurança
- `FileScanResult` - Resultados de escaneamento
- `SecurityEvent` - Eventos de segurança
- `IOC` - Indicadores de Comprometimento

#### Interfaces/Ports (`src/domain/repositories/`, `src/domain/services/`)
- Repositórios: `AlertRepository`, `FileScanRepository`, `EventRepository`, `IOCRepository`
- Serviços: `FileScanner`, `ThreatIntelligenceService`, `EventCorrelator`, `BehavioralAnalyzer`, `ResponseAutomation`

### 2. Application Layer

**Responsabilidade**: Casos de uso que orquestram as regras de negócio

#### Use Cases (`src/application/use_cases/`)
- `ScanFileUseCase` - Escaneamento de arquivos
- `CorrelateEventsUseCase` - Correlação de eventos
- `AnalyzeThreatUseCase` - Análise com Threat Intelligence
- `BehavioralAnalysisUseCase` - Análise comportamental
- `ResponseAutomationUseCase` - Resposta automatizada

### 3. Infrastructure Layer

**Responsabilidade**: Implementações concretas de interfaces do Domain

#### Scanners (`src/infrastructure/scanners/`)
- `ClamAVScanner` - Implementação ClamAV refatorada

#### Repositórios (`src/infrastructure/repositories/`)
- `InMemoryAlertRepository`
- `InMemoryFileScanRepository`
- `InMemoryEventRepository`
- `InMemoryIOCRepository`

#### Serviços (`src/infrastructure/services/`)
- `SimpleEventCorrelator` - Correlação de eventos
- `SimpleThreatIntelligenceService` - Threat Intelligence
- `SimpleBehavioralAnalyzer` - Análise comportamental (ML)
- `SimpleResponseAutomation` - Resposta automatizada

### 4. Presentation Layer

**Responsabilidade**: Interfaces de usuário (API REST)

#### Controllers (`src/presentation/api/controllers/`)
- `alerts_controller.py` - Endpoints de alertas
- `files_controller.py` - Endpoints de arquivos

#### Factory (`src/presentation/api/app_factory.py`)
- `create_app()` - Factory para criação da aplicação Flask com DI

## Princípios Aplicados

### SOLID

- **S**ingle Responsibility: Cada classe tem uma única responsabilidade
- **O**pen/Closed: Aberto para extensão, fechado para modificação
- **L**iskov Substitution: Implementações podem ser substituídas
- **I**nterface Segregation: Interfaces específicas
- **D**ependency Inversion: Dependências de abstrações

### Clean Architecture

- **Independência de Frameworks**: Domain não conhece Flask
- **Testabilidade**: Código facilmente testável
- **Independência de UI**: UI pode mudar sem afetar Domain
- **Independência de Banco de Dados**: Repositórios podem ser trocados
- **Independência de Agentes Externos**: Interfaces bem definidas

### TDD (Test-Driven Development)

1. Escrever teste (que falha)
2. Implementar código mínimo para passar
3. Refatorar

**Cobertura Atual**: ~44-46% (aumentando)

## Fluxo de Dados

### Exemplo: Escaneamento de Arquivo

```
1. Request → Controller
   ↓
2. Controller → Use Case
   ↓
3. Use Case → Scanner (via interface)
   ↓
4. Scanner → Executa escaneamento
   ↓
5. Scanner → Retorna FileScanResult
   ↓
6. Use Case → Repository (via interface)
   ↓
7. Repository → Salva resultado
   ↓
8. Controller → Retorna resposta JSON
```

## Módulos Implementados

###  Análise de Arquivos
- Scanner ClamAV refatorado
- Quarentena automática
- Hash SHA256
- Casos de uso completos

###  SIEM/Correlação de Eventos
- Correlação por IP, domínio, hash
- Detecção de campanhas
- Alertas correlacionados
- Janelas de tempo configuráveis

###  Threat Intelligence
- Verificação de IOCs
- Enriquecimento de alertas
- Normalização de domínios/URLs
- Base para feeds externos

###  Análise Comportamental
- Detecção de anomalias de frequência
- Detecção de padrões suspeitos
- Detecção de zero-day
- Isolation Forest (ML opcional)

###  Resposta Automatizada
- Bloqueio de IPs (iptables)
- Bloqueio de domínios (/etc/hosts)
- Quarentena de arquivos
- Isolamento de endpoints

## Extensibilidade

Para adicionar novo módulo:

1. **Domain**: Criar entidades e interfaces
2. **Application**: Criar caso de uso
3. **Infrastructure**: Implementar serviços
4. **Presentation**: Criar controllers
5. **Tests**: Escrever testes (TDD)

## Referências

- Clean Architecture (Robert C. Martin)
- SOLID Principles
- Test-Driven Development (Kent Beck)

