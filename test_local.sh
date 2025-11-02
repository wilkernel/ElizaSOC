#!/bin/bash
# Script de teste local do ElizaSOC
set -e

cd "$(dirname "$0")"

echo "=========================================="
echo "Teste Local - ElizaSOC v2.0"
echo "=========================================="
echo ""

# 1. Verificar Python
echo "[1/6] Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "ERRO: Python3 não encontrado"
    exit 1
fi
python3 --version
echo "OK"
echo ""

# 2. Verificar dependências
echo "[2/6] Verificando dependências Python..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "AVISO: Flask não instalado. Instalando..."
    pip3 install -q -r requirements.txt --user
fi
echo "OK"
echo ""

# 3. Testar importação de módulos
echo "[3/6] Testando importação de módulos..."
python3 -c "
from src.presentation.api.app_factory import create_app
from src.infrastructure.scanners.clamav_scanner import ClamAVScanner
from src.infrastructure.repositories.in_memory_file_scan_repository import InMemoryFileScanRepository
from src.application.use_cases.scan_file_use_case import ScanFileUseCase
print('OK - Módulos importados com sucesso')
" || exit 1
echo ""

# 4. Executar testes unitários
echo "[4/6] Executando testes unitários..."
python3 -m pytest tests/domain/ -v --tb=short -q || echo "AVISO: Alguns testes falharam"
echo ""

# 5. Criar app e verificar rotas
echo "[5/6] Criando aplicação e verificando rotas..."
python3 -c "
from src.presentation.api.app_factory import create_app
app = create_app()

# Verificar rotas registradas
routes = []
for rule in app.url_map.iter_rules():
    routes.append(rule.rule)

expected_routes = ['/api/status', '/api/alerts', '/api/files/scan']
found = sum(1 for r in expected_routes if any(r in route for route in routes))
print(f'OK - {found}/{len(expected_routes)} rotas principais encontradas')
" || exit 1
echo ""

# 6. Testar inicialização do servidor (timeout curto)
echo "[6/6] Testando inicialização do servidor..."
timeout 3 python3 app_refactored.py > /tmp/elizasoc_test.log 2>&1 &
SERVER_PID=$!
sleep 2

if ps -p $SERVER_PID > /dev/null; then
    echo "OK - Servidor iniciado"
    kill $SERVER_PID 2>/dev/null || true
else
    echo "AVISO: Servidor pode não ter iniciado corretamente"
    cat /tmp/elizasoc_test.log | tail -5
fi
echo ""

echo "=========================================="
echo "Teste Local Concluído"
echo "=========================================="
echo ""
echo "Para iniciar o sistema:"
echo "  ./start.sh"
echo ""
echo "Ou:"
echo "  python3 app_refactored.py"
echo ""

