#!/usr/bin/env bash
# Start script for ElizaSOC - Redireciona para start.sh na raiz
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/../start.sh" "$@"
