#!/bin/bash
# Script para verificar o status do sistema de monitoramento
# Autor: Wilker Junio Coelho Pimenta

echo "=========================================="
echo "🔍 VERIFICAÇÃO DO SISTEMA DE MONITORAMENTO"
echo "=========================================="
echo ""

# 1. Verificar Suricata
echo "1️⃣ Verificando serviço Suricata..."
if systemctl is-active --quiet suricata; then
    echo "✅ Suricata está ATIVO"
    systemctl status suricata --no-pager -l | head -15
else
    echo "❌ Suricata NÃO está ativo"
fi
echo ""

# 2. Verificar jq
echo "2️⃣ Verificando dependências..."
if command -v jq &> /dev/null; then
    echo "✅ jq está instalado: $(which jq)"
else
    echo "❌ jq NÃO está instalado. Execute: sudo apt install jq"
fi
echo ""

# 3. Verificar permissões do diretório de logs
echo "3️⃣ Verificando diretório de logs..."
LOG_DIR="/var/log/suricata"
if [ -d "$LOG_DIR" ]; then
    echo "✅ Diretório $LOG_DIR existe"
    if [ -r "$LOG_DIR" ]; then
        echo "✅ Permissão de leitura: OK"
        ls -la "$LOG_DIR" | head -10
    else
        echo "⚠️  Sem permissão de leitura no diretório"
        echo "   Execute: sudo chmod 755 $LOG_DIR"
    fi
else
    echo "❌ Diretório $LOG_DIR não existe"
    echo "   Execute: sudo mkdir -p $LOG_DIR && sudo chown suricata:suricata $LOG_DIR"
fi
echo ""

# 4. Verificar arquivo eve.json
echo "4️⃣ Verificando arquivo eve.json..."
EVE_JSON="/var/log/suricata/eve.json"
if [ -f "$EVE_JSON" ]; then
    echo "✅ Arquivo $EVE_JSON existe"
    if [ -r "$EVE_JSON" ]; then
        SIZE=$(stat -c%s "$EVE_JSON" 2>/dev/null || echo "0")
        echo "   Tamanho: $SIZE bytes"
        if [ "$SIZE" -gt 0 ]; then
            echo "   Últimas 3 linhas:"
            tail -3 "$EVE_JSON" 2>/dev/null || echo "   (não foi possível ler)"
        fi
    else
        echo "⚠️  Arquivo existe mas sem permissão de leitura"
        echo "   Execute: sudo chmod 644 $EVE_JSON"
    fi
else
    echo "❌ Arquivo $EVE_JSON não existe"
    echo "   Possíveis causas:"
    echo "   - Suricata não conseguiu criar o arquivo (problema de permissão)"
    echo "   - eve-log não está configurado corretamente"
    echo "   Solução: Execute o script configurar_suricata.sh com sudo"
fi
echo ""

# 5. Verificar configuração do Suricata
echo "5️⃣ Verificando configuração do Suricata..."
if [ -r "/etc/suricata/suricata.yaml" ]; then
    if grep -q "eve-log" /etc/suricata/suricata.yaml 2>/dev/null; then
        echo "✅ eve-log encontrado na configuração"
        if grep -q "enabled: true" /etc/suricata/suricata.yaml 2>/dev/null; then
            echo "✅ eve-log parece estar habilitado"
        fi
    else
        echo "⚠️  eve-log não encontrado na configuração"
    fi
else
    echo "⚠️  Não foi possível ler /etc/suricata/suricata.yaml"
fi
echo ""

# 6. Verificar logs do sistema
echo "6️⃣ Verificando últimos erros do Suricata..."
if command -v journalctl &> /dev/null; then
    echo "Últimas mensagens do sistema:"
    journalctl -u suricata -n 5 --no-pager 2>/dev/null | grep -i "error\|permission\|eve" || echo "Nenhum erro recente encontrado"
fi
echo ""

echo "=========================================="
echo "📋 RECOMENDAÇÕES"
echo "=========================================="
if [ ! -f "$EVE_JSON" ]; then
    echo "1. Execute o script de configuração:"
    echo "   sudo bash configurar_suricata.sh"
    echo ""
    echo "2. Ou ajuste as permissões manualmente:"
    echo "   sudo mkdir -p /var/log/suricata"
    echo "   sudo chown -R suricata:suricata /var/log/suricata"
    echo "   sudo chmod 755 /var/log/suricata"
    echo "   sudo systemctl restart suricata"
    echo ""
fi

echo "3. Para executar o monitoramento:"
echo "   bash monitorar_phishing_servico.sh"
echo ""

echo "4. Para monitoramento contínuo com alertas por e-mail:"
echo "   bash alertas_email.sh &"
echo ""

