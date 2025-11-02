#!/bin/bash
# Sistema de alertas por e-mail para monitoramento de phishing com Suricata
# Autor: Wilker Junio Coelho Pimenta
# Requer: jq, mailx ou sendmail

# Configurações de e-mail (personalize conforme necessário)
FROM_EMAIL="${FROM_EMAIL:-alerts@yourdomain.com}"
TO_EMAIL="${TO_EMAIL:-admin@yourdomain.com}"
SMTP_SERVER="${SMTP_SERVER:-localhost}"
SMTP_PORT="${SMTP_PORT:-25}"

# Arquivos de log
LOG_DIR="/var/log/suricata"
EVE_JSON="$LOG_DIR/eve.json"
ALERT_LOG="$HOME/ElizaSOC/logs/alertas_phishing.log"

# Função para enviar e-mail
send_alert_email() {
    local timestamp="$1"
    local signature="$2"
    local src_ip="$3"
    local dest_ip="$4"
    local severity="$5"

    local subject="[ALERTA SURICATA] Domínio suspeito detectado"
    local body="Alerta de Phishing Detectado

Data/Hora: $timestamp
Assinatura: $signature
IP Origem: $src_ip
IP Destino: $dest_ip
Severidade: $severity

Este é um alerta automático gerado pelo sistema de monitoramento Suricata.
Verifique os logs em $EVE_JSON para mais detalhes."

    echo "$body" | mailx -s "$subject" -r "$FROM_EMAIL" "$TO_EMAIL" 2>/dev/null || \
    echo "$body" | sendmail -f "$FROM_EMAIL" "$TO_EMAIL" 2>/dev/null || \
    echo "Erro: Não foi possível enviar e-mail. Verifique se mailx ou sendmail estão instalados."
}

# Verifica se o log existe
if [ ! -f "$EVE_JSON" ]; then
    echo " Arquivo $EVE_JSON não encontrado. Verifique se o Suricata está rodando."
    exit 1
fi

# Cria diretório de logs se não existir
mkdir -p "$(dirname "$ALERT_LOG")"

# Monitora o arquivo eve.json em tempo real e filtra alertas
tail -f "$EVE_JSON" | jq -r '
  select(.alert != null) |
  select(.alert.signature | test("PHISHING|TROJAN|MALWARE|SUSPICIOUS|MALICIOUS|BLACKLIST"; "i")) |
  "\(.timestamp)|\(.alert.signature)|\(.src_ip)|\(.dest_ip)|\(.alert.severity)"' | while IFS='|' read -r timestamp signature src_ip dest_ip severity; do

    # Log do alerta
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ALERTA: $signature | $src_ip -> $dest_ip | Severidade: $severity" >> "$ALERT_LOG"

    # Envia e-mail de alerta
    send_alert_email "$timestamp" "$signature" "$src_ip" "$dest_ip" "$severity"

    echo " Alerta enviado: $signature"
done
