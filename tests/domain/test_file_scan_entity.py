"""
Testes unitários para entidade FileScanResult
"""
import pytest
from datetime import datetime
from src.domain.entities.file_scan import FileScanResult, ScanStatus


class TestFileScanResult:
    """Testes para entidade FileScanResult"""
    
    def test_create_file_scan_result(self):
        """Testa criação de resultado de escaneamento"""
        scan_result = FileScanResult(
            id="scan-123",
            filepath="/tmp/test.exe",
            filename="test.exe",
            file_hash="abc123",
            file_size=1024,
            status=ScanStatus.CLEAN,
            scan_time=datetime.utcnow(),
            scanner="ClamAV",
        )
        
        assert scan_result.id == "scan-123"
        assert scan_result.filepath == "/tmp/test.exe"
        assert scan_result.filename == "test.exe"
        assert scan_result.file_hash == "abc123"
        assert scan_result.file_size == 1024
        assert scan_result.status == ScanStatus.CLEAN
        assert scan_result.scanner == "ClamAV"
        assert not scan_result.quarantined
    
    def test_file_scan_result_is_infected(self):
        """Testa detecção de arquivo infectado"""
        infected_scan = FileScanResult(
            id="scan-infected",
            filepath="/tmp/malware.exe",
            filename="malware.exe",
            file_hash="infected123",
            file_size=2048,
            status=ScanStatus.INFECTED,
            scan_time=datetime.utcnow(),
            scanner="ClamAV",
            threat_name="Trojan.Generic.123",
        )
        
        assert infected_scan.is_infected() is True
        assert infected_scan.should_quarantine() is True
    
    def test_file_scan_result_should_quarantine(self):
        """Testa lógica de quarentena"""
        # Arquivo infectado deve ser colocado em quarentena
        infected = FileScanResult(
            id="scan-1",
            filepath="/tmp/infected.exe",
            filename="infected.exe",
            file_hash="hash1",
            file_size=1024,
            status=ScanStatus.INFECTED,
            scan_time=datetime.utcnow(),
            scanner="ClamAV",
        )
        assert infected.should_quarantine() is True
        
        # Arquivo suspeito deve ser colocado em quarentena
        suspicious = FileScanResult(
            id="scan-2",
            filepath="/tmp/suspicious.exe",
            filename="suspicious.exe",
            file_hash="hash2",
            file_size=1024,
            status=ScanStatus.SUSPICIOUS,
            scan_time=datetime.utcnow(),
            scanner="ClamAV",
        )
        assert suspicious.should_quarantine() is True
        
        # Arquivo limpo não deve ser colocado em quarentena
        clean = FileScanResult(
            id="scan-3",
            filepath="/tmp/clean.exe",
            filename="clean.exe",
            file_hash="hash3",
            file_size=1024,
            status=ScanStatus.CLEAN,
            scan_time=datetime.utcnow(),
            scanner="ClamAV",
        )
        assert clean.should_quarantine() is False
    
    def test_file_scan_result_to_dict(self):
        """Testa conversão para dicionário"""
        scan_result = FileScanResult(
            id="scan-dict",
            filepath="/tmp/test.exe",
            filename="test.exe",
            file_hash="abc123",
            file_size=1024,
            status=ScanStatus.INFECTED,
            scan_time=datetime(2025, 1, 15, 10, 30, 0),
            scanner="ClamAV",
            threat_name="Trojan.Test",
            quarantined=True,
            quarantine_path="/quarantine/test.exe",
        )
        
        result = scan_result.to_dict()
        
        assert result["id"] == "scan-dict"
        assert result["filepath"] == "/tmp/test.exe"
        assert result["filename"] == "test.exe"
        assert result["status"] == "infected"
        assert result["threat_name"] == "Trojan.Test"
        assert result["quarantined"] is True
        assert result["quarantine_path"] == "/quarantine/test.exe"
        assert "scan_time" in result

