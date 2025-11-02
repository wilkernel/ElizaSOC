"""
Interface EventCorrelator - Contrato para serviço de correlação de eventos
"""
from abc import ABC, abstractmethod
from typing import List

from ..entities.event import SecurityEvent
from ..entities.alert import Alert


class EventCorrelator(ABC):
    """Interface para serviço de correlação de eventos"""
    
    @abstractmethod
    def correlate_events(self, events: List[SecurityEvent]) -> List[Alert]:
        """
        Correlaciona eventos relacionados e gera alertas
        
        Args:
            events: Lista de eventos a correlacionar
            
        Returns:
            Lista de alertas correlacionados
        """
        pass
    
    @abstractmethod
    def find_related_events(self, event: SecurityEvent, time_window_seconds: int = 300) -> List[SecurityEvent]:
        """
        Encontra eventos relacionados dentro de uma janela de tempo
        
        Args:
            event: Evento de referência
            time_window_seconds: Janela de tempo em segundos
            
        Returns:
            Lista de eventos relacionados
        """
        pass

