# 🚀 Guia de Implementação Passo a Passo

## Fase 1: Preparação e Instalação de Dependências (Dia 1)

### Passo 1.1: Atualizar Sistema Base

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential git curl wget
```

### Passo 1.2: Instalar ClamAV (Antivírus)

```bash
# Instalar ClamAV
sudo apt install -y clamav clamav-daemon clamav-freshclam

# Configurar atualizações automáticas
sudo systemctl enable clamav-freshclam
sudo systemctl start clamav-freshclam

# Primeira atualização manual
sudo freshclam

# Verificar instalação
clamscan --version
```

### Passo 1.3: Instalar YARA (Motor de Detecção)

```bash
# Dependências
sudo apt install -y libssl-dev libjansson-dev libmagic-dev

# Instalar YARA
cd /tmp
wget https://github.com/VirusTotal/yara/archive/v4.3.2.tar.gz
tar -xzf v4.3.2.tar.gz
cd yara-4.3.2
./bootstrap.sh
./configure
make
sudo make install

# Verificar
yara --version
```

### Passo 1.4: Instalar Ferramentas de Análise

```bash
# Exiftool (metadados)
sudo apt install -y libimage-exiftool-perl

# Capa (análise de malware)
pip3 install capa-rules

# Hash tools
sudo apt install -y hashdeep

# Ferramentas de rede
sudo apt install -y tcpdump wireshark-common
```

### Passo 1.5: Instalar Python Dependências

```bash
cd "/home/wilker/Área de Trabalho/Monitoramento_Phishing_Suricata_Shell"
pip3 install -r requirements.txt

# Dependências adicionais
pip3 install --user requests python-magic yara-python vt-py
```

## Fase 2: Configuração do Suricata Avançado (Dia 2)

### Passo 2.1: Atualizar Regras do Suricata

```bash
# Instalar suricata-update se não estiver instalado
sudo apt install -y python3-pip
sudo pip3 install suricata-update

# Atualizar regras
sudo suricata-update

# Ativar regras emergentes (emerging threats)
sudo suricata-update update-sources
sudo suricata-update --reload-command="sudo systemctl reload suricata"
```

### Passo 2.2: Habilitar File Extraction no Suricata

Editar `/etc/suricata/suricata.yaml`:

```yaml
file-store:
  enabled: yes
  log-dir: /var/log/suricata/files/
  force-magic: yes
  force-hash: yes
  include-file-size: yes

# Limites de tamanho de arquivo
file-extraction:
  enabled: yes
  rules: null  # null = extrair todos
  limit: 1000mb  # Limite de arquivos a extrair por dia
  zip-match-passwd: no
```

### Passo 2.3: Configurar HTTP Logging Detalhado

```yaml
outputs:
  - eve-log:
      enabled: yes
      filetype: regular
      filename: /var/log/suricata/eve.json
      types:
        - alert
        - http:
            extended: yes
            custom: [Accept, Accept-Language, User-Agent]
        - dns
        - tls:
            extended: yes
        - files
        - fileinfo
```

### Passo 2.4: Reiniciar Suricata

```bash
sudo systemctl restart suricata
sudo systemctl status suricata
```

## Fase 3: Implementar File Monitor (Dia 3)

### Passo 3.1: Criar Script de Monitoramento de Arquivos

```bash
cat > /home/wilker/Área-de-Trabalho/Monitoramento_Phishing_Suricata_Shell/file_monitor.py << 'EOF'
#!/usr/bin/env python3
# Monitor de arquivos baixados
import os
import hashlib
import json
from datetime import datetime
import magic

