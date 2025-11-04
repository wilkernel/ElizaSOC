#!/bin/bash
# Script completo para iniciar ElizaSOC com todos os serviços
# Autor: Wilker Junio Coelho Pimenta

set -e

cd "$(dirname "$0")"

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        ElizaSOC - Sistema de Monitoramento Completo          ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Função para verificar se um comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Função para iniciar serviço
start_service() {
    local service_name=$1
    local description=$2
    
    if systemctl is-active --quiet "$service_name" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $description já está ativo"
        return 0
    fi
    
    echo -e "${YELLOW}→${NC} Iniciando $description..."
    if sudo systemctl start "$service_name" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $description iniciado com sucesso"
        return 0
    else
        echo -e "${RED}✗${NC} Falha ao iniciar $description"
        return 1
    fi
}

# Verificar Python3
echo -e "${BLUE}[1/7]${NC} Verificando Python..."
if ! command_exists python3; then
    echo -e "${RED}ERRO: Python3 não está instalado${NC}"
    echo "Instale com: sudo apt install python3 python3-pip"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python3 está disponível"
echo ""

# Instalar dependências Python
echo -e "${BLUE}[2/7]${NC} Verificando dependências Python..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo -e "${YELLOW}Instalando dependências Python...${NC}"
    pip3 install -r requirements.txt --user 2>&1 | grep -v "Requirement already satisfied" || true
fi
echo -e "${GREEN}✓${NC} Dependências Python instaladas"
echo ""

# Criar diretórios
echo -e "${BLUE}[3/7]${NC} Criando diretórios..."
mkdir -p logs quarantine
echo -e "${GREEN}✓${NC} Diretórios criados"
echo ""

# Configurar Suricata
echo -e "${BLUE}[4/7]${NC} Configurando Suricata..."

# Verificar se Suricata está instalado
if ! command_exists suricata; then
    echo -e "${YELLOW}AVISO: Suricata não está instalado${NC}"
    echo "Execute: sudo bash configurar_suricata.sh"
else
    # Verificar permissões do eve.json
    if [ -f "/var/log/suricata/eve.json" ]; then
        if [ ! -r "/var/log/suricata/eve.json" ]; then
            echo -e "${YELLOW}Ajustando permissões do eve.json...${NC}"
            sudo chmod 644 /var/log/suricata/eve.json || true
        fi
    else
        echo -e "${YELLOW}AVISO: eve.json não existe. Configure o Suricata primeiro${NC}"
    fi
    
    # Tentar iniciar Suricata como serviço
    start_service "suricata" "Suricata IDS"
fi
echo ""

# Configurar ClamAV
echo -e "${BLUE}[5/7]${NC} Configurando ClamAV..."
if ! command_exists clamscan; then
    echo -e "${YELLOW}AVISO: ClamAV não está instalado${NC}"
    echo "Execute: sudo apt install clamav clamav-daemon"
else
    # Verificar se freshclam precisa rodar
    if [ ! -f "/var/log/clamav/freshclam.log" ] || \
       [ $(find /var/lib/clamav -name "*.cvd" -mtime +1 | wc -l) -gt 0 ]; then
        echo -e "${YELLOW}Atualizando base de dados do ClamAV...${NC}"
        sudo freshclam 2>&1 | grep -v "already up-to-date" || true
    fi
    
    start_service "clamav-daemon" "ClamAV Daemon"
    start_service "clamav-freshclam" "ClamAV Freshclam"
fi
echo ""

# Verificar estado final dos serviços
echo -e "${BLUE}[6/7]${NC} Estado dos Serviços:"
if systemctl is-active --quiet suricata 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Suricata IDS: ${GREEN}ATIVO${NC}"
else
    echo -e "${YELLOW}⚠${NC} Suricata IDS: ${YELLOW}INATIVO${NC}"
fi

if command_exists clamscan; then
    echo -e "${GREEN}✓${NC} ClamAV: ${GREEN}DISPONÍVEL${NC}"
else
    echo -e "${YELLOW}⚠${NC} ClamAV: ${YELLOW}NÃO INSTALADO${NC}"
fi

if [ -r "/var/log/suricata/eve.json" ]; then
    EVE_SIZE=$(stat -c%s /var/log/suricata/eve.json 2>/dev/null || echo 0)
    echo -e "${GREEN}✓${NC} Log do Suricata: ${GREEN}ACESSÍVEL${NC} ($EVE_SIZE bytes)"
else
    echo -e "${RED}✗${NC} Log do Suricata: ${RED}INACESSÍVEL${NC}"
fi
echo ""

# Iniciar a aplicação
echo -e "${BLUE}[7/7]${NC} Iniciando ElizaSOC Dashboard..."
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ElizaSOC está iniciando...${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}URLs de Acesso:${NC}"
echo -e "  Dashboard: ${GREEN}http://localhost:5000${NC}"
echo -e "  API Status: ${GREEN}http://localhost:5000/api/status${NC}"
echo ""
echo -e "${BLUE}Funcionalidades:${NC}"
echo -e "  ${GREEN}•${NC} Dashboard em tempo real"
echo -e "  ${GREEN}•${NC} Monitoramento de alertas Suricata"
echo -e "  ${GREEN}•${NC} Escaneamento ClamAV"
echo -e "  ${GREEN}•${NC} Logs em tempo real"
echo -e "  ${GREEN}•${NC} Gráficos e estatísticas"
echo ""
echo -e "${YELLOW}Para parar o servidor, pressione Ctrl+C${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Determinar qual aplicação executar
API_TYPE="${1:-refactored}"

if [ "$API_TYPE" = "legacy" ] || [ "$API_TYPE" = "old" ]; then
    APP_FILE="app.py"
    echo -e "${YELLOW}Usando API Legacy (app.py)...${NC}"
else
    APP_FILE="app.py"
    echo -e "${GREEN}Usando API Refatorada (Clean Architecture)...${NC}"
fi

# Executar aplicação
chmod +x "$APP_FILE" 2>/dev/null || true
exec python3 "$APP_FILE"

