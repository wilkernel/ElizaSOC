"""
Testes de implementação do EventCorrelator
"""
import pytest
from datetime import datetime, timedelta
from src.domain.entities.event import SecurityEvent, EventType
from src.infrastructure.services.event_correlator import SimpleEventCorrelator
from src.infrastructure.repositories.in_memory_event_repository import InMemoryEventRepository


class TestSimpleEventCorrelator:
    """Testes para implementação SimpleEventCorrelator"""
    
    @pytest.fixture
    def correlator(self):
        """Cria instância do correlator"""
        repo = InMemoryEventRepository()
        return SimpleEventCorrelator(repo)
    
    def test_correlate_empty_list(self, correlator):
        """Testa correlação de lista vazia"""
        alerts = correlator.correlate_events([])
        assert alerts == []
    
    def test_correlate_single_event(self, correlator):
        """Testa correlação de um único evento"""
        event = SecurityEvent(
            id="single",
            event_type=EventType.ALERT,
            timestamp=datetime.utcnow(),
            source="Suricata",
            data={"src_ip": "192.168.1.1"},
        )
        
        alerts = correlator.correlate_events([event])
        # Um único evento não deve gerar alerta correlacionado
        assert len(alerts) == 0
    
    def test_correlate_unrelated_events(self, correlator):
        """Testa eventos não relacionados"""
        base_time = datetime.utcnow()
        
        events = [
            SecurityEvent(
                id="e1",
                event_type=EventType.ALERT,
                timestamp=base_time,
                source="Suricata",
                data={"src_ip": "192.168.1.1"},
            ),
            SecurityEvent(
                id="e2",
                event_type=EventType.ALERT,
                timestamp=base_time + timedelta(hours=2),  # Muito tempo depois
                source="Suricata",
                data={"src_ip": "10.0.0.1"},  # IP diferente
            ),
        ]
        
        alerts = correlator.correlate_events(events)
        # Eventos não relacionados não devem gerar alertas correlacionados
        assert len(alerts) == 0
    
    def test_correlate_same_domain(self, correlator):
        """Testa correlação por domínio"""
        base_time = datetime.utcnow()
        
        events = [
            SecurityEvent(
                id="dns",
                event_type=EventType.DNS,
                timestamp=base_time,
                source="Suricata",
                data={"query": "suspicious.com"},
            ),
            SecurityEvent(
                id="http",
                event_type=EventType.HTTP,
                timestamp=base_time + timedelta(seconds=10),
                source="Suricata",
                data={"host": "suspicious.com"},
            ),
        ]
        
        for event in events:
            correlator.event_repository.save(event)
        
        alerts = correlator.correlate_events(events)
        assert len(alerts) > 0

