#  Instalação e Configuração - ElizaSOC v2.0

**Versão**: 2.0.0  
**Data**: 2025-11-02

## Pré-requisitos

- Ubuntu 22.04 LTS ou superior
- Python 3.10+
- ClamAV (para escaneamento de arquivos)
- Suricata (opcional, para monitoramento de rede)
- Acesso root/sudo (para algumas funcionalidades)

## Instalação Rápida

### 1. Clonar/Obter o Projeto

```bash
cd ~
git clone <url-do-repositorio> ElizaSOC
cd ElizaSOC
```

### 2. Instalar Dependências do Sistema

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv clamav clamav-daemon
```

### 3. Instalar Dependências Python

```bash
# Criar ambiente virtual (recomendado)
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 4. Configurar ClamAV

```bash
# Atualizar assinaturas
sudo freshclam

# Testar instalação
clamscan --version
```

### 5. Executar API

```bash
# API Refatorada (Clean Architecture)
python3 app.py

# Ou API antiga (compatibilidade)
python3 app.py
```

A API estará disponível em: `http://localhost:5000`

## Instalação Detalhada

### Configuração de Ambiente Virtual

```bash
# Criar venv
python3 -m venv venv

# Ativar venv
source venv/bin/activate

# Desativar (quando necessário)
deactivate
```

### Dependências Python

#### Obrigatórias
- Flask 3.0+
- flask-cors
- pytest (para testes)

#### Opcionais
- scikit-learn (para análise comportamental ML)
- numpy (requerido pelo scikit-learn)
- pika (para RabbitMQ - futuro)
- requests (para APIs externas)

### Configuração Avançada

#### Variáveis de Ambiente

Criar arquivo `.env`:

```bash
# Flask
FLASK_ENV=development  # ou production
FLASK_DEBUG=True

# Quarentena
QUARANTINE_DIR=/var/quarantine

# Logs
LOG_DIR=./logs

# Threat Intelligence (futuro)
VIRUSTOTAL_API_KEY=your_key_here
OTX_API_KEY=your_key_here
```

#### Permissões

Para bloqueios de IP/domínio e isolamento de endpoints:

```bash
# Adicionar usuário ao grupo sudo (se necessário)
sudo usermod -aG sudo $USER

# Ou executar com sudo
sudo python3 app.py
```

## Verificação da Instalação

### 1. Testes

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=src --cov-report=html

# Testes específicos
pytest tests/domain/
pytest tests/integration/
```

### 2. Verificar API

```bash
# Status da API
curl http://localhost:5000/api/status

# Listar alertas
curl http://localhost:5000/api/alerts
```

### 3. Testar Escaneamento

```bash
# Criar arquivo de teste
echo "test content" > /tmp/test.txt

# Escanear via API
curl -X POST http://localhost:5000/api/files/scan \
  -H "Content-Type: application/json" \
  -d '{"filepath": "/tmp/test.txt", "quarantine": false}'
```

## Troubleshooting

### ClamAV não encontrado

```bash
# Verificar instalação
which clamscan

# Se não instalado
sudo apt install -y clamav clamav-daemon
sudo freshclam
```

### Erro de Permissões

```bash
# Para quarentena
sudo mkdir -p /var/quarantine
sudo chown $USER:$USER /var/quarantine

# Para bloqueios de IP (requer root)
sudo python3 app.py
```

### Erro de Importação

```bash
# Verificar ambiente virtual
which python3
pip list | grep Flask

# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

### Porta 5000 em uso

```bash
# Verificar processo
lsof -i :5000

# Matar processo
kill -9 <PID>

# Ou usar outra porta
export FLASK_RUN_PORT=5001
python3 app.py
```

## Configuração de Produção

### 1. Usar Gunicorn

```bash
pip install gunicorn

# Executar
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 2. Criar Service Systemd

Criar `/etc/systemd/system/elizasoc.service`:

```ini
[Unit]
Description=ElizaSOC API
After=network.target

[Service]
User=elizasoc
WorkingDirectory=/opt/elizasoc
Environment="PATH=/opt/elizasoc/venv/bin"
ExecStart=/opt/elizasoc/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

### 3. Configurar Nginx (Reverso Proxy)

```nginx
server {
    listen 80;
    server_name elizasoc.example.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Próximos Passos

Após instalação:

1. Configurar Suricata (se usar monitoramento de rede)
2. Configurar feeds de Threat Intelligence
3. Treinar modelos de ML (se usar análise comportamental)
4. Configurar backups de dados
5. Configurar monitoramento e alertas do sistema

## Suporte

- Documentação completa: `docs/`
- Arquitetura: `docs/ARQUITETURA.md`
- Uso: `docs/USO.md`

