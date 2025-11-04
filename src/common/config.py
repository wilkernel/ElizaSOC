"""
Configuração do sistema ElizaSOC
"""
import os
from typing import Optional
from pathlib import Path


class Config:
    """Configuração centralizada do sistema"""
    
    # Flask
    FLASK_ENV: str = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG: bool = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Diretórios
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    QUARANTINE_DIR: str = os.getenv('QUARANTINE_DIR', str(BASE_DIR / 'quarantine'))
    LOG_DIR: str = os.getenv('LOG_DIR', str(BASE_DIR / 'logs'))
    
    # ClamAV
    CLAMAV_TIMEOUT: int = int(os.getenv('CLAMAV_TIMEOUT', '300'))
    
    # Suricata
    SURICATA_EVE_JSON_PATH: str = os.getenv('SURICATA_EVE_JSON', '/var/log/suricata/eve.json')
    
    # API
    API_HOST: str = os.getenv('API_HOST', '0.0.0.0')
    API_PORT: int = int(os.getenv('API_PORT', '5000'))
    
    # CORS
    CORS_ORIGINS: list = os.getenv(
        'CORS_ORIGINS',
        'http://localhost:5000,http://127.0.0.1:5000'
    ).split(',')
    
    # Production mode
    @property
    def is_production(self) -> bool:
        """Verifica se está em modo produção"""
        return self.FLASK_ENV == 'production'
    
    @property
    def is_development(self) -> bool:
        """Verifica se está em modo desenvolvimento"""
        return self.FLASK_ENV == 'development'


# Instância global de configuração
config = Config()
