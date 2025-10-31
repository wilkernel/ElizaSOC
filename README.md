# Monitoramento de Phishing com Suricata

Sistema completo para monitoramento de atividades suspeitas de phishing na rede usando Suricata IDS/IPS, com alertas por e-mail e visualização em tempo real via ELK Stack.

## Funcionalidades

- 🔍 **Monitoramento em Tempo Real**: Análise contínua do log `eve.json` do Suricata para detectar domínios suspeitos.
- 📧 **Alertas por E-mail**: Notificações automáticas via e-mail quando phishing ou malware é detectado.
- 📊 **Dashboard ELK**: Visualização interativa de logs com Elasticsearch, Logstash e Kibana.
- 📝 **Logs Estruturados**: Registro detalhado de todos os alertas em arquivo local.
- 🔧 **Configuração Automática**: Scripts para configurar Suricata e ELK Stack.

## Requisitos

- **Sistema Operacional**: Ubuntu 22.04 ou superior
- **Suricata**: Instalado e configurado como serviço
- **Ferramentas**: jq, mailx ou sendmail
- **ELK Stack**: Elasticsearch, Logstash, Kibana (instalação incluída)
- **Permissões**: Acesso root/sudo para configuração

## Instalação

### 1. Clonagem do Repositório
```bash
git clone https://github.com/seu-usuario/Monitoramento_Phishing_Suricata_Shell.git
cd Monitoramento_Phishing_Suricata_Shell
```

### 2. Configuração do Suricata
```bash
sudo bash configurar_suricata.sh
```
Este script:
- Configura a interface de rede (wlp2s0)
- Habilita logging para eve.json
- Reinicia o serviço Suricata

### 3. Instalação do ELK Stack
```bash
# Adicionar repositório Elasticsearch
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-7.x.list

# Instalar componentes
sudo apt update
sudo apt install -y elasticsearch logstash kibana jq mailutils

# Copiar configurações
sudo cp elastic_config/elasticsearch.yml /etc/elasticsearch/
sudo cp elastic_config/logstash.conf /etc/logstash/conf.d/
sudo cp elastic_config/kibana.yml /etc/kibana/

# Iniciar serviços
sudo systemctl enable elasticsearch
sudo systemctl start elasticsearch
sudo systemctl enable logstash
sudo systemctl start logstash
sudo systemctl enable kibana
sudo systemctl start kibana
```

### 4. Configuração de E-mail
Edite o arquivo `alertas_email.sh` e configure as variáveis:
```bash
FROM_EMAIL="alerts@seudominio.com"
TO_EMAIL="admin@seudominio.com"
SMTP_SERVER="smtp.seudominio.com"
SMTP_PORT="587"
```

Para Gmail, use:
```bash
FROM_EMAIL="seuemail@gmail.com"
TO_EMAIL="destinatario@dominio.com"
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT="587"
```
Certifique-se de habilitar "Acesso a apps menos seguros" no Gmail ou usar App Passwords.

## Uso

### Monitoramento Básico
```bash
bash monitorar_phishing_servico.sh
```
Gera relatório de alertas atuais.

### Alertas por E-mail
```bash
sudo bash alertas_email.sh &
```
Executa em background, monitorando continuamente e enviando alertas.

### Visualização ELK
Acesse http://localhost:5601 para o Kibana.

#### Configuração Inicial no Kibana
1. Vá para Management > Index Patterns
2. Crie padrão: `suricata-*`
3. Time field: `@timestamp`

#### Visualizações Sugeridas
- **Alertas por Tipo**: Pie chart de `alert.signature.keyword`
- **Alertas ao Longo do Tempo**: Line chart de `@timestamp`
- **IPs Suspeitos**: Table com `src_ip` e `dest_ip`
- **Severidade**: Bar chart de `alert.severity`

## Estrutura de Arquivos

```
Monitoramento_Phishing_Suricata_Shell/
├── monitorar_phishing_servico.sh    # Análise pontual de logs
├── configurar_suricata.sh           # Configuração do Suricata
├── alertas_email.sh                 # Sistema de alertas por e-mail
├── elastic_config/
│   ├── logstash.conf                # Pipeline Logstash
│   ├── elasticsearch.yml            # Config Elasticsearch
│   └── kibana.yml                   # Config Kibana
├── logs/
│   └── alertas_phishing.log         # Log local de alertas
└── README.md                        # Esta documentação
```

## Exemplo de Alerta

```
Assunto: [ALERTA SURICATA] Domínio suspeito detectado

Alerta de Phishing Detectado

Data/Hora: 2023-10-31T12:45:30.123456-05:00
Assinatura: ET MALWARE Suspicious Domain in DNS Lookup
IP Origem: 192.168.1.100
IP Destino: 8.8.8.8
Severidade: 2

Este é um alerta automático gerado pelo sistema de monitoramento Suricata.
Verifique os logs em /var/log/suricata/eve.json para mais detalhes.
```

## Troubleshooting

### Suricata não gera eve.json
- Verifique se o serviço está ativo: `sudo systemctl status suricata`
- Confirme configuração: `grep -A 10 "eve-log" /etc/suricata/suricata.yaml`
- Reinicie: `sudo systemctl restart suricata`

### E-mail não é enviado
- Instale mailx: `sudo apt install mailutils`
- Teste envio: `echo "Teste" | mailx -s "Teste" seuemail@dominio.com`
- Verifique logs: `tail -f /var/log/mail.log`

### ELK Stack não inicia
- Verifique Java: `java -version`
- Logs Elasticsearch: `sudo journalctl -u elasticsearch -f`
- Logs Logstash: `sudo journalctl -u logstash -f`
- Logs Kibana: `sudo journalctl -u kibana -f`

### Permissões negadas
- Execute scripts com sudo quando necessário
- Verifique permissões dos arquivos de log: `ls -la /var/log/suricata/`

## Logs e Rotação

Os alertas são salvos em `logs/alertas_phishing.log`. Para rotação automática:

Crie `/etc/logrotate.d/alertas_phishing`:
```
/home/usuario/Monitoramento_Phishing_Suricata_Shell/logs/alertas_phishing.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

## Créditos

Desenvolvido por Wilker Junio Coelho Pimenta

## Licença

Este projeto é distribuído sob a licença MIT. Veja LICENSE para detalhes.
