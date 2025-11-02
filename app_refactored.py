#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicação ElizaSOC Refatorada - Clean Architecture
Autor: Wilker Junio Coelho Pimenta
"""
import os
from src.presentation.api.app_factory import create_app

if __name__ == '__main__':
    # Criar diretórios necessários
    os.makedirs('logs', exist_ok=True)
    os.makedirs('quarantine', exist_ok=True)
    
    # Criar aplicação
    app = create_app()
    
    print(" Iniciando ElizaSOC API (Refatorada - Clean Architecture)...")
    print(" Acesse: http://localhost:5000")
    print(" API Docs: http://localhost:5000/api/status")
    
    # Modo desenvolvimento
    debug_mode = os.getenv('FLASK_ENV') != 'production'
    
    app.run(host='0.0.0.0', port=5000, debug=debug_mode, threaded=True)

