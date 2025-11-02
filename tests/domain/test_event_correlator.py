"""
Testes para EventCorrelator (TDD)
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock
from src.domain.entities.event import SecurityEvent, EventType
from src.domain.entities.alert import Alert, AlertCategory, AlertSeverity
from src.infrastructure.services.event_correlator import SimpleEventCorrelator
from src.infrastructure.repositories.in_memory_event_repository import InMemoryEventRepository


class TestEventCorrelator:
    """Testes para correlação de eventos"""
    
    @pytest.fixture
    def event_repository(self):
        """Repositório de eventos para testes"""
        return InMemoryEventRepository()
    
    @pytest.fixture
    def correlator(self, event_repository):
        """Cria instância do correlator"""
        return SimpleEventCorrelator(event_repository)
    
    @pytest.fixture
    def sample_events(self):
        """Cria eventos de exemplo para correlação"""
        base_time = datetime.utcnow()
        
        # Evento 1: Alerta de phishing
        event1 = SecurityEvent(
            id="event-1",
            event_type=EventType.ALERT,
            timestamp=base_time,
            source="Suricata",
            data={
                "src_ip": "192.168.1.100",
                "dest_ip": "10.0.0.1",
                "signature": "ET PHISHING Test",
            }
        )
        
        # Evento 2: DNS lookup relacionado (mesmo IP origem)
        event2 = SecurityEvent(
            id="event-2",
            event_type=EventType.DNS,
            timestamp=base_time + timedelta(seconds=5),
            source="Suricata",
            data={
                "src_ip": "192.168.1.100",
                "query": "suspicious-domain.com",
            }
        )
        
        # Evento 3: HTTP request relacionado (mesmo IP, domínio suspeito)
        event3 = SecurityEvent(
            id="event-3",
            event_type=EventType.HTTP,
            timestamp=base_time + timedelta(seconds=10),
            source="Suricata",
            data={
                "src_ip": "192.168.1.100",
                "host": "suspicious-domain.com",
                "url": "/phishing-page",
            }
        )
        
        return [event1, event2, event3]
    
    def test_correlate_events_by_ip(self, correlator, sample_events):
        """Testa correlação de eventos por IP"""
        # Salvar eventos no repositório
        for event in sample_events:
            correlator.event_repository.save(event)
        
        # Correlacionar eventos
        alerts = correlator.correlate_events(sample_events)
        
        # Deve gerar pelo menos um alerta correlacionado
        assert len(alerts) > 0
        assert all(a.correlated for a in alerts)
        
        # Verificar que eventos relacionados estão nos metadados
        first_alert = alerts[0]
        assert "correlated_events" in first_alert.metadata
        assert len(first_alert.metadata["correlated_events"]) >= 2
    
    def test_find_related_events_time_window(self, correlator, sample_events):
        """Testa busca de eventos relacionados em janela de tempo"""
        # Salvar eventos no repositório
        for event in sample_events:
            correlator.event_repository.save(event)
        
        # Evento de referência
        reference_event = sample_events[0]
        time_window = 300  # 5 minutos
        
        # Buscar eventos relacionados
        related = correlator.find_related_events(reference_event, time_window)
        
        # Deve encontrar pelo menos um evento relacionado (mesmo IP)
        assert len(related) >= 1
    
    def test_correlate_phishing_campaign(self, correlator, sample_events):
        """Testa correlação de campanha de phishing"""
        # Salvar eventos no repositório
        for event in sample_events:
            correlator.event_repository.save(event)
        
        alerts = correlator.correlate_events(sample_events)
        
        # Deve gerar alerta de phishing
        assert len(alerts) > 0
        phishing_alerts = [a for a in alerts if a.category == AlertCategory.PHISHING]
        assert len(phishing_alerts) > 0
    
    def test_correlate_malware_download(self, correlator):
        """Testa correlação de download de malware"""
        base_time = datetime.utcnow()
        
        events = [
            # HTTP download
            SecurityEvent(
                id="e1",
                event_type=EventType.HTTP,
                timestamp=base_time,
                source="Suricata",
                data={
                    "src_ip": "192.168.1.100",
                    "host": "malicious-site.com",
                    "url": "/malware.exe",
                }
            ),
            # File extract
            SecurityEvent(
                id="e2",
                event_type=EventType.FILE_EXTRACT,
                timestamp=base_time + timedelta(seconds=2),
                source="Suricata",
                data={
                    "src_ip": "192.168.1.100",
                    "filename": "malware.exe",
                    "file_hash": "abc123",
                }
            ),
            # File scan (infectado)
            SecurityEvent(
                id="e3",
                event_type=EventType.FILE_SCAN,
                timestamp=base_time + timedelta(seconds=5),
                source="ClamAV",
                data={
                    "file_hash": "abc123",
                    "infected": True,
                    "threat_name": "Trojan.Generic",
                }
            ),
        ]
        
        # Salvar eventos
        for event in events:
            correlator.event_repository.save(event)
        
        alerts = correlator.correlate_events(events)
        
        # Deve gerar alerta de malware correlacionado
        assert len(alerts) > 0
        malware_alerts = [a for a in alerts if a.category == AlertCategory.MALWARE]
        assert len(malware_alerts) > 0

