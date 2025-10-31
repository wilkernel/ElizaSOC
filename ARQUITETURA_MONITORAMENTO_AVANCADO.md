# 🏗️ Arquitetura de Monitoramento Avançado - Phishing, Malware e Vírus

## Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                    CAMADA DE CAPTURA                            │
├─────────────────────────────────────────────────────────────────┤
│  Suricata IDS/IPS  │  ClamAV  │  File Monitor  │  Network TAP │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              CAMADA DE PROCESSAMENTO                            │
├─────────────────────────────────────────────────────────────────┤
│  Log Collector  │  File Analyzer  │  Threat Intel  │  YARA      │
│  (Logstash)     │  (ClamAV/VT)    │  (IOC Feeds)   │  (Rules)   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              CAMADA DE ANÁLISE E CORRELAÇÃO                     │
├─────────────────────────────────────────────────────────────────┤
│  SIEM           │  ML Engine      │  Rule Engine   │  Correlator│
│  (Elasticsearch) │  (Anomaly Det.) │  (Custom Rules)│  (Events)  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              CAMADA DE VISUALIZAÇÃO E ALERTAS                    │
├─────────────────────────────────────────────────────────────────┤
│  Dashboard Web  │  Kibana        │  Email Alerts  │  API REST  │
│  (Flask)        │  (Visualization)│  (SMTP)        │  (External) │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              CAMADA DE RESPONSE AUTOMATIZADO                     │
├─────────────────────────────────────────────────────────────────┤
│  Firewall Rules │  Quarantine     │  IP Blocking   │  Isolation │
│  (iptables)     │  (File Move)    │  (Suricata)    │  (Network) │
└─────────────────────────────────────────────────────────────────┘
```

## Componentes Detalhados

### 1. Camada de Captura

#### 1.1 Suricata IDS/IPS (Já Implementado)
- **Função**: Detecção de tráfego de rede suspeito
- **Melhorias**: 
  - Atualizar regras diariamente (Emerging Threats, Snort)
  - Habilitar módulos avançados (HTTP, TLS, DNS profiling)
  - Configurar detecção de C2 communication

#### 1.2 ClamAV (Antivírus Open Source)
- **Função**: Escaneamento de arquivos em trânsito
- **Integração**: Via Suricata file extraction
- **Atualizações**: Diárias de assinaturas de vírus

#### 1.3 File Monitor
- **Função**: Monitora downloads e arquivos criados
- **Implementação**: `inotify` ou `auditd`
- **Campos**: MD5, SHA256, tipo MIME, tamanho

#### 1.4 Network TAP/SPAN
- **Função**: Captura passiva de todo tráfego
- **Benefício**: Visibilidade completa sem impacto na rede

### 2. Camada de Processamento

#### 2.1 Log Collector (Logstash - Já Configurado)
- **Função**: Coleta e normaliza logs de múltiplas fontes
- **Entradas**: Suricata, ClamAV, file monitor, sistema
- **Output**: Elasticsearch

#### 2.2 File Analyzer
- **Função**: Análise profunda de arquivos suspeitos
- **Engines**:
  - **ClamAV**: Detecção de vírus/malware conhecidos
  - **VirusTotal API**: Verificação multi-engine (40+ antivírus)
  - **YARA**: Regras customizadas para padrões
  - **Capa** (Malware Analysis): Detecção de comportamento suspeito
  - **Exiftool**: Metadados de arquivos

#### 2.3 Threat Intelligence
- **Função**: Validação contra IOCs conhecidos
- **Feeds**:
  - Abuse.ch (URLhaus, Feodo Tracker)
  - AlienVault OTX (Open Threat Exchange)
  - Emerging Threats Intelligence
  - VirusTotal Intelligence
  - Custom IOCs

#### 2.4 YARA Rules Engine
- **Função**: Detecção baseada em padrões (strings, regex)
- **Uso**: Malware families, phishing patterns, IOCs

### 3. Camada de Análise

#### 3.1 SIEM (Elasticsearch - Já Configurado)
- **Função**: Armazenamento e busca de eventos de segurança
- **Índices**:
  - `suricata-*`: Alertas do Suricata
  - `clamav-*`: Resultados de escaneamento
  - `files-*`: Arquivos analisados
  - `threat-intel-*`: IOCs e feeds
  - `correlation-*`: Eventos correlacionados

#### 3.2 ML Engine (Anomaly Detection)
- **Função**: Detecção de comportamento anômalo
- **Tecnologias**:
  - Elastic Machine Learning
  - Custom Python (scikit-learn)
- **Análises**:
  - Tráfego anômalo
  - Acessos não usuais
  - Padrões de horário suspeitos

#### 3.3 Rule Engine (Custom)
- **Função**: Regras de negócio customizadas
- **Exemplos**:
  - Múltiplas conexões para IPs suspeitos = possível C2
  - Download + execução em <5min = possível malware
  - Domínio novo acessado por múltiplos hosts = possível phishing

#### 3.4 Event Correlator
- **Função**: Correlaciona eventos relacionados
- **Casos**:
  - Mesmo IP em múltiplos alertas = possível ataque coordenado
  - Mesmo arquivo baixado por múltiplos hosts = possível worm
  - DNS lookup + HTTP request para domínio suspeito = possível phishing

### 4. Camada de Visualização

#### 4.1 Dashboard Web (Flask - Já Implementado)
- **Melhorias Necessárias**:
  - Gráfico de tendências de ameaças
  - Mapa de calor de IPs/domínios
  - Timeline de ataques
  - Análise de campanhas

#### 4.2 Kibana (Já Configurado)
- **Dashboards**:
  - Security overview
  - Malware detection
  - Network flows
  - Threat intel feed status

#### 4.3 Alertas (Email - Já Implementado)
- **Melhorias**:
  - Alertas por SMS (Twilio)
  - Integração Slack/Teams
  - Alertas críticos por telefone

### 5. Camada de Response

#### 5.1 Firewall Rules (iptables/nftables)
- **Função**: Bloqueio automático de IPs maliciosos
- **Trigger**: Score de ameaça > threshold

#### 5.2 Quarantine
- **Função**: Isolamento de arquivos suspeitos
- **Ação**: Mover para diretório seguro, remover permissões

#### 5.3 IP Blocking (Suricata)
- **Função**: Bloqueio em nível de IDS/IPS
- **Benefício**: Bloqueio antes de atingir destino

#### 5.4 Network Isolation
- **Função**: Isolar hosts comprometidos
- **Ação**: VLAN isolation, rota negada

## Fluxo de Dados Completo

### Cenário 1: Detecção de Phishing

```
1. Usuário acessa URL suspeita
   ↓
