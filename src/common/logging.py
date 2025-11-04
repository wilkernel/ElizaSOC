"""
Configuração de logging estruturado
"""
import logging
import sys
from typing import Optional
import json
from datetime import datetime

try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False


class JSONFormatter(logging.Formatter):
    """Formatter JSON para logs estruturados"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formata log como JSON"""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Adicionar campos extras
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        # Adicionar exception info se houver
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def setup_logging(level: str = 'INFO', use_json: bool = False) -> None:
    """
    Configura logging do sistema
    
    Args:
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        use_json: Se True, usa formato JSON (para produção)
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configurar root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remover handlers existentes
    root_logger.handlers.clear()
    
    # Criar handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # Escolher formatter
    if use_json or STRUCTLOG_AVAILABLE:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    
    # Configurar loggers específicos
    logging.getLogger('src').setLevel(log_level)
    logging.getLogger('flask').setLevel(logging.WARNING)  # Reduzir logs do Flask


def get_logger(name: str) -> logging.Logger:
    """
    Obtém um logger configurado
    
    Args:
        name: Nome do logger (geralmente __name__)
        
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)


# Configurar logging padrão ao importar
setup_logging()
