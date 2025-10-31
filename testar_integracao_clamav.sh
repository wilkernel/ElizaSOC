#!/bin/bash
# Script de teste completo da integração ClamAV
# Autor: Wilker Junio Coelho Pimenta

echo "🧪 TESTE COMPLETO DA INTEGRAÇÃO CLAMAV"
echo "========================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_FILE="/tmp/eicar_test.com"

# Criar diretório de quarentena se não existir
echo "1️⃣ Criando diretório de quarentena..."
sudo mkdir -p /var/quarantine
sudo chmod 777 /var/quarantine
echo "✅ Diretório criado: /var/quarantine"
echo ""

# Criar arquivo EICAR de teste
echo "2️⃣ Criando arquivo de teste EICAR..."
echo 'X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*' > "$TEST_FILE"
echo "✅ Arquivo criado: $TEST_FILE"
echo ""

# Testar escaneamento direto
echo "3️⃣ Testando escaneamento direto com ClamAV..."
clamscan "$TEST_FILE" > /dev/null 2>&1
if [ $? -eq 1 ]; then
    echo "✅ ClamAV detectou o arquivo (esperado)"
else
    echo "❌ ClamAV não detectou o arquivo"
fi
echo ""

# Testar módulo Python
echo "4️⃣ Testando módulo Python clamav_scanner.py..."
cd "$SCRIPT_DIR"
result=$(python3 clamav_scanner.py "$TEST_FILE" 2>&1)
echo "$result" | head -15

# Verificar se foi detectado
if echo "$result" | grep -q '"infected": true'; then
    echo "✅ Módulo Python detectou vírus corretamente"
    
    # Verificar se foi colocado em quarentena
    if echo "$result" | grep -q '"quarantined": true'; then
        echo "✅ Arquivo foi movido para quarentena"
        ls -lh /var/quarantine/*.com 2>/dev/null | tail -1
    else
        echo "⚠️  Arquivo não foi colocado em quarentena (pode ser permissão)"
    fi
else
    echo "❌ Módulo Python não detectou vírus"
fi
echo ""

# Testar API (se dashboard estiver rodando)
echo "5️⃣ Testando API REST..."
if curl -s http://localhost:5000/api/viruses > /dev/null 2>&1; then
    echo "✅ API está acessível"
    
    # Tentar escanear via API
    scan_result=$(curl -s -X POST "http://localhost:5000/api/files/scan?filepath=$TEST_FILE")
    if echo "$scan_result" | grep -q '"infected"'; then
        echo "✅ API de escaneamento funcionando"
    else
        echo "⚠️  API retornou: $scan_result"
    fi
else
    echo "⚠️  Dashboard não está rodando (inicie com: bash iniciar_dashboard.sh)"
fi
echo ""

# Limpar
echo "6️⃣ Limpando arquivos de teste..."
rm -f "$TEST_FILE"
echo "✅ Limpeza concluída"
echo ""

echo "========================================"
echo "✅ TESTE CONCLUÍDO"
echo ""
echo "📊 Próximos passos:"
echo "  1. Verificar estatísticas em: http://localhost:5000"
echo "  2. Ver vírus detectados: http://localhost:5000/api/viruses"
echo "  3. Iniciar monitoramento automático: bash auto_scan_files.sh &"

