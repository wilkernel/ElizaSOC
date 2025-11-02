#!/usr/bin/env bash
# Wrapper script: delega a execução para scripts/setup/configurar_suricata.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/scripts/setup/configurar_suricata.sh" "$@"
