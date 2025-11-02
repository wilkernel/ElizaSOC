"""
Testes para ThreatIntelligenceService (TDD)
"""
import pytest
from datetime import datetime
from src.domain.entities.threat_intelligence import IOC, IOCType, IOCSource
from src.infrastructure.services.threat_intelligence_service import SimpleThreatIntelligenceService
from src.infrastructure.repositories.in_memory_ioc_repository import InMemoryIOCRepository


class TestThreatIntelligenceService:
    """Testes para serviço de Threat Intelligence"""
    
    @pytest.fixture
    def ioc_repository(self):
        """Repositório de IOCs para testes"""
        return InMemoryIOCRepository()
    
    @pytest.fixture
    def threat_intel_service(self, ioc_repository):
        """Cria instância do serviço"""
        return SimpleThreatIntelligenceService(ioc_repository)
    
    @pytest.fixture
    def sample_iocs(self, ioc_repository):
        """Cria IOCs de exemplo"""
        now = datetime.utcnow()
        
        iocs = [
            IOC(
                id="ioc-1",
                ioc_type=IOCType.IP,
                value="192.0.2.1",
                source=IOCSource.ABUSE_CH,
                threat_type="malware",
                confidence=90,
                first_seen=now,
                last_seen=now,
            ),
            IOC(
                id="ioc-2",
                ioc_type=IOCType.DOMAIN,
                value="malicious-site.com",
                source=IOCSource.ALIENVAULT_OTX,
                threat_type="phishing",
                confidence=85,
                first_seen=now,
                last_seen=now,
            ),
            IOC(
                id="ioc-3",
                ioc_type=IOCType.HASH,
                value="abc123def456",
                source=IOCSource.VIRUSTOTAL,
                threat_type="trojan",
                confidence=95,
                first_seen=now,
                last_seen=now,
            ),
        ]
        
        for ioc in iocs:
            ioc_repository.save(ioc)
        
        return iocs
    
    def test_check_ip_found(self, threat_intel_service, sample_iocs):
        """Testa verificação de IP conhecido como malicioso"""
        result = threat_intel_service.check_ip("192.0.2.1")
        
        assert result is not None
        assert result.value == "192.0.2.1"
        assert result.ioc_type == IOCType.IP
        assert result.is_high_confidence()
    
    def test_check_ip_not_found(self, threat_intel_service):
        """Testa verificação de IP não conhecido"""
        result = threat_intel_service.check_ip("8.8.8.8")
        assert result is None
    
    def test_check_domain_found(self, threat_intel_service, sample_iocs):
        """Testa verificação de domínio conhecido"""
        result = threat_intel_service.check_domain("malicious-site.com")
        
        assert result is not None
        assert result.value == "malicious-site.com"
        assert result.ioc_type == IOCType.DOMAIN
    
    def test_check_domain_not_found(self, threat_intel_service):
        """Testa verificação de domínio não conhecido"""
        result = threat_intel_service.check_domain("google.com")
        assert result is None
    
    def test_check_hash_found(self, threat_intel_service, sample_iocs):
        """Testa verificação de hash conhecido"""
        result = threat_intel_service.check_hash("abc123def456")
        
        assert result is not None
        assert result.value == "abc123def456"
        assert result.ioc_type == IOCType.HASH
    
    def test_check_hash_not_found(self, threat_intel_service):
        """Testa verificação de hash não conhecido"""
        result = threat_intel_service.check_hash("unknownhash123")
        assert result is None
    
    def test_check_url(self, threat_intel_service, sample_iocs):
        """Testa verificação de URL"""
        # Por enquanto, verifica domínio da URL
        result = threat_intel_service.check_url("http://malicious-site.com/path")
        
        assert result is not None
    
    def test_update_feeds(self, threat_intel_service, ioc_repository):
        """Testa atualização de feeds"""
        # Simula atualização de feeds (retorna número de IOCs atualizados)
        count = threat_intel_service.update_feeds()
        
        # Deve retornar número >= 0
        assert count >= 0

