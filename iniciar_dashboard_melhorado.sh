#!/bin/bash
# Script melhorado para iniciar o Dashboard
# Autor: Wilker Junio Coelho Pimenta

cd "$(dirname "$0")"

echo "🚀 Iniciando Dashboard de Monitoramento Suricata"
echo ""

# Verificar se Python3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não está instalado."
    exit 1
fi

# Verificar se o módulo ClamAV pode ser importado
echo "🔍 Verificando integração ClamAV..."
if python3 -c "from clamav_scanner import scan_file" 2>/dev/null; then
    echo "✅ ClamAV integrado com sucesso"
else
    echo "⚠️  ClamAV não disponível (funcionalidades básicas ainda funcionam)"
fi

# Verificar se o arquivo eve.json existe e é acessível
if [ -r "/var/log/suricata/eve.json" ]; then
    echo "✅ Arquivo eve.json acessível"
else
    echo "⚠️  AVISO: Arquivo /var/log/suricata/eve.json não está acessível"
    echo "   O dashboard funcionará, mas sem dados do Suricata"
fi

# Verificar se o Suricata está rodando
if systemctl is-active --quiet suricata 2>/dev/null; then
    echo "✅ Suricata está ativo"
else
    echo "⚠️  Suricata não está rodando (dashboard ainda funcionará)"
fi

# Definir modo desenvolvimento para facilitar debug
export FLASK_ENV=development
unset PRODUCTION_MODE

echo ""
echo "🌐 Iniciando servidor web..."
echo "📊 Acesse: http://localhost:5000"
echo "   OU de outra máquina: http://192.168.100.67:5000"
echo ""
echo "   Para parar o servidor, pressione Ctrl+C"
echo ""

# Tornar o script Python executável
chmod +x app.py

# Executar o aplicativo
python3 app.py

