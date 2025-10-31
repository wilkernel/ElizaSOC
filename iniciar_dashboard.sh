#!/bin/bash
# Script para iniciar o Dashboard Web
# Autor: Wilker Junio Coelho Pimenta

cd "$(dirname "$0")"

echo "🚀 Iniciando Dashboard de Monitoramento Suricata"
echo ""

# Verificar se Python3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não está instalado. Instale com: sudo apt install python3 python3-pip"
    exit 1
fi

# Verificar se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não está instalado. Instale com: sudo apt install python3-pip"
    exit 1
fi

# Verificar se as dependências estão instaladas
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Instalando dependências Python..."
    pip3 install -r requirements.txt --user
    if [ $? -ne 0 ]; then
        echo "❌ Erro ao instalar dependências. Tente: pip3 install -r requirements.txt"
        exit 1
    fi
fi

# Verificar se o arquivo eve.json existe e é acessível
if [ ! -r "/var/log/suricata/eve.json" ]; then
    echo "⚠️  AVISO: Arquivo /var/log/suricata/eve.json não está acessível"
    echo "   Execute: sudo chmod 644 /var/log/suricata/eve.json"
    echo ""
    echo "   Ou ajuste as permissões do diretório:"
    echo "   sudo chmod 755 /var/log/suricata"
    echo ""
fi

# Verificar se o Suricata está rodando
if systemctl is-active --quiet suricata; then
    echo "✅ Suricata está ativo"
else
    echo "⚠️  Suricata não está rodando. Inicie com: sudo systemctl start suricata"
    echo ""
fi

echo ""
echo "🌐 Iniciando servidor web..."
echo "📊 Acesse: http://localhost:5000"
echo "   Para parar o servidor, pressione Ctrl+C"
echo ""

# Tornar o script Python executável
chmod +x app.py

# Executar o aplicativo
python3 app.py


