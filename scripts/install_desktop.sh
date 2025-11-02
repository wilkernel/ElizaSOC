#!/usr/bin/env bash
set -euo pipefail

# Instalador desktop (não destrutivo)
# O que faz:
# - cria/atualiza .venv no diretório do projeto
# - instala dependências do requirements.txt e requirements-desktop.txt
# - cria um wrapper executável em /usr/local/bin/monitoramento-dashboard (requer sudo)
# - cria um arquivo .desktop para aparecer no menu (requer sudo)

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
PY="$VENV_DIR/bin/python"
PIP="$VENV_DIR/bin/pip"
WRAPPER_PATH="/usr/local/bin/monitoramento-dashboard"
DESKTOP_PATH="/usr/share/applications/monitoramento-suricata-dashboard.desktop"

echo "Instalador do Monitoramento Suricata - Desktop"
echo "Projeto: $PROJECT_DIR"

echo "1) Criando/atualizando virtualenv em $VENV_DIR"
if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

echo "Ativando venv e atualizando pip"
source "$VENV_DIR/bin/activate"
python -m pip install --upgrade pip setuptools wheel

echo "2) Instalando dependências do projeto"
if [ -f "$PROJECT_DIR/requirements.txt" ]; then
  "$PIP" install -r "$PROJECT_DIR/requirements.txt"
fi

if [ -f "$PROJECT_DIR/requirements-desktop.txt" ]; then
  "$PIP" install -r "$PROJECT_DIR/requirements-desktop.txt"
fi

echo "3) Criando wrapper executável em $WRAPPER_PATH (requer sudo)"
TMP_WRAPPER="$(mktemp)"
cat > "$TMP_WRAPPER" <<EOF
#!/usr/bin/env bash
cd "$PROJECT_DIR"
source "$VENV_DIR/bin/activate"
exec "$PY" "$PROJECT_DIR/app_desktop.py" "\$@"
EOF
sudo mv "$TMP_WRAPPER" "$WRAPPER_PATH"
sudo chmod 755 "$WRAPPER_PATH"

echo "4) Criando atalho .desktop em $DESKTOP_PATH (requer sudo)"
ICON_PATH="$PROJECT_DIR/static/css/style.css"
# If you have an icon file, set ICON_PATH to it; using stylesheet path as placeholder
TMP_DESKTOP="$(mktemp)"
cat > "$TMP_DESKTOP" <<EOF
[Desktop Entry]
Name=Monitoramento Suricata
Comment=Dashboard de monitoramento (Suricata + ClamAV)
Exec=$WRAPPER_PATH
Icon=$ICON_PATH
Terminal=false
Type=Application
Categories=Utility;Security;
EOF
sudo mv "$TMP_DESKTOP" "$DESKTOP_PATH"
sudo chmod 644 "$DESKTOP_PATH"

echo "Instalação concluída. Para iniciar o app, execute:
  monitoramento-dashboard
ou abra o atalho no menu de aplicações."

echo "Observações:"
echo " - O instalador precisa de sudo para instalar o atalho e o wrapper em locais do sistema." 
echo " - Se preferir não instalar no sistema, rode localmente:"
echo "     source .venv/bin/activate && python app_desktop.py"
