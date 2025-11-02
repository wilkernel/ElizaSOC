"""
Configuração global de testes - Fixtures compartilhadas
"""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock


@pytest.fixture
def temp_dir():
    """Cria um diretório temporário para testes"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_alert_data():
    """Dados de exemplo de alerta do Suricata"""
    return {
        "event_type": "alert",
        "timestamp": "2025-01-15T10:30:00.123456+0000",
        "src_ip": "192.168.1.100",
        "dest_ip": "8.8.8.8",
        "src_port": 54321,
        "dest_port": 80,
        "proto": "TCP",
        "alert": {
            "action": "allowed",
            "gid": 1,
            "signature_id": 2019065,
            "rev": 2,
            "signature": "ET MALWARE Suspicious Domain in DNS Lookup",
            "category": "Potential Corporate Privacy Violation",
            "severity": 2
        }
    }


@pytest.fixture
def sample_file_scan_result():
    """Resultado de exemplo de escaneamento de arquivo"""
    return {
        "filepath": "/tmp/suspicious.exe",
        "filename": "suspicious.exe",
        "infected": True,
        "virus_name": "Trojan.Generic.1234567",
        "file_size": 1024,
        "file_hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6",
        "scan_time": "2025-01-15T10:30:00.123456+0000",
        "scanner": "ClamAV",
        "quarantined": False
    }


@pytest.fixture
def mock_file_system(tmp_path):
    """Mock do sistema de arquivos para testes"""
    class MockFileSystem:
        def __init__(self, base_path):
            self.base_path = Path(base_path)
            self.base_path.mkdir(parents=True, exist_ok=True)
        
        def create_file(self, filename, content=b""):
            file_path = self.base_path / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_bytes(content)
            return str(file_path)
        
        def file_exists(self, filename):
            return (self.base_path / filename).exists()
        
        def read_file(self, filename):
            return (self.base_path / filename).read_bytes()
    
    return MockFileSystem(tmp_path)


@pytest.fixture
def mock_clamav_scanner():
    """Mock do scanner ClamAV para testes"""
    scanner = Mock()
    scanner.scan_file = Mock(return_value={
        "infected": False,
        "virus_name": None,
        "scan_time": "2025-01-15T10:30:00.123456+0000"
    })
    return scanner

