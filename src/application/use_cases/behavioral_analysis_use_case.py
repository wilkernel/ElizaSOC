"""
Use Case: Behavioral Analysis
Caso de uso para análise comportamental de eventos
"""
from typing import List

from src.domain.services.behavioral_analyzer import BehavioralAnalyzer
from src.domain.repositories.event_repository import EventRepository
from src.domain.repositories.alert_repository import AlertRepository
from src.domain.entities.event import SecurityEvent
from src.domain.entities.alert import Alert


class BehavioralAnalysisUseCase:
    """
    Caso de uso para análise comportamental
    Coordena o analyzer e repositórios
    """
    
    def __init__(
        self,
        behavioral_analyzer: BehavioralAnalyzer,
        event_repository: EventRepository,
        alert_repository: AlertRepository,
    ):
        """
        Inicializa o caso de uso
        
        Args:
            behavioral_analyzer: Serviço de análise comportamental
            event_repository: Repositório de eventos
            alert_repository: Repositório de alertas
        """
        self.behavioral_analyzer = behavioral_analyzer
        self.event_repository = event_repository
        self.alert_repository = alert_repository
    
    def execute(self, events: List[SecurityEvent]) -> List[Alert]:
        """
        Executa análise comportamental de eventos
        
        Args:
            events: Lista de eventos a analisar
            
        Returns:
            Lista de alertas gerados
        """
        # Salvar eventos no repositório
        saved_events = []
        for event in events:
            saved_event = self.event_repository.save(event)
            saved_events.append(saved_event)
        
        # Analisar eventos
        alerts = self.behavioral_analyzer.analyze_events(saved_events)
        
        # Salvar alertas
        saved_alerts = []
        for alert in alerts:
            saved_alert = self.alert_repository.save(alert)
            saved_alerts.append(saved_alert)
        
        return saved_alerts
    
    def detect_zero_day(self, event: SecurityEvent) -> bool:
        """
        Detecta possível zero-day em um evento
        
        Args:
            event: Evento a analisar
            
        Returns:
            True se possível zero-day
        """
        # Salvar evento
        saved_event = self.event_repository.save(event)
        
        # Verificar zero-day
        return self.behavioral_analyzer.detect_zero_day(saved_event)

