"""
Testes de Integração - Fluxo completo de correlação de eventos
"""
import pytest
from datetime import datetime, timedelta

from src.domain.entities.event import SecurityEvent, EventType
from src.infrastructure.services.event_correlator import SimpleEventCorrelator
from src.infrastructure.repositories.in_memory_event_repository import InMemoryEventRepository
from src.infrastructure.repositories.in_memory_alert_repository import InMemoryAlertRepository
from src.application.use_cases.correlate_events_use_case import CorrelateEventsUseCase


class TestEventCorrelationIntegration:
    """Testes de integração para correlação de eventos"""
    
    @pytest.fixture
    def event_repo(self):
        """Repositório de eventos"""
        return InMemoryEventRepository()
    
    @pytest.fixture
    def alert_repo(self):
        """Repositório de alertas"""
        return InMemoryAlertRepository()
    
    @pytest.fixture
    def correlator(self, event_repo):
        """Correlator"""
        return SimpleEventCorrelator(event_repo)
    
    @pytest.fixture
    def use_case(self, correlator, event_repo, alert_repo):
        """Caso de uso de correlação"""
        return CorrelateEventsUseCase(
            event_correlator=correlator,
            event_repository=event_repo,
            alert_repository=alert_repo,
        )
    
    @pytest.mark.integration
    def test_correlate_phishing_campaign(self, use_case, alert_repo):
        """
        Testa fluxo completo: múltiplos eventos -> correlação -> alertas
        """
        base_time = datetime.utcnow()
        
        events = [
            SecurityEvent(
                id="e1",
                event_type=EventType.DNS,
                timestamp=base_time,
                source="Suricata",
                data={
                    "src_ip": "192.168.1.100",
                    "query": "phishing-site.com",
                }
            ),
            SecurityEvent(
                id="e2",
                event_type=EventType.HTTP,
                timestamp=base_time + timedelta(seconds=5),
                source="Suricata",
                data={
                    "src_ip": "192.168.1.100",
                    "host": "phishing-site.com",
                    "url": "/phish",
                }
            ),
            SecurityEvent(
                id="e3",
                event_type=EventType.ALERT,
                timestamp=base_time + timedelta(seconds=10),
                source="Suricata",
                data={
                    "src_ip": "192.168.1.100",
                    "signature": "ET PHISHING Test",
                }
            ),
        ]
        
        # Executar correlação
        alerts = use_case.execute(events)
        
        # Verificar resultados
        assert len(alerts) > 0
        
        # Verificar que alertas foram salvos
        for alert in alerts:
            found = alert_repo.find_by_id(alert.id)
            assert found is not None
            assert found.correlated is True
    
    @pytest.mark.integration
    def test_correlate_single_event_with_history(self, use_case, event_repo, alert_repo):
        """
        Testa correlação de evento único com histórico
        """
        base_time = datetime.utcnow()
        
        # Criar evento histórico
        historical_event = SecurityEvent(
            id="hist-1",
            event_type=EventType.DNS,
            timestamp=base_time - timedelta(minutes=2),
            source="Suricata",
            data={
                "src_ip": "192.168.1.100",
                "query": "suspicious.com",
            }
        )
        event_repo.save(historical_event)
        
        # Novo evento
        new_event = SecurityEvent(
            id="new-1",
            event_type=EventType.HTTP,
            timestamp=base_time,
            source="Suricata",
            data={
                "src_ip": "192.168.1.100",
                "host": "suspicious.com",
            }
        )
        
        # Correlacionar
        alerts = use_case.execute_for_event(new_event, time_window_seconds=300)
        
        # Deve encontrar evento histórico e correlacionar
        assert len(alerts) > 0

