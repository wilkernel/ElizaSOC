"""
Interface EventRepository - Contrato para repositório de eventos
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from ..entities.event import SecurityEvent, EventType


class EventRepository(ABC):
    """Interface para repositório de eventos de segurança"""
    
    @abstractmethod
    def save(self, event: SecurityEvent) -> SecurityEvent:
        """Salva um evento"""
        pass
    
    @abstractmethod
    def find_by_id(self, event_id: str) -> Optional[SecurityEvent]:
        """Busca evento por ID"""
        pass
    
    @abstractmethod
    def find_all(
        self,
        limit: int = 100,
        offset: int = 0,
        event_type: Optional[EventType] = None,
        source: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[SecurityEvent]:
        """Busca eventos com filtros"""
        pass
    
    @abstractmethod
    def find_related_events(self, event_id: str) -> List[SecurityEvent]:
        """Busca eventos relacionados"""
        pass

