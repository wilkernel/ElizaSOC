"""
Testes unitários para entidade Alert
"""
import pytest
from datetime import datetime
from src.domain.entities.alert import Alert, AlertSeverity, AlertCategory


class TestAlert:
    """Testes para entidade Alert"""
    
    def test_create_alert(self):
        """Testa criação de alerta"""
        alert = Alert(
            id="test-123",
            timestamp=datetime.utcnow(),
            signature="ET MALWARE Test",
            category=AlertCategory.MALWARE,
            severity=AlertSeverity.HIGH,
            src_ip="192.168.1.100",
            dest_ip="8.8.8.8",
        )
        
        assert alert.id == "test-123"
        assert alert.signature == "ET MALWARE Test"
        assert alert.category == AlertCategory.MALWARE
        assert alert.severity == AlertSeverity.HIGH
        assert alert.src_ip == "192.168.1.100"
        assert alert.dest_ip == "8.8.8.8"
        assert not alert.correlated
        assert not alert.processed
    
    def test_alert_is_phishing(self):
        """Testa detecção de alerta de phishing"""
        alert = Alert(
            id="test-1",
            timestamp=datetime.utcnow(),
            signature="ET PHISHING Test",
            category=AlertCategory.PHISHING,
            severity=AlertSeverity.MEDIUM,
        )
        
        assert alert.is_phishing() is True
        assert alert.is_malware() is False
    
    def test_alert_is_malware(self):
        """Testa detecção de alertas de malware"""
        malware_types = [
            AlertCategory.MALWARE,
            AlertCategory.VIRUS,
            AlertCategory.TROJAN,
            AlertCategory.RANSOMWARE,
        ]
        
        for category in malware_types:
            alert = Alert(
                id=f"test-{category.value}",
                timestamp=datetime.utcnow(),
                signature=f"ET {category.value.upper()} Test",
                category=category,
                severity=AlertSeverity.HIGH,
            )
            assert alert.is_malware() is True
    
    def test_alert_is_critical(self):
        """Testa detecção de alerta crítico"""
        alert = Alert(
            id="test-critical",
            timestamp=datetime.utcnow(),
            signature="ET CRITICAL Test",
            category=AlertCategory.MALWARE,
            severity=AlertSeverity.CRITICAL,
        )
        
        assert alert.is_critical() is True
    
    def test_alert_to_dict(self):
        """Testa conversão de alerta para dicionário"""
        alert = Alert(
            id="test-dict",
            timestamp=datetime(2025, 1, 15, 10, 30, 0),
            signature="ET Test",
            category=AlertCategory.MALWARE,
            severity=AlertSeverity.HIGH,
            src_ip="192.168.1.100",
            dest_ip="8.8.8.8",
        )
        
        result = alert.to_dict()
        
        assert result["id"] == "test-dict"
        assert result["signature"] == "ET Test"
        assert result["category"] == "malware"
        assert result["severity"] == 3
        assert result["src_ip"] == "192.168.1.100"
        assert result["dest_ip"] == "8.8.8.8"
        assert "timestamp" in result
    
    def test_alert_mask_private_ip(self):
        """Testa ofuscação de IPs privados"""
        alert = Alert(
            id="test-mask",
            timestamp=datetime.utcnow(),
            signature="ET Test",
            category=AlertCategory.MALWARE,
            severity=AlertSeverity.HIGH,
            metadata={"src_ip": "192.168.1.100", "dest_ip": "10.0.0.1"},
        )
        
        masked = alert.mark_private_ips()
        
        assert masked["src_ip"] == "*.100"
        assert masked["dest_ip"] == "*.1"
    
    def test_alert_public_ip_not_masked(self):
        """Testa que IPs públicos não são ofuscados"""
        alert = Alert(
            id="test-public",
            timestamp=datetime.utcnow(),
            signature="ET Test",
            category=AlertCategory.MALWARE,
            severity=AlertSeverity.HIGH,
            metadata={"src_ip": "8.8.8.8", "dest_ip": "1.1.1.1"},
        )
        
        masked = alert.mark_private_ips()
        
        assert masked["src_ip"] == "8.8.8.8"
        assert masked["dest_ip"] == "1.1.1.1"