2. Suricata detecta padrão em HTTP/DNS
   ↓
3. Logstash coleta alerta
   ↓
4. Threat Intel valida contra feeds
   ↓
5. Se positivo: Alert gerado
   ↓
6. Dashboard atualizado em tempo real
   ↓
7. Email enviado para admin
   ↓
8. IP/domínio adicionado à blacklist
```

### Cenário 2: Detecção de Malware

```
1. Arquivo baixado (HTTP/Email)
   ↓
2. Suricata extrai arquivo
   ↓
3. File Monitor detecta novo arquivo
   ↓
4. ClamAV escaneia → Se suspeito:
   ↓
5. YARA analisa padrões
   ↓
6. VirusTotal valida (se necessário)
   ↓
7. Correlator verifica comportamento
   ↓
8. Se confirmado: Quarentena + Alert
   ↓
9. Host isolado (se necessário)
```

### Cenário 3: Detecção de Vírus

```
1. Arquivo executável detectado
   ↓
2. ClamAV escaneia imediatamente
   ↓
3. Se vírus conhecido detectado:
   ↓
4. Arquivo movido para quarentena
   ↓
5. Alert crítico gerado
   ↓
6. Hash adicionado à blacklist
   ↓
7. Scan de outros arquivos no sistema
   ↓
8. Relatório completo gerado
```

## Integrações Necessárias

### APIs e Serviços Externos

1. **VirusTotal API**
   - Verificação de arquivos e URLs
   - Rate limit: 500 req/dia (free tier)

2. **Abuse.ch APIs**
   - URLhaus (URLs maliciosas)
   - Feodo Tracker (botnet C2)

3. **AlienVault OTX**
   - IOCs de comunidade
   - Pulses de ameaças

4. **Emerging Threats ET Pro**
   - Regras avançadas
   - Threat intelligence

### Ferramentas Open Source

1. **ClamAV**
   - Antivírus de linha de comando
   - Atualização automática de assinaturas

2. **YARA**
   - Motor de detecção baseado em regras
   - Biblioteca de regras: YARA-Rules

3. **Capa**
   - Análise estática de malware
   - Detecção de capacidades

4. **MISP** (Opcional - SIEM avançado)
   - Plataforma de threat intelligence
   - Compartilhamento de IOCs

## Requisitos de Hardware/Software

### Mínimo Recomendado

- **CPU**: 4 cores
- **RAM**: 8GB (16GB recomendado)
- **Storage**: 100GB (para logs e arquivos em quarentena)
- **Rede**: Interface dedicada para monitoramento

### Software Base

- Ubuntu 22.04 LTS
- Python 3.10+
- Docker (opcional, para isolamento)

## Métricas de Sucesso Esperadas

- **Taxa de Detecção**: >95% (amplitudes conhecidas e zero-day)
- **Falsos Positivos**: <5%
- **Tempo de Detecção**: <30 segundos
- **Tempo de Response**: <5 minutos (automático)
- **Cobertura**: Phishing, Malware, Vírus, Trojans, Ransomware

