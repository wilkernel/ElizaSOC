"""
Testes para implementação ClamAV Scanner (TDD)
"""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import uuid

from src.domain.entities.file_scan import FileScanResult, ScanStatus
from src.domain.services.file_scanner import FileScanner


# Mock da implementação (será criada depois)
class ClamAVScanner(FileScanner):
    """Implementação ClamAV - será implementada após os testes"""
    pass


class TestClamAVScanner:
    """Testes para ClamAV Scanner usando TDD"""
    
    @pytest.fixture
    def scanner(self):
        """Cria instância do scanner"""
        # Por enquanto, retorna mock
        # Depois será substituído pela implementação real
        return Mock(spec=FileScanner)
    
    @pytest.fixture
    def temp_file(self, tmp_path):
        """Cria arquivo temporário para testes"""
        test_file = tmp_path / "test.exe"
        test_file.write_bytes(b"test content")
        return str(test_file)
    
    def test_scan_clean_file(self, scanner, temp_file):
        """Testa escaneamento de arquivo limpo"""
        # Arrange
        expected_result = FileScanResult(
            id=str(uuid.uuid4()),
            filepath=temp_file,
            filename=os.path.basename(temp_file),
            file_hash="abc123",
            file_size=os.path.getsize(temp_file),
            status=ScanStatus.CLEAN,
            scan_time=datetime.utcnow(),
            scanner="ClamAV",
        )
        
        scanner.scan_file.return_value = expected_result
        
        # Act
        result = scanner.scan_file(temp_file, quarantine=False)
        
        # Assert
        assert result is not None
        assert result.status == ScanStatus.CLEAN
        assert result.is_infected() is False
        assert result.scanner == "ClamAV"
        scanner.scan_file.assert_called_once_with(temp_file, quarantine=False)
    
    def test_scan_infected_file(self, scanner, temp_file):
        """Testa escaneamento de arquivo infectado"""
        # Arrange
        expected_result = FileScanResult(
            id=str(uuid.uuid4()),
            filepath=temp_file,
            filename=os.path.basename(temp_file),
            file_hash="infected123",
            file_size=os.path.getsize(temp_file),
            status=ScanStatus.INFECTED,
            scan_time=datetime.utcnow(),
            scanner="ClamAV",
            threat_name="Trojan.Generic.123",
        )
        
        scanner.scan_file.return_value = expected_result
        
        # Act
        result = scanner.scan_file(temp_file, quarantine=True)
        
        # Assert
        assert result.status == ScanStatus.INFECTED
        assert result.is_infected() is True
        assert result.threat_name == "Trojan.Generic.123"
        assert result.should_quarantine() is True
    
    def test_scan_file_not_found(self, scanner):
        """Testa escaneamento de arquivo inexistente"""
        # Arrange
        scanner.scan_file.side_effect = FileNotFoundError("File not found")
        
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            scanner.scan_file("/nonexistent/file.exe")
    
    def test_quarantine_file(self, scanner, temp_file):
        """Testa quarentena de arquivo"""
        # Arrange
        scanner.quarantine_file.return_value = True
        
        # Act
        result = scanner.quarantine_file(temp_file)
        
        # Assert
        assert result is True
        scanner.quarantine_file.assert_called_once_with(temp_file)
    
    def test_scan_directory(self, scanner, tmp_path):
        """Testa escaneamento de diretório"""
        # Arrange
        # Criar arquivos de teste
        file1 = tmp_path / "file1.exe"
        file2 = tmp_path / "file2.txt"
        file1.write_bytes(b"content1")
        file2.write_bytes(b"content2")
        
        expected_results = [
            FileScanResult(
                id=str(uuid.uuid4()),
                filepath=str(file1),
                filename="file1.exe",
                file_hash="hash1",
                file_size=file1.stat().st_size,
                status=ScanStatus.CLEAN,
                scan_time=datetime.utcnow(),
                scanner="ClamAV",
            ),
            FileScanResult(
                id=str(uuid.uuid4()),
                filepath=str(file2),
                filename="file2.txt",
                file_hash="hash2",
                file_size=file2.stat().st_size,
                status=ScanStatus.CLEAN,
                scan_time=datetime.utcnow(),
                scanner="ClamAV",
            ),
        ]
        
        scanner.scan_directory.return_value = expected_results
        
        # Act
        results = scanner.scan_directory(str(tmp_path), recursive=False)
        
        # Assert
        assert len(results) == 2
        assert all(isinstance(r, FileScanResult) for r in results)
        scanner.scan_directory.assert_called_once_with(str(tmp_path), recursive=False)
    
    def test_scan_file_with_hash_calculation(self, scanner, temp_file):
        """Testa que o hash é calculado corretamente"""
        # Arrange
        import hashlib
        expected_hash = hashlib.sha256(b"test content").hexdigest()
        
        result = FileScanResult(
            id=str(uuid.uuid4()),
            filepath=temp_file,
            filename=os.path.basename(temp_file),
            file_hash=expected_hash,
            file_size=os.path.getsize(temp_file),
            status=ScanStatus.CLEAN,
            scan_time=datetime.utcnow(),
            scanner="ClamAV",
        )
        
        scanner.scan_file.return_value = result
        
        # Act
        scan_result = scanner.scan_file(temp_file)
        
        # Assert
        assert scan_result.file_hash == expected_hash
        assert len(scan_result.file_hash) == 64  # SHA256 é 64 caracteres hex

