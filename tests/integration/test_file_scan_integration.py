"""
Testes de Integração - Fluxo completo de escaneamento de arquivo
"""
import pytest
import tempfile
import os
from pathlib import Path

from src.infrastructure.scanners.clamav_scanner import ClamAVScanner
from src.infrastructure.repositories.in_memory_file_scan_repository import InMemoryFileScanRepository
from src.application.use_cases.scan_file_use_case import ScanFileUseCase


class TestFileScanIntegration:
    """Testes de integração para fluxo completo de escaneamento"""
    
    @pytest.fixture
    def temp_file(self, tmp_path):
        """Cria arquivo temporário para testes"""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content for scanning")
        return str(test_file)
    
    @pytest.fixture
    def scanner(self, tmp_path):
        """Cria scanner com diretório de quarentena temporário"""
        quarantine_dir = str(tmp_path / "quarantine")
        return ClamAVScanner(quarantine_dir=quarantine_dir)
    
    @pytest.fixture
    def repository(self):
        """Cria repositório in-memory"""
        return InMemoryFileScanRepository()
    
    @pytest.fixture
    def use_case(self, scanner, repository):
        """Cria caso de uso completo"""
        return ScanFileUseCase(
            file_scanner=scanner,
            file_scan_repository=repository,
        )
    
    @pytest.mark.integration
    def test_scan_file_flow(self, use_case, temp_file):
        """
        Testa fluxo completo: escanear -> salvar -> buscar
        """
        # 1. Escanear arquivo
        result = use_case.execute(temp_file, quarantine=False)
        
        # 2. Verificar resultado
        assert result is not None
        assert result.filepath == temp_file
        assert result.scanner == "ClamAV"
        assert result.file_hash is not None
        assert len(result.file_hash) == 64  # SHA256
        
        # 3. Buscar no repositório
        found = use_case.file_scan_repository.find_by_id(result.id)
        assert found is not None
        assert found.id == result.id
        assert found.filepath == temp_file
    
    @pytest.mark.integration
    def test_scan_and_quarantine_flow(self, use_case, temp_file):
        """
        Testa fluxo: escanear arquivo infectado -> quarentena
        Nota: Este teste requer um arquivo realmente infectado ou mock
        """
        # Por enquanto, apenas testa estrutura
        result = use_case.execute(temp_file, quarantine=True)
        assert result is not None
    
    @pytest.mark.integration
    def test_scan_directory_flow(self, use_case, tmp_path):
        """
        Testa fluxo: escanear diretório -> múltiplos resultados
        """
        # Criar múltiplos arquivos
        for i in range(3):
            test_file = tmp_path / f"test_{i}.txt"
            test_file.write_text(f"Content {i}")
        
        # Escanear diretório
        results = use_case.execute_directory(str(tmp_path), recursive=False)
        
        # Verificar resultados
        assert len(results) == 3
        assert all(r.scanner == "ClamAV" for r in results)
        
        # Verificar que todos foram salvos
        for result in results:
            found = use_case.file_scan_repository.find_by_id(result.id)
            assert found is not None

