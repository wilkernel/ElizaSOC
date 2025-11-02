#!/bin/bash
# Script unificado para iniciar ElizaSOC
# Suporta tanto API antiga (app.py) quanto refatorada (app_refactored.py)

set -e

cd "$(dirname "$0")"

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== ElizaSOC - Sistema de Detecção e Resposta a Ameaças ===${NC}"
echo ""

# Verificar Python3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERRO: Python3 não está instalado.${NC}"
    echo "Instale com: sudo apt install python3 python3-pip"
    exit 1
fi

# Verificar dependências Python
if ! python3 -c "import flask" 2>/dev/null; then
    echo -e "${YELLOW}Instalando dependências Python...${NC}"
    pip3 install -r requirements.txt --user
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERRO: Falha ao instalar dependências.${NC}"
        exit 1
    fi
fi

# Criar diretórios necessários
mkdir -p logs quarantine

# Escolher qual aplicação executar
API_TYPE="${1:-refactored}"

if [ "$API_TYPE" = "legacy" ] || [ "$API_TYPE" = "old" ]; then
    echo -e "${YELLOW}Iniciando API Legacy (app.py)...${NC}"
    APP_FILE="app.py"
    
    # Verificar se Suricata está rodando (opcional)
    if systemctl is-active --quiet suricata 2>/dev/null; then
        echo "Suricata está ativo"
    else
        echo -e "${YELLOW}AVISO: Suricata não está rodando (dashboard ainda funcionará)${NC}"
    fi
    
    if [ ! -r "/var/log/suricata/eve.json" ]; then
        echo -e "${YELLOW}AVISO: Arquivo /var/log/suricata/eve.json não está acessível${NC}"
    fi
else
    echo -e "${GREEN}Iniciando API Refatorada (Clean Architecture)...${NC}"
    APP_FILE="app_refactored.py"
    
    # Verificar se ClamAV está disponível
    if command -v clamscan &> /dev/null; then
        echo "ClamAV disponível"
    else
        echo -e "${YELLOW}AVISO: ClamAV não está instalado (funcionalidades de escaneamento limitadas)${NC}"
    fi
fi

echo ""
echo -e "${GREEN}Servidor será iniciado em:${NC}"
echo "  URL: http://localhost:5000"
echo "  Status: http://localhost:5000/api/status"
echo ""
echo -e "${YELLOW}Para parar o servidor, pressione Ctrl+C${NC}"
echo ""

# Executar aplicação
chmod +x "$APP_FILE" 2>/dev/null || true
exec python3 "$APP_FILE"

