#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicação ElizaSOC Refatorada - Clean Architecture
Entrypoint principal do sistema
Autor: Wilker Junio Coelho Pimenta
"""
import os
from pathlib import Path
from src.presentation.api.app_factory import create_app
from src.common.config import config
from src.common.logging import setup_logging, get_logger

# Configurar logging
log_level = 'DEBUG' if config.is_development else 'INFO'
setup_logging(level=log_level, use_json=config.is_production)
logger = get_logger(__name__)

if __name__ == '__main__':
    # Criar diretórios necessários
    os.makedirs(config.LOG_DIR, exist_ok=True)
    os.makedirs(config.QUARANTINE_DIR, exist_ok=True)
    
    # Criar aplicação
    logger.info("Iniciando ElizaSOC API (Clean Architecture)")
    app = create_app()
    
    # Mensagens de inicialização
    print("\n" + "="*60)
    print("  ElizaSOC API - Sistema de Detecção e Resposta a Ameaças")
    print("  Arquitetura: Clean Architecture + SOLID + TDD")
    print("="*60)
    print(f"  Ambiente: {config.FLASK_ENV}")
    print(f"  Debug: {config.FLASK_DEBUG}")
    print(f"  URL: http://{config.API_HOST}:{config.API_PORT}")
    print(f"  Status: http://{config.API_HOST}:{config.API_PORT}/api/status")
    print("="*60 + "\n")
    
    logger.info(f"Servidor iniciando em {config.API_HOST}:{config.API_PORT}")
    
    # Executar aplicação
    app.run(
        host=config.API_HOST,
        port=config.API_PORT,
        debug=config.FLASK_DEBUG and config.is_development,
        threaded=True
    )

