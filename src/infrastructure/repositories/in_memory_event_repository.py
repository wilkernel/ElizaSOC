"""
Implementação In-Memory do EventRepository
Para uso em testes e desenvolvimento
"""
from typing import List, Optional
from datetime import datetime

from src.domain.repositories.event_repository import EventRepository
from src.domain.entities.event import SecurityEvent, EventType


class InMemoryEventRepository(EventRepository):
    """Implementação in-memory do repositório de eventos"""
    
    def __init__(self):
        """Inicializa repositório vazio"""
        self._events: dict[str, SecurityEvent] = {}
    
    def save(self, event: SecurityEvent) -> SecurityEvent:
        """Salva um evento"""
        self._events[event.id] = event
        return event
    
    def find_by_id(self, event_id: str) -> Optional[SecurityEvent]:
        """Busca evento por ID"""
        return self._events.get(event_id)
    
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
        results = list(self._events.values())
        
        # Aplicar filtros
        if event_type:
            results = [r for r in results if r.event_type == event_type]
        
        if source:
            results = [r for r in results if r.source == source]
        
        if start_date:
            results = [r for r in results if r.timestamp >= start_date]
        
        if end_date:
            results = [r for r in results if r.timestamp <= end_date]
        
        # Ordenar por timestamp (mais recentes primeiro)
        results.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Aplicar paginação
        return results[offset:offset + limit]
    
    def find_related_events(self, event_id: str) -> List[SecurityEvent]:
        """Busca eventos relacionados"""
        event = self.find_by_id(event_id)
        if not event:
            return []
        
        related = []
        for related_id in event.related_events:
            related_event = self.find_by_id(related_id)
            if related_event:
                related.append(related_event)
        
        return related
    
    def clear(self) -> None:
        """Limpa todos os eventos (útil para testes)"""
        self._events.clear()

