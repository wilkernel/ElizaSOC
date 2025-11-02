"""
Testes para ResponseAutomation (TDD)
"""
import pytest
from datetime import datetime
from src.domain.entities.alert import Alert, AlertCategory, AlertSeverity
from src.domain.entities.file_scan import FileScanResult, ScanStatus
from src.infrastructure.services.response_automation import SimpleResponseAutomation


class TestResponseAutomation:
    """Testes para resposta automatizada"""
    
    @pytest.fixture
    def response_automation(self):
        """Cria instância do serviço de resposta"""
        return SimpleResponseAutomation()
    
    @pytest.fixture
    def critical_alert(self):
        """Alerta crítico de exemplo"""
        return Alert(
            id="alert-1",
            timestamp=datetime.utcnow(),
            signature="CRITICAL MALWARE DETECTED",
            category=AlertCategory.MALWARE,
            severity=AlertSeverity.CRITICAL,
            src_ip="192.0.2.1",
            dest_ip="192.168.1.100",
        )
    
    @pytest.fixture
    def infected_file(self):
        """Arquivo infectado de exemplo"""
        return FileScanResult(
            id="scan-1",
            filepath="/tmp/malware.exe",
            filename="malware.exe",
            file_hash="abc123",
            file_size=1024,
            status=ScanStatus.INFECTED,
            scan_time=datetime.utcnow(),
            scanner="ClamAV",
            threat_name="Trojan.Generic",
        )
    
    def test_handle_alert(self, response_automation, critical_alert):
        """Testa processamento de alerta"""
        result = response_automation.handle_alert(critical_alert)
        
        assert isinstance(result, dict)
        assert "actions_taken" in result or "actions" in result or "status" in result
        assert "alert_id" in result
    
    def test_block_ip(self, response_automation):
        """Testa bloqueio de IP"""
        # Por enquanto, apenas verificar que método existe
        # Em produção, bloquearia via iptables/firewall
        result = response_automation.block_ip("192.0.2.1", "Test reason")
        assert isinstance(result, bool)
    
    def test_block_domain(self, response_automation):
        """Testa bloqueio de domínio"""
        result = response_automation.block_domain("malicious.com", "Test reason")
        assert isinstance(result, bool)
    
    def test_quarantine_file_result(self, response_automation, infected_file):
        """Testa quarentena de arquivo"""
        result = response_automation.quarantine_file_result(infected_file)
        assert isinstance(result, bool)
    
    def test_isolate_endpoint(self, response_automation):
        """Testa isolamento de endpoint"""
        result = response_automation.isolate_endpoint("endpoint-1", "Test reason")
        assert isinstance(result, bool)

