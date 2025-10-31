#!/bin/bash
# Monitora diretório do Suricata e escaneia arquivos automaticamente
# Autor: Wilker Junio Coelho Pimenta

SURICATA_FILES_DIR="/var/log/suricata/files"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QUARANTINE_DIR="/var/quarantine"

# Criar diretórios se não existirem
mkdir -p "$QUARANTINE_DIR"
mkdir -p "$SURICATA_FILES_DIR"

echo "🔍 Iniciando monitoramento automático de arquivos..."
echo "📁 Diretório monitorado: $SURICATA_FILES_DIR"
echo "📁 Quarentena: $QUARANTINE_DIR"
echo ""

# Verificar se inotify-tools está instalado
if ! command -v inotifywait &> /dev/null; then
    echo "⚠️  inotify-tools não está instalado. Instalando..."
    sudo apt install -y inotify-tools
fi

# Função para escanear arquivo
scan_file() {
    local file="$1"
    
    if [ ! -f "$file" ]; then
        return
    fi
    
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Escaneando: $(basename "$file")"
    
    # Escanear com ClamAV via Python
    result=$(python3 "$SCRIPT_DIR/clamav_scanner.py" "$file" 2>/dev/null)
    
    # Verificar se foi detectado como vírus
    if echo "$result" | grep -q '"infected": true'; then
        virus_name=$(echo "$result" | grep -o '"virus_name": "[^"]*' | cut -d'"' -f4)
        echo "🚨 VÍRUS DETECTADO: $(basename "$file") - $virus_name"
        echo "$(date '+%Y-%m-%d %H:%M:%S') | VÍRUS | $file | $virus_name" >> "$SCRIPT_DIR/logs/virus_detections.log"
    else
        echo "✅ Limpo: $(basename "$file")"
    fi
}

# Monitorar diretório continuamente
echo "✅ Monitoramento ativo. Pressione Ctrl+C para parar."
echo ""

inotifywait -m -e create --format '%w%f' "$SURICATA_FILES_DIR" 2>/dev/null | while read file; do
    # Aguardar um pouco para garantir que o arquivo foi completamente escrito
    sleep 2
    
    if [ -f "$file" ]; then
        scan_file "$file"
    fi
done

