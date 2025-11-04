#!/bin/bash
# Script para testar o sistema ElizaSOC
# Facilita a geração de dados de teste e verificação do sistema

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GENERATE_SCRIPT="$SCRIPT_DIR/scripts/generate_test_alerts.py"
EVE_JSON="/var/log/suricata/eve.json"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 não encontrado. Por favor, instale Python3."
        exit 1
    fi
    print_success "Python3 encontrado: $(python3 --version)"
}

check_file_permissions() {
    if [ ! -f "$EVE_JSON" ]; then
        print_info "Arquivo $EVE_JSON não existe. Será criado quando necessário."
        
        # Verificar se temos permissão para criar
        EVE_DIR=$(dirname "$EVE_JSON")
        if [ ! -w "$EVE_DIR" ] && [ "$EUID" -ne 0 ]; then
            print_error "Sem permissão para criar $EVE_JSON"
            print_info "Use: sudo $0 ou especifique um arquivo local"
            return 1
        fi
    else
        if [ ! -w "$EVE_JSON" ] && [ "$EUID" -ne 0 ]; then
            print_error "Sem permissão para escrever em $EVE_JSON"
            print_info "Use: sudo $0 ou especifique um arquivo local"
            return 1
        fi
        print_success "Arquivo $EVE_JSON encontrado e acessível"
    fi
    return 0
}

generate_test_data() {
    local num=${1:-10}
    local interval=${2:-1}
    local file=${3:-"$EVE_JSON"}
    
    print_header "Gerando $num alertas de teste"
    
    if [ "$file" != "$EVE_JSON" ] || check_file_permissions; then
        python3 "$GENERATE_SCRIPT" -n "$num" -i "$interval" -f "$file"
        print_success "Dados de teste gerados com sucesso!"
        
        if [ -f "$file" ]; then
            local count=$(grep -c '"event_type":"alert"' "$file" 2>/dev/null || echo "0")
            print_info "Total de alertas no arquivo: $count"
        fi
    else
        print_info "Usando arquivo local: ~/eve_test.json"
        python3 "$GENERATE_SCRIPT" -n "$num" -i "$interval" -f ~/eve_test.json
        print_success "Dados de teste gerados em ~/eve_test.json"
    fi
}

generate_continuous() {
    local interval=${1:-2}
    local file=${2:-"$EVE_JSON"}
    
    print_header "Gerando alertas continuamente (Ctrl+C para parar)"
    print_info "Intervalo: ${interval} segundos"
    
    if [ "$file" != "$EVE_JSON" ] || check_file_permissions; then
        python3 "$GENERATE_SCRIPT" --continuous -i "$interval" -f "$file"
    else
        print_info "Usando arquivo local: ~/eve_test.json"
        python3 "$GENERATE_SCRIPT" --continuous -i "$interval" -f ~/eve_test.json
    fi
}

check_dashboard() {
    print_header "Verificando Dashboard"
    
    if curl -s http://localhost:5000 > /dev/null 2>&1; then
        print_success "Dashboard está rodando em http://localhost:5000"
        return 0
    else
        print_error "Dashboard não está rodando"
        print_info "Inicie o dashboard com: python3 app.py"
        return 1
    fi
}

show_stats() {
    local file=${1:-"$EVE_JSON"}
    
    if [ ! -f "$file" ]; then
        print_error "Arquivo $file não encontrado"
        return 1
    fi
    
    print_header "Estatísticas do arquivo $file"
    
    local total_alerts=$(grep -c '"event_type":"alert"' "$file" 2>/dev/null || echo "0")
    local total_flows=$(grep -c '"event_type":"flow"' "$file" 2>/dev/null || echo "0")
    local total_dns=$(grep -c '"event_type":"dns"' "$file" 2>/dev/null || echo "0")
    local file_size=$(du -h "$file" | cut -f1)
    
    echo "Total de Alertas: $total_alerts"
    echo "Total de Flows: $total_flows"
    echo "Total de DNS: $total_dns"
    echo "Tamanho do arquivo: $file_size"
    
    if [ "$total_alerts" -gt 0 ]; then
        echo ""
        print_info "Último alerta:"
        tail -n 1 "$file" | python3 -m json.tool 2>/dev/null | head -n 20 || tail -n 1 "$file"
    fi
}

show_help() {
    cat << EOF
Uso: $0 [comando] [opções]

Comandos:
  generate [n] [interval] [file]
    Gera n alertas de teste (padrão: 10, intervalo: 1s)
    Exemplo: $0 generate 50 0.5

  continuous [interval] [file]
    Gera alertas continuamente (padrão: intervalo 2s)
    Exemplo: $0 continuous 1

  stats [file]
    Mostra estatísticas do arquivo eve.json
    Exemplo: $0 stats

  check
    Verifica se o dashboard está rodando

  test
    Executa teste completo: gera dados e verifica dashboard

  help
    Mostra esta ajuda

Exemplos:
  # Gerar 20 alertas rapidamente
  $0 generate 20 0.1

  # Gerar alertas continuamente para testar streaming
  $0 continuous 1

  # Ver estatísticas
  $0 stats

  # Teste completo
  $0 test
EOF
}

run_test() {
    print_header "Executando Teste Completo"
    
    check_python
    
    echo ""
    print_info "1. Gerando dados de teste..."
    generate_test_data 30 0.3
    
    echo ""
    print_info "2. Verificando estatísticas..."
    show_stats
    
    echo ""
    print_info "3. Verificando dashboard..."
    if check_dashboard; then
        print_success "Teste completo! Abra http://localhost:5000 no navegador"
        print_info "Vá para a aba 'Logs em Tempo Real' e clique em 'Iniciar Monitoramento'"
        print_info "Depois execute: $0 continuous 1 (em outro terminal) para ver alertas em tempo real"
    else
        print_error "Dashboard não está rodando. Inicie com: python3 app.py"
    fi
}

# Main
case "${1:-help}" in
    generate)
        generate_test_data "${2:-10}" "${3:-1}" "${4:-}"
        ;;
    continuous)
        generate_continuous "${2:-2}" "${3:-}"
        ;;
    stats)
        show_stats "${2:-}"
        ;;
    check)
        check_dashboard
        ;;
    test)
        run_test
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Comando desconhecido: $1"
        echo ""
        show_help
        exit 1
        ;;
esac

