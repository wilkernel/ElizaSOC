# Plano para transformar em aplicativo desktop

Objetivo
 - Empacotar o dashboard web + backend Python como um aplicativo desktop nativo (Windows/Linux/macOS).

Opções recomendadas

1) PyInstaller + pywebview (mais simples, cross-platform)
 - Fluxo:
   1. Empacotar a aplicação Python (Flask + módulos) com PyInstaller em um executável único.
   2. Usar `pywebview` (ou `webview`) para abrir a interface em uma janela nativa apontando para `http://127.0.0.1:PORT` iniciado pelo processo interno.
 - Vantagens: leve, não precisa de Node/Electron, mais simples de distribuir.
 - Comandos de exemplo (no venv):
```bash
# instalar
pip install pyinstaller pywebview

# criar um wrapper pequeno app_desktop.py que inicia o Flask internamente e abre pywebview
# empacotar
pyinstaller --onefile --add-data "templates:templates" --add-data "static:static" app_desktop.py
```

2) Electron / Tauri (mais polido UI, maior bundle)
 - Fluxo: embalar o frontend com Electron ou Tauri e iniciar o backend Flask localmente. Tauri resulta em binários menores, Electron é mais maduro.
 - Requer Node.js para build e configuração adicional.

Requisitos e cuidados
- Porta: escolher porta não privilegiada (ex.: 5000). Garantir que o app verifique disponibilidade e gere único lock (para evitar conflitos).
- Permissões: ações que modificam /var (ex.: quarentena) exigem sudo; ideal separar a UI (user) das ações privilegiadas (service ou helper rodando como root) ou usar polkit/systemd.
- Logs: embutir logs na pasta do usuário ou fornecer opção de configuração.

Passo inicial que eu posso implementar
 - Criar `app_desktop.py` que:
   - Inicia internamente o Flask app (sem executar `app.py` via subprocess).
   - Abre uma janela `pywebview` apontando para `http://127.0.0.1:5000`.
 - Adicionar instruções no `docs/` e um `requirements-desktop.txt` com `pywebview` e `pyinstaller`.

Se quiser, implemento um `app_desktop.py` de exemplo e o `requirements-desktop.txt` aqui no repo e testo localmente (requer venv e dependências instaladas).
