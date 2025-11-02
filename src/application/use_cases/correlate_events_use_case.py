"""
Use Case: Correlate Events
Casos de uso para correlação de eventos de segurança
"""
from typing import List

from src.domain.services.event_correlator import EventCorrelator
from src.domain.repositories.event_repository import EventRepository
from src.domain.repositories.alert_repository import AlertRepository
from src.domain.entities.event import SecurityEvent
from src.domain.entities.alert import Alert


class CorrelateEventsUseCase:
    """
    Caso de uso para correlação de eventos
    Coordena o correlator, repositórios de eventos e alertas
    """
    
    def __init__(
        self,
        event_correlator: EventCorrelator,
        event_repository: EventRepository,
        alert_repository: AlertRepository,
    ):
        """
        Inicializa o caso de uso
        
        Args:
            event_correlator: Serviço de correlação
            event_repository: Repositório de eventos
            alert_repository: Repositório de alertas
        """
        self.event_correlator = event_correlator
        self.event_repository = event_repository
        self.alert_repository = alert_repository
    
    def execute(self, events: List[SecurityEvent]) -> List[Alert]:
        """
        Executa correlação de eventos
        
        Args:
            events: Lista de eventos a correlacionar
            
        Returns:
            Lista de alertas correlacionados
        """
        # Salvar eventos no repositório
        for event in events:
            saved_event = self.event_repository.save(event)
            # Adicionar relacionamentos
            related = self.event_correlator.find_related_events(saved_event)
            for rel_event in related:
                saved_event.add_related_event(rel_event.id)
        
        # Correlacionar eventos
        alerts = self.event_correlator.correlate_events(events)
        
        # Salvar alertas correlacionados
        saved_alerts = []
        for alert in alerts:
            saved_alert = self.alert_repository.save(alert)
            saved_alerts.append(saved_alert)
        
        return saved_alerts
    
    def execute_for_event(self, event: SecurityEvent, time_window_seconds: int = 300) -> List[Alert]:
        """
        Correlaciona um evento específico com eventos relacionados
        
        Args:
            event: Evento de referência
            time_window_seconds: Janela de tempo para buscar eventos relacionados
            
        Returns:
            Lista de alertas correlacionados
        """
        # Salvar evento
        saved_event = self.event_repository.save(event)
        
        # Buscar eventos relacionados
        related_events = self.event_correlator.find_related_events(
            saved_event,
            time_window_seconds
        )
        
        # Se não houver eventos relacionados, não gerar alerta
        if not related_events:
            return []
        
        # Criar lista com evento principal + relacionados
        all_events = [saved_event] + related_events
        
        # Correlacionar
        return self.execute(all_events)

