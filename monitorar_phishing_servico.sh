#!/bin/bash
# Monitoramento de phishing usando Suricata já ativo como serviço
# Autor: Wilker Junio Coelho Pimenta
# Requer: jq

LOG_DIR="/var/log/suricata"
EVE_JSON="$LOG_DIR/eve.json"
RELATORIO="$HOME/relatorio_phishing_$(date +%Y%m%d_%H%M%S).txt"

echo " Iniciando análise de alertas no Suricata ativo..."

# Verifica se o log existe
if [ ! -f "$EVE_JSON" ]; then
  echo " Arquivo $EVE_JSON não encontrado. Verifique se o Suricata está rodando como serviço."
  exit 1
fi

# Filtra alertas de phishing/malware/trojan
jq -r '
  select(.alert != null) |
  select(.alert.signature | test("PHISHING|TROJAN|MALWARE|SUSPICIOUS|MALICIOUS"; "i")) |
  "\(.timestamp) | \(.alert.signature) | \(.src_ip) -> \(.dest_ip)"
' "$EVE_JSON" > "$RELATORIO"

# Resultado
if [ -s "$RELATORIO" ]; then
  echo " Relatório gerado em: $RELATORIO"
  echo "-----------------------------------------"
  cat "$RELATORIO"
  echo "-----------------------------------------"
else
  echo " Nenhum domínio suspeito detectado no log atual."
fi