def calculate_hash(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def analyze_file(filepath):
    file_info = {
        'path': filepath,
        'size': os.path.getsize(filepath),
        'hash_sha256': calculate_hash(filepath),
        'mime_type': magic.from_file(filepath, mime=True),
        'timestamp': datetime.now().isoformat()
    }
    return file_info

# Diretórios a monitorar
MONITOR_DIRS = [
    '/home/*/Downloads',
    '/tmp',
    '/var/log/suricata/files'
]

# Implementar com inotify ou watchdog
EOF
```

### Passo 3.2: Instalar Biblioteca de Monitoramento

```bash
pip3 install --user watchdog
```

## Fase 4: Implementar Integração com ClamAV (Dia 4)

### Passo 4.1: Criar Módulo de Escaneamento

```bash
cat > /home/wilker/Área-de-Trabalho/Monitoramento_Phishing_Suricata_Shell/clamav_scanner.py << 'EOF'
#!/usr/bin/env python3
import subprocess
import json
from datetime import datetime

def scan_file(filepath):
    """Escaneia arquivo com ClamAV"""
    try:
        result = subprocess.run(
            ['clamscan', '--stdout', '--no-summary', filepath],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        is_infected = result.returncode == 1
        virus_name = None
        
        if is_infected:
            # Extrair nome do vírus da saída
            for line in result.stdout.split('\n'):
                if 'FOUND' in line:
                    parts = line.split('FOUND')
                    if len(parts) > 1:
                        virus_name = parts[0].strip().split()[-1]
        
        return {
            'infected': is_infected,
            'virus_name': virus_name,
            'scan_time': datetime.now().isoformat(),
            'scanner': 'ClamAV'
        }
    except subprocess.TimeoutExpired:
        return {'error': 'Timeout durante escaneamento'}
    except Exception as e:
        return {'error': str(e)}
EOF
```

### Passo 4.2: Criar Serviço de Escaneamento Automático

```bash
cat > /home/wilker/Área-de-Trabalho/Monitoramento_Phishing_Suricata_Shell/auto_scan_files.sh << 'EOF'
#!/bin/bash
# Escaneia automaticamente arquivos extraídos pelo Suricata

SURICATA_FILES_DIR="/var/log/suricata/files"
QUARANTINE_DIR="/var/quarantine"

mkdir -p "$QUARANTINE_DIR"

# Monitorar novos arquivos
inotifywait -m -e create --format '%w%f' "$SURICATA_FILES_DIR" | while read file; do
    if [ -f "$file" ]; then
        # Escanear
        result=$(clamscan "$file")
        if [ $? -eq 1 ]; then
            # Vírus detectado - mover para quarentena
            mv "$file" "$QUARANTINE_DIR/"
            echo "[$(date)] VÍRUS DETECTADO: $file -> $QUARANTINE_DIR"
        fi
    fi
done
EOF

chmod +x auto_scan_files.sh
```

## Fase 5: Implementar Threat Intelligence (Dia 5)

### Passo 5.1: Obter API Key do VirusTotal

1. Criar conta em: https://www.virustotal.com/gui/join-us
2. Obter API key gratuita (500 req/dia)

### Passo 5.2: Criar Módulo de Threat Intelligence

```bash
cat > /home/wilker/Área-de-Trabalho/Monitoramento_Phishing_Suricata_Shell/threat_intel.py << 'EOF'
#!/usr/bin/env python3
import requests
import os
import json
from datetime import datetime

class ThreatIntel:
    def __init__(self):
        self.vt_api_key = os.getenv('VT_API_KEY', '')
        self.vt_base_url = 'https://www.virustotal.com/vtapi/v2'
        
    def check_hash(self, file_hash):
        """Verifica hash no VirusTotal"""
        if not self.vt_api_key:
            return None
            
        params = {
            'apikey': self.vt_api_key,
            'resource': file_hash
        }
        
        response = requests.get(
            f'{self.vt_base_url}/file/report',
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def check_url(self, url):
        """Verifica URL no VirusTotal"""
        if not self.vt_api_key:
            return None
            
        params = {
            'apikey': self.vt_api_key,
            'resource': url
        }
        
        response = requests.get(
            f'{self.vt_base_url}/url/report',
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def check_ip(self, ip):
        """Verifica IP no VirusTotal"""
        if not self.vt_api_key:
            return None
            
        params = {
            'apikey': self.vt_api_key,
            'ip': ip
        }
        
        response = requests.get(
            f'{self.vt_base_url}/ip-address/report',
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        return None
EOF
```

### Passo 5.3: Configurar Feeds de IOC

```bash
cat > /home/wilker/Área-de-Trabalho/Monitoramento_Phishing_Suricata_Shell/ioc_feeds.py << 'EOF'
#!/usr/bin/env python3
import requests
import json
from datetime import datetime

class IOCFeeds:
    def __init__(self):
        self.urlhaus_url = 'https://urlhaus.abuse.ch/downloads/csv_recent/'
        self.feodo_url = 'https://feodotracker.abuse.ch/downloads/ipblocklist_recommended.json'
    
    def fetch_urlhaus(self):
        """Busca URLs maliciosas do URLhaus"""
        try:
            response = requests.get(self.urlhaus_url, timeout=30)
            if response.status_code == 200:
                return response.text
        except:
            pass
        return None
    
    def fetch_feodo(self):
        """Busca IPs de botnet do Feodo Tracker"""
        try:
            response = requests.get(self.feodo_url, timeout=30)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
EOF
```

## Fase 6: Atualizar Dashboard para Suportar Novas Funcionalidades (Dia 6)

### Passo 6.1: Atualizar app.py

Adicionar novas rotas para:
- `/api/files` - Lista de arquivos escaneados
- `/api/viruses` - Vírus detectados
- `/api/threat-intel` - Status de threat intelligence
- `/api/file/<hash>` - Detalhes de arquivo específico

### Passo 6.2: Atualizar Frontend

Adicionar novas seções:
- Tab "Arquivos Escaneados"
- Tab "Vírus Detectados"
- Gráfico de taxa de detecção por tipo
- Mapa de origem de ameaças

## Fase 7: Implementar Response Automatizado (Dia 7)

### Passo 7.1: Script de Quarentena

```bash
cat > /home/wilker/Área-de-Trabalho/Monitoramento_Phishing_Suricata_Shell/quarantine.sh << 'EOF'
#!/bin/bash
# Sistema de quarentena automática

QUARANTINE_DIR="/var/quarantine"
mkdir -p "$QUARANTINE_DIR"

quarantine_file() {
    local file="$1"
    local hash="$2"
    
    # Mover para quarentena
    mv "$file" "$QUARANTINE_DIR/${hash}.quarantine"
    
    # Remover permissões
    chmod 000 "$QUARANTINE_DIR/${hash}.quarantine"
    
    # Log
    echo "$(date) | QUARANTINE | $file | $hash" >> /var/log/quarantine.log
}
EOF
```

### Passo 7.2: Script de Bloqueio de IP

```bash
cat > /home/wilker/Área-de-Trabalho/Monitoramento_Phishing_Suricata_Shell/block_ip.sh << 'EOF'
#!/bin/bash
# Bloqueia IP usando iptables

block_ip() {
    local ip="$1"
    local reason="$2"
    
    # Adicionar regra iptables
    sudo iptables -A INPUT -s "$ip" -j DROP
    sudo iptables -A OUTPUT -d "$ip" -j DROP
    
    # Log
    echo "$(date) | BLOCK | $ip | $reason" >> /var/log/ip_block.log
    
    # Persistir regras
    sudo iptables-save > /etc/iptables/rules.v4
}
EOF
```

## Fase 8: Configurar Correlação de Eventos (Dia 8)

### Passo 8.1: Criar Motor de Correlação

Implementar em Python para correlacionar:
- Múltiplos alertas do mesmo IP
- Arquivos baixados + execuções
- DNS lookups suspeitos + conexões HTTP
- Padrões temporais

## Fase 9: Testes e Validação (Dia 9)

### Passo 9.1: Teste com Arquivo EICAR

```bash
# Download do arquivo de teste EICAR (inofensivo mas detectado como vírus)
echo 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*' > /tmp/eicar.com

# Testar escaneamento
clamscan /tmp/eicar.com

# Verificar se foi detectado e movido para quarentena
```

### Passo 9.2: Teste com URLs de Phishing

Usar URLs conhecidas de feeds de threat intelligence para validar detecção.

## Fase 10: Documentação e Manutenção (Dia 10)

### Passo 10.1: Criar Scripts de Manutenção

- Atualização diária de assinaturas
- Limpeza de logs antigos
- Rotação de arquivos em quarentena
- Backup de configurações

### Passo 10.2: Documentar Procedimentos

- Runbook de incidentes
- Procedimentos de escalação
- Manutenção preventiva

## Cronograma Resumido

| Fase | Duração | Prioridade |
|------|---------|------------|
| Fase 1: Preparação | 1 dia | Alta |
| Fase 2: Suricata Avançado | 1 dia | Alta |
| Fase 3: File Monitor | 1 dia | Média |
| Fase 4: ClamAV | 1 dia | Alta |
| Fase 5: Threat Intel | 1 dia | Média |
| Fase 6: Dashboard | 1 dia | Média |
| Fase 7: Response | 1 dia | Baixa |
| Fase 8: Correlação | 1 dia | Baixa |
| Fase 9: Testes | 1 dia | Alta |
| Fase 10: Documentação | 1 dia | Média |

**Total Estimado: 10 dias**

## Próximos Passos Imediatos

1. ✅ **Começar pela Fase 1** - Instalação de dependências
2. ✅ **Configurar API Key do VirusTotal**
3. ✅ **Testar ClamAV** com arquivo EICAR
4. ✅ **Atualizar regras do Suricata**

## Notas Importantes

- ⚠️ **Rate Limits**: VirusTotal free tier tem limite de 500 req/dia
- ⚠️ **Performance**: Escaneamento pode ser lento em arquivos grandes
- ⚠️ **Storage**: Arquivos em quarentena precisam de espaço
- ⚠️ **Privacidade**: Arquivos enviados ao VirusTotal são públicos

