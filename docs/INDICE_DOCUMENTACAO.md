#  Índice de Documentação - ElizaSOC v2.0

**Versão**: 2.0.0  
**Última atualização**: 2025-11-02

##  Documentos Principais

### 1. [README.md](README.md)
**Objetivo**: Índice geral da documentação  
**Para quem**: Todos os usuários  
**Conteúdo**:
- Visão geral da documentação
- Guia de leitura por perfil
- Status dos módulos
- Links rápidos

### 2. [ARQUITETURA.md](ARQUITETURA.md)
**Objetivo**: Arquitetura técnica completa do sistema  
**Para quem**: Desenvolvedores, arquitetos  
**Conteúdo**:
- Estrutura de camadas (Clean Architecture)
- Princípios SOLID aplicados
- Fluxos de dados
- Módulos implementados
- Guia de extensibilidade

### 3. [INSTALACAO.md](INSTALACAO.md)
**Objetivo**: Guia completo de instalação  
**Para quem**: Administradores de sistema  
**Conteúdo**:
- Pré-requisitos
- Instalação passo a passo
- Configuração avançada
- Troubleshooting
- Configuração de produção

### 4. [QUICK_START.md](QUICK_START.md)
**Objetivo**: Guia rápido para iniciar o sistema  
**Para quem**: Todos (primeiro passo)  
**Conteúdo**:
- Instalação rápida
- Comandos básicos
- Verificação de funcionamento
- Troubleshooting rápido

### 5. [USO.md](USO.md)
**Objetivo**: Guia de uso da API e casos de uso  
**Para quem**: Desenvolvedores, administradores  
**Conteúdo**:
- Endpoints REST documentados
- Exemplos de código
- Casos de uso programáticos
- Configuração avançada
- Boas práticas

### 6. [PLANO_IMPLEMENTACAO.md](PLANO_IMPLEMENTACAO.md)
**Objetivo**: Plano detalhado de desenvolvimento  
**Para quem**: Desenvolvedores, gestores  
**Conteúdo**:
- Status atual dos módulos
- Próximas fases de implementação
- Priorização de tarefas
- Estimativas e recursos

##  Documentos de Segurança

### 7. [SECURITY.md](SECURITY.md)
**Objetivo**: Segurança e boas práticas  
**Para quem**: Administradores de segurança  
**Conteúdo**:
- Configurações de segurança
- Recomendações
- Auditoria

### 8. [CHANGELOG_SECURITY.md](CHANGELOG_SECURITY.md)
**Objetivo**: Histórico de correções de segurança  
**Para quem**: Administradores, auditores  
**Conteúdo**:
- Mudanças de segurança
- Correções aplicadas

##  Documentos de Referência

### 9. [DASHBOARD_README.md](DASHBOARD_README.md)
**Objetivo**: Guia do dashboard web  
**Para quem**: Usuários finais  
**Conteúdo**:
- Funcionalidades do dashboard
- Como usar

### 10. [INSTALL.md](INSTALL.md)
**Objetivo**: Instruções de instalação legadas  
**Para quem**: Referência histórica  
**Nota**: Pode estar desatualizado, preferir INSTALACAO.md

### 11. [USAGE.md](USAGE.md)
**Objetivo**: Guia de uso legado  
**Para quem**: Referência histórica  
**Nota**: Pode estar desatualizado, preferir USO.md

##  Guia de Leitura por Perfil

###  Gestor/Executivo
1. Leia: [README.md](README.md) - Visão geral
2. Revise: [ARQUITETURA.md](ARQUITETURA.md) - Status dos módulos

###  Desenvolvedor
1. Leia: [ARQUITETURA.md](ARQUITETURA.md) - Entender estrutura
2. Leia: [USO.md](USO.md) - Como usar a API
3. Siga: TDD para novas funcionalidades

###  Administrador de Sistema
1. Leia: [INSTALACAO.md](INSTALACAO.md) - Instalação
2. Leia: [USO.md](USO.md) - Configuração
3. Revise: [SECURITY.md](SECURITY.md) - Segurança

###  Analista de Segurança
1. Leia: [ARQUITETURA.md](ARQUITETURA.md) - Fluxos de detecção
2. Leia: [USO.md](USO.md) - API e casos de uso
3. Revise: [SECURITY.md](SECURITY.md) - Configurações seguras

##  Documentos por Prioridade

###  Alta Prioridade (Leitura Obrigatória)
1. [QUICK_START.md](QUICK_START.md) - Início rápido
2. [INSTALACAO.md](INSTALACAO.md) - Instalação completa
3. [ARQUITETURA.md](ARQUITETURA.md) - Entender a arquitetura
4. [USO.md](USO.md) - Como usar o sistema

###  Média Prioridade (Importante)
5. [SECURITY.md](SECURITY.md) - Configuração segura
6. [DASHBOARD_README.md](DASHBOARD_README.md) - Dashboard web

###  Baixa Prioridade (Referência)
7. [CHANGELOG_SECURITY.md](CHANGELOG_SECURITY.md) - Histórico
8. [INSTALL.md](INSTALL.md) - Legado
9. [USAGE.md](USAGE.md) - Legado

##  Fluxo de Implementação Recomendado

```
1. README.md (Índice)
   ↓
2. ARQUITETURA.md (Entender estrutura)
   ↓
3. INSTALACAO.md (Instalar sistema)
   ↓
4. USO.md (Usar sistema)
   ↓
5. SECURITY.md (Securizar)
```

##  Status dos Documentos

| Documento | Status | Última Atualização |
|-----------|--------|-------------------|
| README.md |  Atualizado | 2025-11-02 |
| ARQUITETURA.md |  Atualizado | 2025-11-02 |
| INSTALACAO.md |  Atualizado | 2025-11-02 |
| USO.md |  Atualizado | 2025-11-02 |
| SECURITY.md |  Verificar | - |
| CHANGELOG_SECURITY.md |  Verificar | - |
| DASHBOARD_README.md |  Verificar | - |
| INSTALL.md |  Desatualizado | - |
| USAGE.md |  Desatualizado | - |

##  Documentos Removidos

Os seguintes documentos foram removidos por estarem desatualizados após a refatoração:
- `GUIA_IMPLEMENTACAO_PASSO_A_PASSO.md` - Substituído por INSTALACAO.md
- `ARQUITETURA_MONITORAMENTO_AVANCADO.md` - Substituído por ARQUITETURA.md
- `ANALISE_SISTEMA.md` - Desatualizado
- `AVALIACAO_PROJETO.md` - Desatualizado
- `RELATORIO_STATUS.md` - Desatualizado
- `RESUMO_EXECUTIVO.md` - Desatualizado
- `RESUMO_INTEGRACAO_CLAMAV.md` - Desatualizado

##  Atualizações

Este índice será atualizado conforme novos documentos forem criados ou atualizados.

**Versão**: 2.0.0  
**Última atualização**: 2025-11-02
