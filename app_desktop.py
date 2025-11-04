#!/usr/bin/env python3
"""
Wrapper desktop minimal: inicia o Flask app embutido e abre uma janela nativa com pywebview.
Uso (no venv):
  pip install -r requirements-desktop.txt
  python app_desktop.py

Este arquivo é um protótipo. Para empacotar: pyinstaller --onefile app_desktop.py
"""
import threading
import time
import webbrowser
import sys

try:
    # importar o Flask app (Clean Architecture)
    from src.presentation.api.app_factory import create_app
    flask_app = create_app()
except Exception as e:
    print("Erro ao importar app:", e)
    sys.exit(1)


def run_flask():
    # Rodar o servidor Flask em thread separada
    # Desabilitar reloader para evitar múltiplos processos
    flask_app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)


def wait_for_server(url='http://127.0.0.1:5000', timeout=10.0):
    import urllib.request
    start = time.time()
    while True:
        try:
            with urllib.request.urlopen(url, timeout=1) as resp:
                return True
        except Exception:
            if time.time() - start > timeout:
                return False
            time.sleep(0.2)


def main():
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()

    print('Aguardando servidor Flask iniciar...')
    ok = wait_for_server('http://127.0.0.1:5000', timeout=15.0)
    if not ok:
        print('Servidor não respondeu em http://127.0.0.1:5000 dentro do timeout.')
        print('Verifique logs em logs/dashboard.log ou execute python app.py manualmente.')
        # abrir no navegador mesmo assim
        webbrowser.open('http://127.0.0.1:5000')
        return

    try:
        import webview
    except Exception as e:
        print('pywebview não está instalado ou não foi possível importar:', e)
        print('Abrindo no navegador padrão...')
        webbrowser.open('http://127.0.0.1:5000')
        return

    # Criar janela nativa apontando para o dashboard
    window = webview.create_window('Monitoramento Suricata - Dashboard', 'http://127.0.0.1:5000', width=1200, height=800)
    webview.start()


if __name__ == '__main__':
    main()
