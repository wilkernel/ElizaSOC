# Documentação ElizaSOC v2.0

**Sistema Avançado de Detecção e Resposta a Ameaças**  
**Versão**: 2.0.0  
**Arquitetura**: Clean Architecture + SOLID + TDD

## Documentos Principais

### [QUICK_START.md](QUICK_START.md)
Guia rápido para iniciar o sistema localmente - **Leia primeiro**

### [ARQUITETURA.md](ARQUITETURA.md)
Arquitetura técnica completa:
- Estrutura de camadas (Clean Architecture)
- Princípios SOLID aplicados
- Fluxos de dados
- Módulos implementados
- Guia de extensibilidade

### [INSTALACAO.md](INSTALACAO.md)
Guia completo de instalação e configuração:
- Pré-requisitos
- Instalação passo a passo
- Configuração avançada
- Troubleshooting
- Configuração de produção

### [USO.md](USO.md)
Guia de uso da API e casos de uso:
- Endpoints REST documentados
- Exemplos de código Python
- Casos de uso programáticos
- Configuração avançada
- Boas práticas

### [PLANO_IMPLEMENTACAO.md](PLANO_IMPLEMENTACAO.md)
Plano detalhado para continuar o desenvolvimento:
- Status atual dos módulos
- Próximas fases de implementação
- Priorização de tarefas
- Estimativas de tempo
- Recursos necessários

## Documentos de Referência

### [SECURITY.md](SECURITY.md)
Segurança e boas práticas de configuração

### [CHANGELOG_SECURITY.md](CHANGELOG_SECURITY.md)
Histórico de correções de segurança

### [DASHBOARD_README.md](DASHBOARD_README.md)
Guia do dashboard web (legacy)

### [INDICE_DOCUMENTACAO.md](INDICE_DOCUMENTACAO.md)
Índice completo de toda a documentação

## Guia de Leitura Rápida

### Para Começar Agora
1. Leia [QUICK_START.md](QUICK_START.md) - Início rápido
2. Leia [INSTALACAO.md](INSTALACAO.md) - Instalação detalhada
3. Leia [USO.md](USO.md) - Como usar

### Para Entender o Sistema
1. Leia [ARQUITETURA.md](ARQUITETURA.md) - Arquitetura completa
2. Leia [PLANO_IMPLEMENTACAO.md](PLANO_IMPLEMENTACAO.md) - Próximos passos

### Para Desenvolver
1. Leia [ARQUITETURA.md](ARQUITETURA.md) - Entender estrutura
2. Siga TDD para novas funcionalidades
3. Consulte [PLANO_IMPLEMENTACAO.md](PLANO_IMPLEMENTACAO.md) - Tarefas pendentes

## Status Atual

### Módulos Implementados
- Análise de Arquivos (ClamAV) - Completo
- SIEM/Correlação de Eventos - Completo
- Threat Intelligence - Completo (básico)
- Análise Comportamental (ML) - Completo
- Resposta Automatizada - Completo
- API REST Refatorada - Completo

### Próximos Passos
Consulte [PLANO_IMPLEMENTACAO.md](PLANO_IMPLEMENTACAO.md) para detalhes completos.

**Prioridade Alta**:
1. Repositórios persistentes (PostgreSQL)
2. Integração com Suricata
3. Cache Redis

**Prioridade Média**:
1. Feeds de Threat Intelligence
2. Mensageria RabbitMQ
3. Workers de processamento

## Estrutura de Arquivos

```
docs/
├── README.md                  # Este arquivo (índice)
├── QUICK_START.md             # Início rápido
├── ARQUITETURA.md             # Arquitetura técnica
├── INSTALACAO.md              # Instalação
├── USO.md                     # Guia de uso
├── PLANO_IMPLEMENTACAO.md     # Plano de desenvolvimento
├── SECURITY.md                # Segurança
├── CHANGELOG_SECURITY.md      # Histórico de segurança
├── DASHBOARD_README.md        # Dashboard web
└── INDICE_DOCUMENTACAO.md     # Índice completo
```

## Atualizações

**Última atualização**: 2025-11-02  
**Versão da documentação**: 2.0.0

---

Para mais informações, consulte os documentos específicos listados acima.
