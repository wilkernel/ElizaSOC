"""
Factory para criação da aplicação Flask
Seguindo Clean Architecture - Dependency Injection
"""
import os
from flask import Flask, render_template
from flask_cors import CORS

from src.common.config import config
from src.common.logging import get_logger

from src.infrastructure.scanners.clamav_scanner import ClamAVScanner
from src.infrastructure.repositories.in_memory_alert_repository import InMemoryAlertRepository
from src.infrastructure.repositories.in_memory_file_scan_repository import InMemoryFileScanRepository
from src.infrastructure.repositories.in_memory_event_repository import InMemoryEventRepository
from src.infrastructure.repositories.in_memory_ioc_repository import InMemoryIOCRepository
from src.infrastructure.services.event_correlator import SimpleEventCorrelator
from src.infrastructure.services.threat_intelligence_service import SimpleThreatIntelligenceService

from src.application.use_cases.scan_file_use_case import ScanFileUseCase
from src.application.use_cases.correlate_events_use_case import CorrelateEventsUseCase
from src.application.use_cases.analyze_threat_use_case import AnalyzeThreatUseCase

from src.presentation.api.controllers.alerts_controller import alerts_bp, register_alerts_routes
from src.presentation.api.controllers.files_controller import files_bp, register_files_routes
from src.presentation.api.controllers.dashboard_controller import dashboard_bp, register_dashboard_routes

logger = get_logger(__name__)


def create_app(flask_config=None):
    """
    Factory para criar aplicação Flask com injeção de dependências
    
    Args:
        flask_config: Dicionário de configuração Flask (opcional)
        
    Returns:
        Flask app configurada
    """
    # Determinar diretório raiz do projeto
    base_dir = config.BASE_DIR
    
    app = Flask(
        __name__,
        template_folder=str(base_dir / 'templates'),
        static_folder=str(base_dir / 'static')
    )
    
    # Configuração Flask
    if flask_config:
        app.config.update(flask_config)
    else:
        app.config['SECRET_KEY'] = config.SECRET_KEY
        app.config['PRODUCTION_MODE'] = config.is_production
        app.config['DEBUG'] = config.FLASK_DEBUG
    
    # CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": config.CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    logger.info("Aplicação Flask criada com sucesso")
    
    # Inicializar dependências (Infrastructure Layer)
    # Em produção, isso seria feito via DI Container
    file_scanner = ClamAVScanner()
    alert_repository = InMemoryAlertRepository()
    file_scan_repository = InMemoryFileScanRepository()
    event_repository = InMemoryEventRepository()
    ioc_repository = InMemoryIOCRepository()
    
    # Inicializar serviços (Infrastructure Layer)
    event_correlator = SimpleEventCorrelator(event_repository)
    threat_intelligence_service = SimpleThreatIntelligenceService(ioc_repository)
    
    # Inicializar casos de uso (Application Layer)
    scan_file_use_case = ScanFileUseCase(
        file_scanner=file_scanner,
        file_scan_repository=file_scan_repository,
    )
    
    correlate_events_use_case = CorrelateEventsUseCase(
        event_correlator=event_correlator,
        event_repository=event_repository,
        alert_repository=alert_repository,
    )
    
    analyze_threat_use_case = AnalyzeThreatUseCase(
        threat_intelligence_service=threat_intelligence_service,
    )
    
    # Registrar dependências na aplicação para acesso nos controllers
    @app.before_request
    def inject_dependencies():
        """Injeta dependências no contexto de requisição"""
        from flask import g
        
        g.alert_repository = alert_repository
        g.file_scan_repository = file_scan_repository
        g.event_repository = event_repository
        g.scan_file_use_case = scan_file_use_case
        g.correlate_events_use_case = correlate_events_use_case
        g.analyze_threat_use_case = analyze_threat_use_case
    
    # Registrar rotas com dependências injetadas
    register_alerts_routes(alerts_bp, alert_repository)
    register_files_routes(files_bp, file_scan_repository, scan_file_use_case)
    register_dashboard_routes(dashboard_bp)
    
    # Registrar blueprints
    app.register_blueprint(alerts_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(dashboard_bp)
    
    # Rota raiz - renderiza dashboard
    @app.route('/')
    def index():
        """Página principal do dashboard"""
        return render_template('index.html')
    
    return app

