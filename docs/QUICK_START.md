# Quick Start - ElizaSOC v2.0

Guia rápido para iniciar o sistema localmente.

## Instalação Rápida

```bash
# 1. Instalar dependências
sudo apt update
sudo apt install -y python3-pip python3-venv clamav

# 2. Criar e ativar venv
python3 -m venv venv
source venv/bin/activate

# 3. Instalar Python packages
pip install -r requirements.txt

# 4. Configurar ClamAV (opcional)
sudo freshclam
```

## Iniciar Sistema

```bash
# Opção 1: Script unificado (recomendado)
./start.sh

# Opção 2: API Refatorada diretamente
python3 app_refactored.py

# Opção 3: API Legacy (compatibilidade)
python3 app.py
```

## Verificar Funcionamento

```bash
# Status da API
curl http://localhost:5000/api/status

# Escanear arquivo de teste
echo "test content" > /tmp/test.txt
curl -X POST http://localhost:5000/api/files/scan \
  -H "Content-Type: application/json" \
  -d '{"filepath": "/tmp/test.txt", "quarantine": false}'
```

## Estrutura de Execução

```
start.sh
  ├─ Verifica Python3
  ├─ Instala dependências (se necessário)
  ├─ Cria diretórios (logs, quarantine)
  └─ Executa app_refactored.py (padrão)
      └─ API REST disponível em http://localhost:5000
```

## Testes

```bash
# Executar testes
pytest

# Com cobertura
pytest --cov=src --cov-report=html
```

## Troubleshooting

### Erro: ClamAV não encontrado
```bash
sudo apt install -y clamav clamav-daemon
sudo freshclam
```

### Erro: Porta 5000 em uso
```bash
export FLASK_RUN_PORT=5001
./start.sh
```

### Erro: Módulos não encontrados
```bash
pip install -r requirements.txt --force-reinstall
```

## Próximos Passos

1. Configurar banco de dados (PostgreSQL)
2. Integrar com Suricata
3. Configurar feeds de Threat Intelligence
4. Ver documentação completa em [docs/README.md](README.md)

