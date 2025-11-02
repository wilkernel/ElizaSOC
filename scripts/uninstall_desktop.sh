#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
WRAPPER_PATH="/usr/local/bin/monitoramento-dashboard"
DESKTOP_PATH="/usr/share/applications/monitoramento-suricata-dashboard.desktop"

echo "Desinstalador do Monitoramento Suricata - Desktop"

if [ -f "$WRAPPER_PATH" ]; then
  echo "Removendo wrapper: $WRAPPER_PATH"
  sudo rm -f "$WRAPPER_PATH"
else
  echo "Wrapper não encontrado: $WRAPPER_PATH"
fi

if [ -f "$DESKTOP_PATH" ]; then
  echo "Removendo atalho: $DESKTOP_PATH"
  sudo rm -f "$DESKTOP_PATH"
else
  echo "Atalho .desktop não encontrado: $DESKTOP_PATH"
fi

read -r -p "Deseja remover o virtualenv em $VENV_DIR ? [y/N]: " CONFIRM
if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
  if [ -d "$VENV_DIR" ]; then
    echo "Removendo virtualenv..."
    rm -rf "$VENV_DIR"
  else
    echo "Virtualenv não encontrado: $VENV_DIR"
  fi
else
  echo "Preservando virtualenv."
fi

echo "Desinstalação concluída."
